# -*- coding: utf-8 -*-
# @Time    : 2020/8/28 14:57
# @Author  : hyy
# @Email   : hyywestwood@zju.edu.cn
# @File    : question_4_display.py
# @Software: PyCharm
from PyQt5.QtWidgets import *
import matplotlib
matplotlib.use("Qt5Agg")  # 声明使用QT5
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt


class MplWidget(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.canvas = FigureCanvas(Figure())

        vertical_layout = QVBoxLayout()
        vertical_layout.addWidget(self.canvas)

        self.canvas.axes = self.canvas.figure.add_subplot(111)
        self.setLayout(vertical_layout)