# -*- coding: utf-8 -*-
# @Time    : 2020/8/27 15:34
# @Author  : hyy
# @Email   : hyywestwood@zju.edu.cn
# @File    : question_1.py
# @Software: PyCharm
import pandas as pd
import numpy as np
import datetime
import matplotlib.pyplot as plt
from water_type import *


class Pond_A():
    def __init__(self, max_volume=360000, pump_rate=0.6):
        self.max_volume = max_volume  #m3
        self.pump = pump(pump_rate)   # m3/s
        self.water = []
        # self.water.append(water_type_original(self.max_volume))
        self.total_volume = 0
        self.irrigation_outflow = 0
        self.water_overflow = 0

    # 每天从水厂排入的水量
    def _water_from_waterplant(self):
        miu = 20000  # m3
        sig = 5000  #m3
        volume = max(sig*np.random.randn() + miu, 0)
        self.total_volume += volume
        return water_type_plant(volume)

    def inflow(self, current_time, df):
        volume = df.loc[current_time]['inFlow_to_Pond A (m3/h)']
        self.total_volume += volume
        return water_type_rain(volume)

    # 灌溉用水，也设置为排出水龄较长的水
    def irrigation_demand(self, current_time, df, residual_water_demand=None):
        # 当前时刻的总需水量=灌溉需水量 + 之前未满足的需水量
        if residual_water_demand is None:
            volume = df.loc[current_time]['irrigation_demand  (m3/h)']
        else:
            volume = df.loc[current_time]['irrigation_demand  (m3/h)'] + residual_water_demand

        self.irrigation_outflow = 0
        # 当前小时内，泵可以正常工作的时间
        runtime_useful = min(self.pump.max_pump_runtime - self.pump.runtime, 1)
        if runtime_useful <= 0:
            # 如果泵工作超时，直接停止取水灌溉
            assert self.pump.runtime == 12
            return volume
        else:
            # 判断 A 总水量能否满足要求
            if self.total_volume > volume or self.total_volume>self.pump.pump_rate*3600:
                # 如果能则慢慢灌溉
                del_list = []
                for item in self.water:
                    if item.volume > volume:
                        # 这部分水体体积比灌溉需求大
                        (runtime_useful, volume_not_satisfied) = self.pump.run(volume, runtime_useful)
                        if volume_not_satisfied is None:
                            item.volume = item.volume - volume
                            self.irrigation_outflow += volume
                        else:
                            item.volume = item.volume - (volume - volume_not_satisfied)
                            self.irrigation_outflow += (volume - volume_not_satisfied)
                            return volume_not_satisfied
                        break
                    elif item.volume == volume:
                        # 刚好相等
                        (runtime_useful, volume_not_satisfied) = self.pump.run(volume, runtime_useful)
                        if volume_not_satisfied is None:
                            item.volume = 0
                            self.irrigation_outflow += volume
                            del_list.append(item)
                            break
                        else:
                            self.irrigation_outflow += item.volume - volume_not_satisfied
                            item.volume = volume_not_satisfied
                            return volume_not_satisfied
                    else:
                        # 小于需求，继续从下一个水体获取
                        (runtime_useful, volume_not_satisfied) = self.pump.run(item.volume, runtime_useful)
                        if volume_not_satisfied is None:
                            self.irrigation_outflow += item.volume
                            volume = volume - item.volume
                            item.volume = 0
                            del_list.append(item)
                        else:
                            self.irrigation_outflow += item.volume - volume_not_satisfied
                            item.volume = volume_not_satisfied
                            return volume_not_satisfied

                # 将已经排空的水体删除
                for item in del_list:
                    self.water.remove(item)

                # 水体总体积更新
                self.total_volume = self.total_volume - self.irrigation_outflow
            else:
                volume = volume - self.total_volume
                self.pump.runtime += self.total_volume/self.pump.pump_rate/3600
                self.total_volume = 0
                self.water = []
                return volume

    # 超量排除，需优先排出水龄较长的水，也需通过水泵？
    def overflow(self):
        if self.total_volume > self.max_volume:
            surplus_water = self.total_volume - self.max_volume
            self.water_overflow = surplus_water
            del_list = []
            for item in self.water:
                if item.volume > surplus_water:
                    # 这部分水体体积比灌溉需求大
                    item.volume = item.volume - surplus_water
                    break
                elif item.volume == surplus_water:
                    # 刚好相等
                    del_list.append(item)
                    break
                else:
                    # 小于需求，继续从下一个水体获取
                    surplus_water = surplus_water - item.volume
                    del_list.append(item)

            # 将已经排出的水体删除
            for item in del_list:
                self.water.remove(item)
            self.total_volume = self.max_volume
        else:
            self.water_overflow = 0

    # 自排序，使得水龄长的水体在前，便于超量排出与灌溉的计算
    def self_sort(self):
        self.water = list(filter(lambda x: x.volume > 0, self.water))
        self.water.sort(key=lambda x: x.age, reverse=True)
        for item in self.water:
            item.age += 1


