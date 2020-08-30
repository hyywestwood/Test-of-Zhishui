# -*- coding: utf-8 -*-
# @Time    : 2020/8/28 11:42
# @Author  : hyy
# @Email   : hyywestwood@zju.edu.cn
# @File    : question_4_simulation.py
# @Software: PyCharm
from PyQt5.QtCore import QObject, pyqtSignal, QRunnable

from question_1 import Pond_A, Pond_B
from queation_2 import link_Pond
from water_type import *
import numpy as np
import pandas as pd
import datetime
import matplotlib.pyplot as plt


class WorkerSignals(QObject):
    result = pyqtSignal(object)

class WorkerSignals1(QObject):
    result = pyqtSignal(object, object)

class Worker_link(QRunnable):
    def __init__(self, variables, is_linked):
        super(Worker_link, self).__init__()
        self.signals_run = WorkerSignals()
        self.signals_finished = WorkerSignals()
        self.variables = variables
        self.is_linked = is_linked
        df = pd.read_csv('Inflow_IrrigationDemand.csv')
        df['Time'] = pd.to_datetime(df['Time'])
        df.set_index("Time", inplace=True)
        self.df = df
        # 连通
        self.pond = link_Pond(variables[1], variables[0], variables[3], variables[2])

    def run(self):
        start_time = datetime.datetime.strptime('2016-1-1 0:00', '%Y-%m-%d %H:%M')
        end_time = start_time + datetime.timedelta(days=730)

        time = start_time
        residual_demand = None
        df_linkpond = pd.DataFrame(
            columns=['total volume', 'irrigation outflow', 'water_overflow', 'inflow2A', 'pump_runtime'])

        while time < end_time:
            # 调蓄带, 包括污雨水汇入，灌溉用水排出，水厂水源汇入和超量排出四个过程
            self.pond.water.append(self.pond.inflowA(time, self.df))  # A雨污水汇入
            self.pond.water.append(self.pond.inflowB(time, self.df))  # B雨污水汇入
            residual_demand = self.pond.irrigation_demand(time, self.df, residual_demand)  # 灌溉用水排出
            # 新的一天开始
            if time.hour == 0:
                self.pond.pump.runtime = 0  # 水泵运行时间清空
                if self.pond.total_volume < self.pond.max_volume:
                    self.pond.water.append(self.pond._water_from_waterplant())  # 水厂水源汇入
            self.pond.overflow()
            self.pond.self_sort()

            df_linkpond.loc[time] = [self.pond.total_volume, self.pond.irrigation_outflow, self.pond.water_overflow,
                                     self.df.loc[time]['inFlow_to_Pond A (m3/h)'], self.pond.pump.runtime]
            time += datetime.timedelta(hours=1)
            run_percent = 100*(time - start_time)/(end_time-start_time)
            self.signals_run.result.emit(int(run_percent))
        # self.case = Caserun(self.variables, self.is_linked)
        self.signals_finished.result.emit(df_linkpond)


class Worker_notlink(QRunnable):
    def __init__(self, variables, is_linked):
        super(Worker_notlink, self).__init__()
        self.signals_run = WorkerSignals()
        self.signals_finished = WorkerSignals1()
        self.variables = variables
        self.is_linked = is_linked
        df = pd.read_csv('Inflow_IrrigationDemand.csv')
        df['Time'] = pd.to_datetime(df['Time'])
        df.set_index("Time", inplace=True)
        self.df = df
        # 不连通
        self.pondA = Pond_A(variables[1], variables[0])
        self.pondB = Pond_B(variables[3], variables[2])

    def run(self):
        start_time = datetime.datetime.strptime('2016-1-1 0:00', '%Y-%m-%d %H:%M')
        end_time = start_time + datetime.timedelta(days=730)

        time = start_time
        residual_demand = None
        df_a = pd.DataFrame(
            columns=['total volume', 'irrigation outflow', 'water_overflow', 'inflow2A', 'pump_runtime'])
        df_b = pd.DataFrame(
            columns=['total volume', 'irrigation outflow', 'water_overflow', 'inflow2B', 'pump_runtime'])

        while time < end_time:
            # A 调蓄带, 包括污雨水汇入，灌溉用水排出，水厂水源汇入和超量排出四个过程
            self.pondA.water.append(self.pondA.inflow(time, self.df))  # A雨污水汇入
            residual_demand = self.pondA.irrigation_demand(time, self.df, residual_demand)  # 灌溉用水排出
            # 新的一天开始
            if time.hour == 0:
                self.pondA.pump.runtime = 0  # 水泵运行时间清空
                if self.pondA.total_volume < self.pondA.max_volume:
                    self.pondA.water.append(self.pondA._water_from_waterplant())  # 水厂水源汇入
            self.pondA.overflow()
            self.pondA.self_sort()

            # B 调蓄带，仅包含污雨水汇入和超量排出两个过程
            self.pondB.water.append(self.pondB.inflow(time, self.df))  # A雨污水汇入
            # 新的一天开始
            if time.hour == 0:
                self.pondB.pump.runtime = 0  # 水泵运行时间清空
            self.pondB.overflow()
            self.pondB.self_sort()

            df_a.loc[time] = [self.pondA.total_volume, self.pondA.irrigation_outflow, self.pondA.water_overflow,
                              self.df.loc[time]['inFlow_to_Pond A (m3/h)'], self.pondA.pump.runtime]
            df_b.loc[time] = [self.pondB.total_volume, self.pondB.irrigation_outflow, self.pondB.water_overflow,
                              self.df.loc[time]['inFlow_to_Pond B (m3/h)'], self.pondB.pump.runtime]
            time += datetime.timedelta(hours=1)
            run_percent = 100*(time - start_time)/(end_time-start_time)
            self.signals_run.result.emit(int(run_percent))
        # self.case = Caserun(self.variables, self.is_linked)
        self.signals_finished.result.emit(df_a, df_b)


