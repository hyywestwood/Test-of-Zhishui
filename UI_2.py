# -*- coding: utf-8 -*-
# @Time    : 2019/11/22 13:15
# @Author  : hyy
# @Email   : 1554148540@qq.com
# @File    : UI_2.py
# @Software: PyCharm
import subprocess
import sys, codecs
import os, linecache

from PyQt5.QtCore import QThreadPool, QRunnable, QObject, pyqtSignal
from PyQt5.QtGui import QTextCursor, QStandardItemModel, QStandardItem, QIcon
from PyQt5.QtWidgets import (QApplication, QTextEdit,
                             QPushButton, QWidget, QVBoxLayout, QTableView, QHeaderView, QHBoxLayout, QMessageBox,
                             QStackedWidget, QGridLayout)


class WorkerSignals(QObject):
    result = pyqtSignal(object)


class Worker(QRunnable):
    def __init__(self):
        super(Worker, self).__init__()
        self.signals = WorkerSignals()

    def run(self):
        exePath = r'.\LH_simulation.exe'
        liaohe = subprocess.Popen(exePath, bufsize=0, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                  encoding='gbk', universal_newlines=True)
        while True:
            nextline = liaohe.stdout.readline()
            self.signals.result.emit(nextline)


class Table(QWidget):

    def __init__(self,parent=None):
        super(Table, self).__init__(parent)

        self.data, self.variables = get_data()
        self.meaning = ['最大生长速率', '硝酸盐参考浓度', '藻类氮半饱和常数', '藻类适宜温度下限','藻类适宜温度上限',
                        '低温效应系数', '高温效应系数', '代谢的温度效应系数', '代谢参考温度', '基础代谢速率',
                        '捕食作用速率', '捕食温度效应系数', '捕食浓度参考值', '捕食经验系数', '盐度半饱和常数',
                        '最大硝化速率', '硝化最适温度下限', '硝化最适温度上限', '硝化低温效应系数', '硝化高温效应系数',
                        '硝化溶解氧半饱和常数', '硝化氮半饱和常数', '代谢氮分配系数', '捕食氮分配系数', '藻类氮碳比',
                        'COD降解速率', 'COD半饱和常数', '复氧系数', '水面风速', '复氧参考温度',
                        '藻类生长的氧碳比', '藻类生长氮碳比', '经验参数']
        self.value_range = ['1-5', '已停用', '0.01-0.3', '15-25', '15-25',
                            '0.012', '0.012', '0.322', '15-25', '0.001-0.1',
                            '0.01-1', '0.01', '1.0', '1.1', '1.0',
                            '0.01-0.8', '15-30', '15-30', '0.0045-0.006', '0.0045-0.006',
                            '0.01-1', '0.2-1', '1', '1', '0.1-0.5',
                            '0.1-1国外概念', '0.5-3国外概念', '1-5', '', '15-25',
                            '2.1', '4.33', '已停用']
        # 设置数据层次结构，4行4列
        self.model=QStandardItemModel(len(self.data), 3)
        # 设置水平方向四个头标签文本内容
        self.model.setHorizontalHeaderLabels(['污染物参数', '参数取值', '常见取值范围'])

        for row in range(len(self.data)):
            for column in range(3):
                if column == 0:
                    item=QStandardItem('%s' % (self.meaning[row] + '-' + self.variables[row]))
                    item.setEditable(False)
                elif column == 1:
                    item = QStandardItem('%.4f' % self.data[row])
                else:
                    item = QStandardItem('%s' % self.value_range[row])
                    item.setEditable(False)
                # 设置每个位置的文本值
                self.model.setItem(row,column,item)

        # 实例化表格视图，设置模型为自定义的模型
        self.tableView=QTableView()
        self.tableView.setModel(self.model)

        # #todo 优化1 表格填满窗口
        # #水平方向标签拓展剩下的窗口部分，填满表格
        self.tableView.horizontalHeader().setStretchLastSection(True)
        # #水平方向，表格大小拓展到适当的尺寸
        self.tableView.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # 设置布局
        layout=QVBoxLayout()
        layout.addWidget(self.tableView)
        self.setLayout(layout)


def get_data():
    f_path = os.getcwd() + "\\pollution_parameter.txt"
    data = []
    variables = []
    for i in range(1,5):
        line = linecache.getline(f_path, 3 * i - 1)
        # print(line)
        # input()
        variables = variables + line.split()
        linecache.clearcache()

        line = linecache.getline(f_path, 3*i)
        data = data + list(map(float, line.split()))
        linecache.clearcache()
    return data, variables


