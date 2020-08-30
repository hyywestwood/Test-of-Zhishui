# -*- coding: utf-8 -*-
# @Time    : 2020/8/27 19:27
# @Author  : hyy
# @Email   : hyywestwood@zju.edu.cn
# @File    : question_3.py
# @Software: PyCharm
from question_1 import Pond_A, Pond_B
from water_type import *
import numpy as np
import pandas as pd
import datetime
import matplotlib.pyplot as plt


class link_Pond(Pond_A):
    def __init__(self, pump_raise = 1, maxvolume_raise = 1):
        self.A = Pond_A()
        self.B = Pond_B()
        self.max_volume = self.A.max_volume + self.B.max_volume  # m3
        self.max_volume = self.max_volume * maxvolume_raise  # m3
        self.pump = pump((0.25 + 0.6)*pump_raise)  # 存疑？联通之后灌溉是两个泵抽水吗？
        self.water = []
        self.total_volume = 0
        self.irrigation_outflow = 0
        self.water_overflow = 0

    def inflowA(self, current_time, df):
        volume = df.loc[current_time]['inFlow_to_Pond A (m3/h)']
        self.total_volume += volume
        return water_type_rain(volume)

    def inflowB(self, current_time, df):
        volume = df.loc[current_time]['inFlow_to_Pond B (m3/h)']
        self.total_volume += volume
        return water_type_rain(volume)


def simulation(pump_raise = 1, maxvolume_raise = 1):
    linkPond = link_Pond(pump_raise, maxvolume_raise)

    start_time = datetime.datetime.strptime('2016-1-1 0:00', '%Y-%m-%d %H:%M')
    end_time = start_time + datetime.timedelta(days=731)

    time = start_time
    residual_demand = None
    df_linkpond = pd.DataFrame(
        columns=['total volume', 'irrigation outflow', 'water_overflow', 'inflow2A', 'pump_runtime'])

    while time < end_time:
        # 调蓄带, 包括污雨水汇入，灌溉用水排出，水厂水源汇入和超量排出四个过程
        linkPond.water.append(linkPond.inflowA(time, df))  # A雨污水汇入
        linkPond.water.append(linkPond.inflowB(time, df))  # B雨污水汇入
        residual_demand = linkPond.irrigation_demand(time, df, residual_demand)  # 灌溉用水排出
        # 新的一天开始
        if time.hour == 0:
            linkPond.pump.runtime = 0  # 水泵运行时间清空
            if linkPond.total_volume < linkPond.max_volume:
                linkPond.water.append(linkPond._water_from_waterplant())  # 水厂水源汇入
        linkPond.overflow()
        linkPond.self_sort()

        df_linkpond.loc[time] = [linkPond.total_volume, linkPond.irrigation_outflow, linkPond.water_overflow,
                                 df.loc[time]['inFlow_to_Pond A (m3/h)'], linkPond.pump.runtime]
        time += datetime.timedelta(hours=1)

    # 求解利用效率
    sum_out = df_linkpond['irrigation outflow'].to_numpy() + df_linkpond['water_overflow'].to_numpy()
    efficiency_list = df_linkpond['irrigation outflow'].to_numpy() / sum_out
    efficiency_list[np.isnan(efficiency_list)] = 0
    return np.mean(efficiency_list), df_linkpond