class Caserun():
    def __init__(self, variables, is_linked):
        df = pd.read_csv('Inflow_IrrigationDemand.csv')
        df['Time'] = pd.to_datetime(df['Time'])
        df.set_index("Time", inplace=True)
        self.df = df
        self.signal = pyqtSignal(object)

        if is_linked:
            self.pond = link_Pond(variables[1], variables[0], variables[3], variables[2])
            self.df_linkpond = self.run_simulation1(self.df, self.pond)
            self.efficiency_linkpond, self.efficiency_list_linkpond = self.efficiency_calculate(self.df_linkpond)
        else:
            self.pondA = Pond_A(variables[1], variables[0])
            self.pondB = Pond_B(variables[3], variables[2])
            self.df_a, self.df_b = self.run_simulation2(self.df, self.pondA, self.pondB)
            self.efficiency_a, self.efficiency_list_a = self.efficiency_calculate(self.df_a)
            self.efficiency_b, self.efficiency_list_b = self.efficiency_calculate(self.df_b)

    def run_simulation1(self, df, linkpond):
        start_time = datetime.datetime.strptime('2016-1-1 0:00', '%Y-%m-%d %H:%M')
        end_time = start_time + datetime.timedelta(days=730)
        time = start_time
        residual_demand = None
        df_linkpond = pd.DataFrame(
            columns=['total volume', 'irrigation outflow', 'water_overflow', 'inflow2A', 'pump_runtime'])

        while time < end_time:
            # 调蓄带, 包括污雨水汇入，灌溉用水排出，水厂水源汇入和超量排出四个过程
            linkpond.water.append(linkpond.inflowA(time, df))  # A雨污水汇入
            linkpond.water.append(linkpond.inflowB(time, df))  # B雨污水汇入
            residual_demand = linkpond.irrigation_demand(time, df, residual_demand)  # 灌溉用水排出
            # 新的一天开始
            if time.hour == 0:
                linkpond.pump.runtime = 0  # 水泵运行时间清空
                if linkpond.total_volume < linkpond.max_volume:
                    linkpond.water.append(linkpond._water_from_waterplant())  # 水厂水源汇入
            linkpond.overflow()
            linkpond.self_sort()

            df_linkpond.loc[time] = [linkpond.total_volume, linkpond.irrigation_outflow, linkpond.water_overflow,
                                     df.loc[time]['inFlow_to_Pond A (m3/h)'], linkpond.pump.runtime]
            time += datetime.timedelta(hours=1)
            run_percent = 100*(time - start_time)/(end_time - start_time)
            self.signal.emit(int(run_percent))
        return df_linkpond

    def run_simulation2(self, df, A, B):
        start_time = datetime.datetime.strptime('2016-1-1 0:00', '%Y-%m-%d %H:%M')
        end_time = start_time + datetime.timedelta(days=730)

        time = start_time
        residual_demand = None
        df_a = pd.DataFrame(
            columns=['total volume', 'irrigation outflow', 'water_overflow', 'inflow2A', 'pump_runtime'])
        df_b = pd.DataFrame(
            columns=['total volume', 'irrigation outflow', 'water_overflow', 'inflow2B', 'pump_runtime'])

        while time < end_time:
            # A 调蓄带, 包括污雨水汇入，灌溉用水排出，水厂水源汇入和超量排出四个过程
            A.water.append(A.inflow(time, df))  # A雨污水汇入
            residual_demand = A.irrigation_demand(time, df, residual_demand)  # 灌溉用水排出
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
            run_percent = 100 * (time - start_time) / (end_time - start_time)
            self.signal.emit(int(run_percent))
        return df_a, df_b

    def efficiency_calculate(self, df):
        # 求解利用效率
        sum_out = df['irrigation outflow'].to_numpy() + df['water_overflow'].to_numpy()
        efficiency_list = df['irrigation outflow'].to_numpy() / sum_out
        efficiency_list[np.isnan(efficiency_list)] = 0
        return np.mean(efficiency_list), efficiency_list


if __name__ == '__main__':
    variables = [0.6, 360000, 0.25, 90000]
    is_link = False  # A B 调蓄带默认不连通

    # case = Caserun(variables, is_link)