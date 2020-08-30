# -*- coding: utf-8 -*-
# @Time    : 2020/8/28 18:38
# @Author  : hyy
# @Email   : hyywestwood@zju.edu.cn
# @File    : question_4_test.py
# @Software: PyCharm
from PyQt5.QtWidgets import *
from PyQt5.uic import loadUi

from matplotlib.backends.backend_qt5agg import (NavigationToolbar2QT  as  NavigationToolbar)
from test import *
import numpy  as  np
import random


class MatplotlibWidget_test(QMainWindow, Ui_MainWindow):
    def __init__(self, parent = None):
        super(MatplotlibWidget_test, self).__init__(parent)
        self.setWindowTitle("PyQt5 & Matplotlib Example GUI")
        self.update_graph()
        # self.pushButton_generate_random_signal.clicked.connect(self.update_graph)

        # self.addToolBar(NavigationToolbar(self.MplWidget.canvas, self))

    def update_graph(self):
        fs = 500
        f = random.randint(1, 100)
        ts = 1 / fs
        length_of_signal = 100
        t = np.linspace(0, 1, length_of_signal)

        cosinus_signal = np.cos(2 * np.pi * f * t)
        sinus_signal = np.sin(2 * np.pi * f * t)

        self.widget_2.canvas.axes.clear()
        self.widget_2.canvas.axes.plot(t, cosinus_signal)
        self.widget_2.canvas.axes.plot(t, sinus_signal)
        self.widget_2.canvas.axes.legend(('cosinus', 'sinus'), loc='upper right')
        self.widget_2.canvas.axes.set_title(' Cosinus - Sinus Signal')
        self.widget_2.canvas.draw()


app = QApplication([])
window = MatplotlibWidget_test()
window.show()
app.exec_()