class Pond_B(Pond_A):
    def __init__(self, max_volume=90000, pump_rate=0.25):
        self.max_volume = max_volume  # m3
        self.pump = pump(pump_rate)  # m3/s
        self.water = []
        self.total_volume = 0
        self.irrigation_outflow = 0
        self.water_overflow = 0

    def inflow(self, current_time, df):
        volume = df.loc[current_time]['inFlow_to_Pond B (m3/h)']
        self.total_volume += volume
        return water_type_rain(volume)


if __name__ == '__main__':
    df = pd.read_csv('Inflow_IrrigationDemand.csv')
    df['Time'] = pd.to_datetime(df['Time'])
    df.set_index("Time", inplace=True)

    A = Pond_A()
    B = Pond_B()

    start_time = datetime.datetime.strptime('2016-1-1 0:00', '%Y-%m-%d %H:%M')
    end_time = start_time + datetime.timedelta(days=731)

    time = start_time
    residual_demand = None
    df_a = pd.DataFrame(columns=['total volume', 'irrigation outflow', 'water_overflow', 'inflow2A', 'pump_runtime'])
    df_b = pd.DataFrame(columns=['total volume', 'irrigation outflow', 'water_overflow', 'inflow2B', 'pump_runtime'])

    while time < end_time:
        # A 调蓄带, 包括污雨水汇入，灌溉用水排出，水厂水源汇入和超量排出四个过程
        A.water.append(A.inflow(time, df))  # A雨污水汇入
        residual_demand = A.irrigation_demand(time, df, residual_demand) # 灌溉用水排出
        # 新的一天开始
        if time.hour == 0:
            A.pump.runtime = 0  # 水泵运行时间清空
            if A.total_volume < A.max_volume:
                A.water.append(A._water_from_waterplant())  # 水厂水源汇入
        A.overflow()
        A.self_sort()

        # B 调蓄带，仅包含污雨水汇入和超量排出两个过程
        B.water.append(B.inflow(time, df))  # A雨污水汇入
        # 新的一天开始
        if time.hour == 0:
            B.pump.runtime = 0  # 水泵运行时间清空
        B.overflow()
        B.self_sort()

        df_a.loc[time] = [A.total_volume, A.irrigation_outflow, A.water_overflow,
                          df.loc[time]['inFlow_to_Pond A (m3/h)'], A.pump.runtime]
        df_b.loc[time] = [B.total_volume, B.irrigation_outflow, B.water_overflow,
                          df.loc[time]['inFlow_to_Pond B (m3/h)'], B.pump.runtime]
        time += datetime.timedelta(hours=1)
        # print('A总体积为：', A.total_volume)

    # from picdraw import pic_question
    # pic1 = pic_question()
    # pic1.pondA(df_a)

    # fig = plt.figure(figsize=(8, 4))
    # # plt.grid()
    # ax = fig.add_subplot(111)
    # plt.scatter(df_a.index, df_a['inflow2A'], c='r', label='inflow')
    # plt.scatter(df_a.index, df_a['water_overflow'], c='k', label='outflow')
    # # ax2 = ax.twinx()
    # # lns3 = ax2.scatter(df_a.index, df_a['pump_runtime'], c='b', label='pump-runtime')
    # fig.legend(loc=1, bbox_to_anchor=(1,1), bbox_transform=ax.transAxes)
    # plt.xlabel("Time", fontdict={'family': 'Times New Roman', 'size': 20})
    # plt.ylabel('$\mathregular{Flow (m^3/s)}$', fontdict={'family': 'Times New Roman', 'size': 20})
    # plt.xticks(fontproperties='Times New Roman', size=10)
    # plt.yticks(fontproperties='Times New Roman', size=10)
    # plt.show()
    # plt.savefig('./pics/inflow-outflow.png')
    # df_a.plot.line(secondary_y=['total volume'])


    fig = plt.figure(figsize=(8, 4))
    # plt.grid()
    ax = fig.add_subplot(111)
    plt.scatter(df_a.index, df_a['total volume'], c='k', label='Total volume-pond A')
    plt.scatter(df_b.index, df_b['total volume'], c='r', label='Total volume-pond B')
    # plt.scatter(df_a.index, df_a['water_overflow'], c='k', label='outflow')
    # ax2 = ax.twinx()
    # lns3 = ax2.scatter(df_a.index, df_a['pump_runtime'], c='b', label='pump-runtime')
    fig.legend(loc=1, bbox_to_anchor=(1, 1), bbox_transform=ax.transAxes,fontsize=16)
    plt.xlabel("Time", fontdict={'family': 'Times New Roman', 'size': 20})
    plt.ylabel('$\mathregular{Flow (m^3)}$', fontdict={'family': 'Times New Roman', 'size': 20})
    plt.xticks(fontproperties='Times New Roman', size=10)
    plt.yticks(fontproperties='Times New Roman', size=10)
    #
    fig = plt.figure(figsize=(8, 4))
    # plt.grid()
    ax = fig.add_subplot(111)
    plt.scatter(df_a.index, df_a['irrigation outflow'], c='k', label='irrigation outflow-pond A')
    plt.scatter(df_b.index, df_b['irrigation outflow'], c='r', label='irrigation outflow-pond B')
    # plt.scatter(df_a.index, df_a['water_overflow'], c='k', label='outflow')
    # ax2 = ax.twinx()
    # lns3 = ax2.scatter(df_a.index, df_a['pump_runtime'], c='b', label='pump-runtime')
    fig.legend(loc=1, bbox_to_anchor=(1, 1), bbox_transform=ax.transAxes,fontsize=16)
    plt.xlabel("Time", fontdict={'family': 'Times New Roman', 'size': 20})
    plt.ylabel('$\mathregular{Flow (m^3/h)}$', fontdict={'family': 'Times New Roman', 'size': 20})
    plt.xticks(fontproperties='Times New Roman', size=10)
    plt.yticks(fontproperties='Times New Roman', size=10)
    #
    fig = plt.figure(figsize=(8, 4))
    # plt.grid()
    ax = fig.add_subplot(111)
    plt.scatter(df_a.index, df_a['water_overflow'], c='k', label='water_overflow-pond A')
    plt.scatter(df_b.index, df_b['water_overflow'], c='r', label='water_overflow-pond B')
    # plt.scatter(df_a.index, df_a['water_overflow'], c='k', label='outflow')
    # ax2 = ax.twinx()
    # lns3 = ax2.scatter(df_a.index, df_a['pump_runtime'], c='b', label='pump-runtime')
    fig.legend(loc=1, bbox_to_anchor=(1, 1), bbox_transform=ax.transAxes,fontsize=16)
    plt.xlabel("Time", fontdict={'family': 'Times New Roman', 'size': 20})
    plt.ylabel('$\mathregular{Flow (m^3/h)}$', fontdict={'family': 'Times New Roman', 'size': 20})
    plt.xticks(fontproperties='Times New Roman', size=10)
    plt.yticks(fontproperties='Times New Roman', size=10)

    fig = plt.figure(figsize=(8, 4))
    # plt.grid()
    ax = fig.add_subplot(111)
    plt.scatter(df_a.index[800:2200], df_b['total volume'][800:2200], c='k', label='water_overflow-pond A')
    plt.scatter(df_a.index[800:2200], df_b['water_overflow'][800:2200], c='b', label='water_overflow-pond A')
    plt.scatter(df_b.index[800:2200], df['inFlow_to_Pond B (m3/h)'][800:2200], c='r', label='water_overflow-pond B')
    # plt.scatter(df_a.index, df_a['water_overflow'], c='k', label='outflow')
    # ax2 = ax.twinx()
    # lns3 = ax2.scatter(df_a.index, df_a['pump_runtime'], c='b', label='pump-runtime')
    fig.legend(loc=1, bbox_to_anchor=(1, 1), bbox_transform=ax.transAxes,fontsize=16)
    plt.xlabel("Time", fontdict={'family': 'Times New Roman', 'size': 20})
    plt.ylabel('$\mathregular{Flow (m^3)}$', fontdict={'family': 'Times New Roman', 'size': 20})
    plt.xticks(fontproperties='Times New Roman', size=10)
    plt.yticks(fontproperties='Times New Roman', size=10)
