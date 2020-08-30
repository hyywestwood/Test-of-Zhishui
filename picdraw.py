# -*- coding: utf-8 -*-
# @Time    : 2020/8/27 16:42
# @Author  : hyy
# @Email   : hyywestwood@zju.edu.cn
# @File    : picdraw.py
# @Software: PyCharm
import matplotlib.pyplot as plt


class pic_question():
    def pondA(self, df_a):
        fig = plt.figure(figsize=(8, 4))
        # plt.grid()
        ax = fig.add_subplot(111)
        plt.scatter(df_a.index, df_a['total volume'], c='k', label='Total volume')
        # plt.scatter(df_a.index, df_a['water_overflow'], c='k', label='outflow')
        # ax2 = ax.twinx()
        # lns3 = ax2.scatter(df_a.index, df_a['pump_runtime'], c='b', label='pump-runtime')
        fig.legend(loc=1, bbox_to_anchor=(1, 1), bbox_transform=ax.transAxes)
        plt.xlabel("Time", fontdict={'family': 'Times New Roman', 'size': 20})
        plt.ylabel('$\mathregular{Flow (m^3/s)}$', fontdict={'family': 'Times New Roman', 'size': 20})
        plt.xticks(fontproperties='Times New Roman', size=10)
        plt.yticks(fontproperties='Times New Roman', size=10)