class MainWindow(QWidget):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.resize(1000, 800)
        self.setWindowTitle('调蓄带调蓄模拟程序 V0.0.01')
        self.setWindowIcon(QIcon('.\\icon.ico'))
        self.threadpool = QThreadPool() # 使用多线程解决主窗口不响应的问题

        # 这次只设置一个主页面，分为参数设置及结果显示两部分
        self.main_Layout = QVBoxLayout()

        # 参数部分
        variables_Layout = QGridLayout()


        # 设置界面左边按钮
        self.but_box = QVBoxLayout()
        b_canshu = QPushButton('参数设置')
        b_canshu.pressed.connect(self.change_layout)
        b_run = QPushButton('程序运行')
        b_run.pressed.connect(self.change_layout1)
        self.but_box.addWidget(b_canshu)
        self.but_box.addWidget(b_run)
        self.btn = QWidget()
        self.btn.setLayout(self.but_box)

        # 设置参数更改界面的布局，由一个按钮和一个表格组成
        self.canshu_layout = QVBoxLayout()
        self.table = Table()
        b1 = QPushButton("参数更改完毕请按此按钮重新生成参数文件")
        b1.pressed.connect(self.change_file)
        self.canshu_layout.addWidget(self.table)
        self.canshu_layout.addWidget(b1)
        self.stack1 = QWidget()
        self.stack1.setLayout(self.canshu_layout)

        # 设置程序运行界面的布局，由一个按钮和一个富文本控件组成
        self.run_layout = QVBoxLayout()
        self.text = QTextEdit()
        self.text.setText('点击运行开始辽河污染模拟')
        b2 = QPushButton("运行")
        b2.pressed.connect(self.run)
        self.run_layout.addWidget(self.text)
        self.run_layout.addWidget(b2)
        self.stack2 = QWidget()
        self.stack2.setLayout(self.run_layout)

        # 堆载窗口控件
        self.stack = QStackedWidget(self)
        self.stack.addWidget(self.stack1)
        self.stack.addWidget(self.stack2)

        # 设置程序主页面的总布局，由左侧的两个按钮和右边对应的操作页面组成
        # 通过按钮事件来指定右边的显示为stack中的哪一个
        layout = QHBoxLayout()
        layout.addWidget(self.btn)
        layout.addWidget(self.stack)
        self.setLayout(layout)

    def text_change(self, text):
        self.text.moveCursor(QTextCursor.End)
        self.text.append(text)

    def run(self):
        work = Worker()
        work.signals.result.connect(self.text_change)
        self.threadpool.start(work)

    def change_file(self):
        with codecs.open("temp.txt", "w", encoding='utf-8') as fid:
            fid.write('与藻类有关的系数 \r')
            for i in range(0, 15):
                fid.write(self.table.variables[i] + "\t")
            fid.write("\r")
            for i in range(0, 15):
                fid.write(self.table.model.item(i, 1).text() + "\t")
            fid.write("\r")

            fid.write('与氨氮有关的经验系数 \r')
            for i in range(15, 25):
                fid.write(self.table.variables[i] + "\t")
            fid.write("\r")
            for i in range(15, 25):
                fid.write(self.table.model.item(i, 1).text() + "\t")
            fid.write("\r")

            fid.write('与化学需氧量有关的参数 \r')
            for i in range(25, 27):
                fid.write(self.table.variables[i] + "\t")
            fid.write("\r")
            for i in range(25, 27):
                fid.write(self.table.model.item(i, 1).text() + "\t")
            fid.write("\r")

            fid.write('与溶解氧有关的经验参数 \r')
            for i in range(27, 33):
                fid.write(self.table.variables[i] + "\t")
            fid.write("\r")
            for i in range(27, 33):
                fid.write(self.table.model.item(i, 1).text() + "\t")
            fid.write("\r")

        os.remove("pollution_parameter.txt")
        os.rename('temp.txt', 'pollution_parameter.txt')

        # 设置消息提示完成
        QMessageBox.information(self, '程序信息', '参数文件已重新生成！', QMessageBox.Yes|QMessageBox.No, QMessageBox.Yes)

    def change_layout(self):
        self.stack.setCurrentIndex(0)

    def change_layout1(self):
        self.stack.setCurrentIndex(1)


if __name__ == '__main__':
    app = QApplication(sys.argv)

    a = MainWindow()
    a.show()
    sys.exit(app.exec_())