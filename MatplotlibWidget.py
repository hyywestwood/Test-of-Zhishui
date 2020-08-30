# -*- coding: utf-8 -*-
# @Time    : 2020/8/28 18:47
# @Author  : hyy
# @Email   : hyywestwood@zju.edu.cn
# @File    : MatplotlibWidget.py
# @Software: PyCharm
import sys
import random
import matplotlib

matplotlib.use("Qt5Agg")
from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QSizePolicy, QWidget
from numpy import arange, sin, pi
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
import matplotlib.pyplot as plt


class MyMplCanvas(FigureCanvas):
    """FigureCanvas的最终的父类其实是QWidget。"""

    def __init__(self, parent=None, width=5, height=4, dpi=100):

        # 配置中文显示
        plt.rcParams['font.family'] = ['SimHei']  # 用来正常显示中文标签
        plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号

        self.fig = Figure(figsize=(width, height), dpi=dpi)  # 新建一个figure
        # self.axes.hold(False)  # 每次绘图的时候不保留上一次绘图的结果

        FigureCanvas.__init__(self, self.fig)
        self.setParent(parent)

        '''定义FigureCanvas的尺寸策略，这部分的意思是设置FigureCanvas，使之尽可能的向外填充空间。'''
        FigureCanvas.setSizePolicy(self,
                                   QSizePolicy.Expanding,
                                   QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

    '''绘制静态图，可以在这里定义自己的绘图逻辑'''

    def start_static_plot(self, X, Y1, Y2, title):
        self.fig.clf()
        self.fig.suptitle(title)
        self.axes = self.fig.add_subplot(111, facecolor=(.18, .31, .31))  # 建立一个子图，如果要建立复合图，可以在这里修改
        self.axes.set_facecolor('#eafff5')
        self.axes.scatter(X, Y1, c='k', label='Pond A:' + Y1.name)
        self.axes.scatter(X, Y2, c='r', label='Pond B:' + Y2.name)
        self.axes.set_ylabel('Time')
        self.axes.set_xlabel('volume (m3)')
        self.axes.legend()
        self.axes.grid(True)
        self.draw()

    def start_static_plot_link(self, X, Y, title):
        self.fig.clf()
        self.fig.suptitle(title)
        self.axes = self.fig.add_subplot(111)  # 建立一个子图，如果要建立复合图，可以在这里修改
        self.axes.scatter(X, Y, c='k', label='linkPond:'+Y.name)
        self.axes.set_ylabel('Time')
        self.axes.set_xlabel(Y.name)
        self.axes.legend()
        self.axes.grid(True)
        self.draw()

    def draw_efficiency(self, X, irrigation, overflow):
        self.fig.clf()
        self.axes = self.fig.add_subplot(111)  # 建立一个子图，如果要建立复合图，可以在这里修改
        self.axes.scatter(X, irrigation, c='k', label='irrigation outflow')
        self.axes.scatter(X, overflow, c='r', label='water overflow')
        self.axes.set_ylabel('Time')
        self.axes.set_xlabel('Total volume (m3)')
        self.axes.legend()
        self.axes.grid(True)

        self.draw()

    '''启动绘制动态图'''
    def start_dynamic_plot(self, *args, **kwargs):
        timer = QtCore.QTimer(self)
        timer.timeout.connect(self.update_figure)  # 每隔一段时间就会触发一次update_figure函数。
        timer.start(1000)  # 触发的时间间隔为1秒。

    '''动态图的绘图逻辑可以在这里修改'''

    def update_figure(self):
        self.fig.suptitle('测试动态图')
        l = [random.randint(0, 10) for i in range(4)]
        self.axes.plot([0, 1, 2, 3], l, 'r')
        self.axes.set_ylabel('动态图：Y轴')
        self.axes.set_xlabel('动态图：X轴')
        self.axes.grid(True)
        self.draw()


class MatplotlibWidget(QWidget):
    def __init__(self, parent=None):
        super(MatplotlibWidget, self).__init__(parent)
        self.initUi()

    def initUi(self):
        self.layout = QVBoxLayout(self)
        self.mpl = MyMplCanvas(self, width=5, height=4, dpi=100)
        # self.mpl.start_static_plot() # 如果你想要初始化的时候就呈现静态图，请把这行注释去掉
        #self.mpl.start_dynamic_plot() # 如果你想要初始化的时候就呈现动态图，请把这行注释去掉
        self.mpl_ntb = NavigationToolbar(self.mpl, self)  # 添加完整的 toolbar

        self.layout.addWidget(self.mpl)
        self.layout.addWidget(self.mpl_ntb)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ui = MatplotlibWidget()
    ui.mpl.start_static_plot()  # 测试静态图效果
    # ui.mpl.start_dynamic_plot() # 测试动态图效果
    ui.show()
    sys.exit(app.exec_())