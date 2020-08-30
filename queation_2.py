# -*- coding: utf-8 -*-
# @Time    : 2020/8/27 16:56
# @Author  : hyy
# @Email   : hyywestwood@zju.edu.cn
# @File    : queation_2.py
# @Software: PyCharm
from question_1 import Pond_A, Pond_B
from water_type import *
import pandas as pd
import numpy as np
import datetime
import matplotlib.pyplot as plt


class link_Pond(Pond_A):
    def __init__(self, max_volumeA=360000, pump_rateA=0.6, max_volumeB=90000, pump_rateB=0.25):
        # self.A = Pond_A()
        # self.B = Pond_B()
        self.max_volume = max_volumeA + max_volumeB  # m3
        self.pump = pump(pump_rateA + pump_rateB)  # 存疑？联通之后灌溉是两个泵抽水吗？
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


if __name__ == '__main__':
    df = pd.read_csv('Inflow_IrrigationDemand.csv')
    df['Time'] = pd.to_datetime(df['Time'])
    df.set_index("Time", inplace=True)

    linkPond = link_Pond()

    start_time = datetime.datetime.strptime('2016-1-1 0:00', '%Y-%m-%d %H:%M')
    end_time = start_time + datetime.timedelta(days=730)

    time = start_time
    residual_demand = None
    df_linkpond = pd.DataFrame(columns=['total volume', 'irrigation outflow', 'water_overflow', 'inflow2A', 'pump_runtime'])

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

    fig = plt.figure(figsize=(8, 4))
    # plt.grid()
    ax = fig.add_subplot(111)
    plt.scatter(df_linkpond.index, df_linkpond['total volume'], c='k', label='Total volume')
    # plt.scatter(df_a.index, df_a['water_overflow'], c='k', label='outflow')
    # ax2 = ax.twinx()
    # lns3 = ax2.scatter(df_a.index, df_a['pump_runtime'], c='b', label='pump-runtime')
    fig.legend(loc=1, bbox_to_anchor=(1, 1), bbox_transform=ax.transAxes,fontsize=16)
    plt.xlabel("Time", fontdict={'family': 'Times New Roman', 'size': 20})
    plt.ylabel('$\mathregular{Flow (m^3)}$', fontdict={'family': 'Times New Roman', 'size': 20})
    plt.xticks(fontproperties='Times New Roman', size=10)
    plt.yticks(fontproperties='Times New Roman', size=10)

    fig = plt.figure(figsize=(8, 4))
    # plt.grid()
    ax = fig.add_subplot(111)
    plt.scatter(df_linkpond.index, df_linkpond['irrigation outflow'], c='k', label='irrigation outflow')
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
    plt.scatter(df_linkpond.index, df_linkpond['water_overflow'], c='k', label='water_overflow')
    # plt.scatter(df_a.index, df_a['water_overflow'], c='k', label='outflow')
    # ax2 = ax.twinx()
    # lns3 = ax2.scatter(df_a.index, df_a['pump_runtime'], c='b', label='pump-runtime')
    fig.legend(loc=1, bbox_to_anchor=(1, 1), bbox_transform=ax.transAxes,fontsize=16)
    plt.xlabel("Time", fontdict={'family': 'Times New Roman', 'size': 20})
    plt.ylabel('$\mathregular{Flow (m^3/h)}$', fontdict={'family': 'Times New Roman', 'size': 20})
    plt.xticks(fontproperties='Times New Roman', size=10)
    plt.yticks(fontproperties='Times New Roman', size=10)