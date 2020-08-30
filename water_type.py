# -*- coding: utf-8 -*-
# @Time    : 2020/8/26 23:53
# @Author  : hyy
# @Email   : hyywestwood@zju.edu.cn
# @File    : water_type.py
# @Software: PyCharm


# 从水厂来的水
class water_type_plant():
    def __init__(self, volume):
        self.volume = volume  #m3
        self.age = 0


# 雨水与污水
class water_type_rain():
    def __init__(self, volume):
        self.volume = volume  #m3
        self.age = 0


# 原调蓄带中的水
class water_type_original():
    def __init__(self, volume):
        self.volume = volume  #m3
        self.age = 0


# 水泵
class pump():
    def __init__(self, pump_rate):
        self.pump_rate = pump_rate  #m3/s
        self.runtime = 0   # hours
        self.max_pump_runtime = 12

    def run(self, volume, runtime_useful):
        # 泵试图在不超过其最大工作时间的情况下，将volume排出
        time_will_used = volume / self.pump_rate / 3600
        if time_will_used <= runtime_useful:
            self.runtime += time_will_used
            runtime_useful -= time_will_used
            return runtime_useful, None
        else:
            volume = volume - self.pump_rate*runtime_useful*3600
            self.runtime = runtime_useful
            runtime_useful = 0
            return runtime_useful, volume


if __name__ == '__main__':
    def aaa(a):
        if a == 4:
            a = 3

    d = 4
    aaa(3)