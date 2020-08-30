# -*- coding: utf-8 -*-
# @Time    : 2020/8/28 1:03
# @Author  : hyy
# @Email   : hyywestwood@zju.edu.cn
# @File    : new_UI.py
# @Software: PyCharm
import os
import subprocess
import sys
import qdarkstyle
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox
from test import *
from PyQt5.QtCore import pyqtSignal, QThreadPool, QObject, QRunnable
from PyQt5.QtGui import QIntValidator,QDoubleValidator, QRegExpValidator
from PyQt5.QtGui import QTextCursor, QStandardItemModel, QStandardItem, QIcon
from question_4_simulation import Worker_link, Worker_notlink


class MyWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, parent = None):
        super(MyWindow, self).__init__(parent)
        self.setWindowIcon(QIcon('.\\icon.ico'))
        self.threadpool = QThreadPool()  # 使用多线程解决主窗口不响应的问题
        self.variables = [0.6, 360000, 0.25, 90000]  # 模型参数预设初始值
        self.is_link = False  # A B 调蓄带默认不连通
        self.setupUi(self)
        self.setWindowTitle('调蓄带调蓄模拟程序 V0.0.01')
        self.settings()
        self.run_progress_bar.setValue(0)
        self.parameter_run()
        self.testbtn1.clicked.connect(self.btn1_fun)
        self.testbtn2.clicked.connect(self.btn2_fun)
        self.testbtn3.clicked.connect(self.btn3_fun)
        self.testbtn4.clicked.connect(self.file_write)
        self.testbtn2.setEnabled(False)
        self.testbtn3.setEnabled(False)
        self.testbtn4.setEnabled(False)
        self.draw_selection_box.currentIndexChanged.connect(self.pic_change)

    def btn1_fun(self):
        self.stackedWidget.setCurrentIndex(0)

    def btn2_fun(self):
        self.stackedWidget.setCurrentIndex(1)

    def btn3_fun(self):
        self.stackedWidget.setCurrentIndex(2)

    def file_write(self):
        path1 = os.path.join('.', 'results')
        if not os.path.exists(path1):
            os.mkdir(path1)
        if self.is_link:
            self.df.to_csv('./results/data_of_linkpond.csv')
        else:
            self.df.to_csv('./results/data_of_pondA.csv')
            self.df_plus.to_csv('./results/data_of_pondB.csv')
        self.add_message('结果文件成功生成！')
        QMessageBox.information(self, '恭喜！', '结果文件成功生成，请在./results文件夹下查看',
                                QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)

    pargetSignal = pyqtSignal()

    def parameter_run(self):
        self.pargetSignal.connect(self.getpar) # 连接信号与槽
        self.simulatebtn.clicked.connect(self.pargetSignal.emit) # 建立点击按钮，发送信号的连接

    # 获得模型参数的具体实现
    def getpar(self):
        # 得到参数后禁止按钮再被点击，且绘图界面暂时关闭
        self.simulatebtn.setEnabled(False)
        self.testbtn2.setEnabled(False)
        self.testbtn3.setEnabled(False)
        self.testbtn4.setEnabled(False)

        lineedit = [self.pump_rate_A.text(), self.maxvolume_A.text(), self.pump_rate_B.text(), self.maxvolume_B.text()]
        for ind, item in enumerate(lineedit):
            if item.isnumeric():
                self.variables[ind] = float(item)
        self.is_link = self.islinkcheackbox.isChecked()

        # 设置消息提示即将开始模拟，确认输入参数，确认后开始模拟
        message = "<p>将使用以下参数进行模拟，是否继续？</p>" \
                  "<p>调蓄池A：水泵流量：{} 库容：{}</p>" \
                  "<p>调蓄池B：水泵流量：{} 库容：{}</p>" \
                  "<p>是否连通：{}</p>".format(self.variables[0], self.variables[1], self.variables[2],
                                          self.variables[3], self.is_link)
        reply = QMessageBox.information(self, '参数信息确认', message,
                                        QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
        if reply == QMessageBox.Yes:
            if self.is_link:
                work = Worker_link(self.variables, self.is_link)
                work.signals_run.result.connect(self.pbar_show)
                work.signals_finished.result.connect(self.result_display)
            else:
                work = Worker_notlink(self.variables, self.is_link)
                work.signals_run.result.connect(self.pbar_show)
                work.signals_finished.result.connect(self.result_display)
            self.threadpool.start(work)
            # self.plainTextEdit.setPlainText("")
        else:
            self.simulatebtn.setEnabled(True)
            print('未进行模拟......')
        # self.plot_test(self.case.df_a, self.case.df_b)

    def pbar_show(self, step):
        # self.add_message('run scuess here')
        self.run_progress_bar.setValue(step)

    def result_display(self, df, df_plus=None):
        self.df = df
        self.df_plus = df_plus
        self.testbtn2.setEnabled(True)
        self.testbtn3.setEnabled(True)
        self.testbtn4.setEnabled(True)
        # print(df.columns)
        # 与matplotlib结合做模拟结果的显示
        if self.is_link:
            # 如果水池连通
            self.draw_widget.mpl.start_static_plot_link(df.index, df['total volume'],
                                                   self.draw_selection_box.currentText())
            self.draw_widget2.mpl.draw_efficiency(df.index, df['irrigation outflow'], df['water_overflow'])
        else:
            # 水池不连通
            self.draw_widget.mpl.start_static_plot(df.index, df['total volume'], df_plus['total volume'], self.draw_selection_box.currentText())
            self.draw_widget2.mpl.draw_efficiency(df.index, df['irrigation outflow'], df['water_overflow'])
            # print(df_plus.columns)
        # 模拟完毕，运行模拟按钮可以再被点击了
        self.simulatebtn.setEnabled(True)

    def pic_change(self, i):
        if self.is_link:
            self.draw_widget.mpl.start_static_plot_link(self.df.index, self.df[self.df.columns[i]],
                                                        self.draw_selection_box.currentText())
        else:
            self.add_message('正尝试更改时间序列图' + self.draw_selection_box.currentText())
            # self.add_message(self.df.columns[i])
            self.draw_widget.mpl.start_static_plot(self.df.index, self.df[self.df.columns[i]],
                                                   self.df_plus[self.df_plus.columns[i]],self.draw_selection_box.currentText())

    # 向窗口增加一些信息
    def add_message(self, msg):
        self.plainTextEdit.moveCursor(QTextCursor.End)
        self.plainTextEdit.appendPlainText(msg)

    # 限值参数的输入
    def settings(self):
        doubleValidator1 = QDoubleValidator(self)
        doubleValidator1.setRange(0, 500000)
        doubleValidator2 = QDoubleValidator(self)
        doubleValidator2.setRange(0, 1)
        self.maxvolume_A.setValidator(doubleValidator1)
        self.maxvolume_B.setValidator(doubleValidator1)
        self.pump_rate_A.setValidator(doubleValidator2)
        self.pump_rate_B.setValidator(doubleValidator2)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    myWin = MyWindow()
    # setup stylesheet
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
    # or in new API
    # app.setStyleSheet(qdarkstyle.load_stylesheet(qt_api='pyqt5'))
    myWin.show()
    sys.exit(app.exec_())