if __name__ == '__main__':
    df = pd.read_csv('Inflow_IrrigationDemand.csv')
    df['Time'] = pd.to_datetime(df['Time'])
    df.set_index("Time", inplace=True)

    # 泵抽水能力增加幅度，库容增幅，1代表不增，2.5表示增加150%， 2表示增加100%
    pump_raise_list = np.linspace(0.1, 1, 7)
    maxvolume_raise_list = np.linspace(0.1, 1, 7)
    df_link_list = []
    efficiency_pump, efficiency_maxvolume = [], []
    for i in range(len(pump_raise_list)):
        # efficiency, df_linkpond = simulation(pump_raise_list[i], 1)
        efficiency, df_linkpond = simulation(1, maxvolume_raise_list[i])
        # efficiency_pump.append(simulation(pump_raise_list[i], 1))
        efficiency_maxvolume.append(efficiency)
        df_link_list.append(df_linkpond)

    # fig = plt.figure(figsize=(8, 7))
    # # plt.grid()
    # ax = fig.add_subplot(211)
    # plt.scatter(df_linkpond.index, df_linkpond['irrigation outflow'], c='k', label='irrigation outflow')
    # plt.scatter(df_linkpond.index, df['irrigation_demand  (m3/h)'], c='b', label='irrigation_demand')
    # fig.legend(loc=1, bbox_to_anchor=(1, 1), bbox_transform=ax.transAxes)
    # plt.xlabel("Time", fontdict={'family': 'Times New Roman', 'size': 20})
    # plt.ylabel('$\mathregular{Flow (m^3)}$', fontdict={'family': 'Times New Roman', 'size': 20})
    # plt.xticks(fontproperties='Times New Roman', size=10)
    # plt.yticks(fontproperties='Times New Roman', size=10)
    #
    # ax1 = fig.add_subplot(212)
    # plt.grid()
    # plt.scatter(df_linkpond.index, df_linkpond['pump_runtime'], c='r', label='pump_runtime')
    # fig.legend(loc=1, bbox_to_anchor=(1, 1), bbox_transform=ax.transAxes)
    # plt.xlabel("Time", fontdict={'family': 'Times New Roman', 'size': 20})
    # plt.ylabel('Pump runtime (h)', fontdict={'family': 'Times New Roman', 'size': 20})
    # plt.xticks(fontproperties='Times New Roman', size=10)
    # plt.yticks(fontproperties='Times New Roman', size=10)

    # fig = plt.figure(figsize=(8, 4))
    # # plt.grid()
    # ax = fig.add_subplot(111)
    # plt.scatter(df.index, df['irrigation_demand  (m3/h)'], c='k', label='irrigation_demand  (m3/h)')
    # plt.scatter(df.index, df_link_list[0]['irrigation outflow'], c='r', label='pump rate:0.085')
    # plt.scatter(df.index, df_link_list[1]['irrigation outflow'], c='b', label='pump rate:0.085')
    # # plt.scatter(df.index, df_link_list[0]['water_overflow'], c='k', label='water_overflow')
    # # plt.twinx()
    # # plt.scatter(df.index, df_link_list[0]['pump_runtime'], c='r', label='pump_runtime')
    # # plt.scatter(df_a.index, df_a['water_overflow'], c='k', label='outflow')
    # # ax2 = ax.twinx()
    # # lns3 = ax2.scatter(df_a.index, df_a['pump_runtime'], c='b', label='pump-runtime')
    # fig.legend(loc=1, bbox_to_anchor=(1, 1), bbox_transform=ax.transAxes, fontsize=12)
    # plt.xlabel("Time", fontdict={'family': 'Times New Roman', 'size': 20})
    # plt.ylabel('$\mathregular{Flow (m^3/h)}$', fontdict={'family': 'Times New Roman', 'size': 20})
    # plt.xticks(fontproperties='Times New Roman', size=10)
    # plt.yticks(fontproperties='Times New Roman', size=10)

    demand, outflow_1, outflow_2, outflow_3 = [], [], [], []
    for i in range(len(df.index)):
        demand.append(sum(df['irrigation_demand  (m3/h)'][:i+1]))
        outflow_1.append(sum(df_link_list[0]['irrigation outflow'][:i+1]))
        outflow_2.append(sum(df_link_list[1]['irrigation outflow'][:i + 1]))
        outflow_3.append(sum(df_link_list[2]['irrigation outflow'][:i + 1]))

    fig = plt.figure(figsize=(8, 4))
    # plt.grid()
    ax = fig.add_subplot(111)
    plt.plot(df.index, demand, 'k',linewidth=3, label='Total irrigation_demand')
    plt.plot(df.index, outflow_1, 'r',linewidth=2, label='Total irrigation outflow:pump rate:0.085')
    plt.plot(df.index, outflow_2, 'b', linewidth=2, label='Total irrigation outflow:pump rate:0.2125')
    plt.plot(df.index, outflow_3, 'g', linewidth=2, label='Total irrigation outflow:pump rate:0.34')
    fig.legend(loc=2, bbox_to_anchor=(0, 1), bbox_transform=ax.transAxes, fontsize=12)
    plt.xlabel("Time", fontdict={'family': 'Times New Roman', 'size': 20})
    plt.ylabel('$\mathregular{Volume (m^3)}$', fontdict={'family': 'Times New Roman', 'size': 20})
    plt.xticks(fontproperties='Times New Roman', size=10)
    plt.yticks(fontproperties='Times New Roman', size=10)
    #
    effi_list = []
    for item in df_link_list:
        sum_out = item['irrigation outflow'].to_numpy() + item['water_overflow'].to_numpy()
        e = item['irrigation outflow'].to_numpy() / sum_out
        e[np.isnan(e)] = 0
        effi_list.append(e)

    fig = plt.figure(figsize=(8, 4))
    # plt.grid()
    ax = fig.add_subplot(111)
    plt.scatter(df.index, effi_list[0], c='r', label='maxvolume:45000')
    plt.scatter(df.index, effi_list[1], c='b', label='maxvolume:112500')
    plt.scatter(df.index, effi_list[2], c='g', label='maxvolume:180000')
    fig.legend(loc=1, bbox_to_anchor=(1, 1), bbox_transform=ax.transAxes, fontsize=12)
    plt.xlabel("Time", fontdict={'family': 'Times New Roman', 'size': 20})
    plt.ylabel('Efficiency', fontdict={'family': 'Times New Roman', 'size': 20})
    plt.xticks(fontproperties='Times New Roman', size=10)
    plt.yticks(fontproperties='Times New Roman', size=10)
