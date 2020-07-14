# -*- coding: utf-8 -*-
from threading import Thread
from time import time

from matplotlib.backends.backend_qt5 import \
    NavigationToolbar2QT as NavigationToolbar
from matplotlib.backends.backend_qt5agg import \
    FigureCanvasQTAgg as FigureCanvas
from matplotlib.pyplot import cla, figure
from PySide2.QtCore import QMetaObject, QRect, QTimer
from PySide2.QtGui import QColor, QFont
from PySide2.QtWidgets import *

from flow_monitor import Monitor
from tools import get_rate, time_to_formal


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setWindowTitle("流量监测系统")
        Form.resize(950, 630)
        self.horizontalLayoutWidget = QWidget(Form)
        self.horizontalLayoutWidget.setGeometry(QRect(10, 10, 530, 30))
        self.horizontalLayout = QHBoxLayout(self.horizontalLayoutWidget)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setSpacing(10)
        Form.setFixedSize(Form.width(), Form.height())
        self.monitor = Monitor(self)
        """主字体"""
        font = QFont()
        font.setFamily("Lucida Sans Typewriter")
        font.setPointSize(10)
        """应用选择框"""
        self.comboBox = QComboBox(self.horizontalLayoutWidget)
        self.comboBox.setFont(font)
        self.horizontalLayout.addWidget(self.comboBox)
        """流量预警线设置"""
        self.warn_line = QLineEdit(self.horizontalLayoutWidget)
        self.warn_line.setText("1024")
        self.horizontalLayout.addWidget(self.warn_line)
        self.label = QLabel(self.horizontalLayoutWidget)
        self.label.setText("kB/s")
        self.horizontalLayout.addWidget(self.label)
        self.start_button = QPushButton(self.horizontalLayoutWidget)
        self.start_button.setText("开始监测")
        self.start_button.clicked.connect(self.start)
        self.horizontalLayout.addWidget(self.start_button)

        self.stop_button = QPushButton(self.horizontalLayoutWidget)
        self.stop_button.setText("停止监测")
        self.stop_button.clicked.connect(self.stop)
        self.horizontalLayout.addWidget(self.stop_button)
        self.stop_button.setEnabled(False)

        self.update_button = QPushButton(self.horizontalLayoutWidget)
        self.update_button.setText("更新进程列表")
        self.horizontalLayout.addWidget(self.update_button)
        self.horizontalLayout.setStretch(0, 2)
        self.horizontalLayout.setStretch(1, 1)
        self.horizontalLayout.setStretch(2, 1)
        self.horizontalLayout.setStretch(3, 1)
        self.horizontalLayout.setStretch(4, 1)

        self.APPList_label = QLabel(Form)
        self.APPList_label.setText("进程连接列表")
        self.APPList_label.setStyleSheet("font-size: 20px; font-family: 宋体")
        self.APPList_label.setGeometry(QRect(680, 10, 150, 30))
        """应用树列表"""
        self.App_Tree = QTreeWidget(Form)
        self.App_Tree.header().setVisible(False)
        self.App_Tree.setFont(font)
        self.App_Tree.setStyleSheet("QTreeView::item{margin:2px;}")
        self.App_Tree.setGeometry(QRect(560, 40, 380, 580))

        self.update_button.clicked.connect(self.refresh_process)

        self.verticalLayoutWidget = QWidget(Form)
        self.verticalLayoutWidget.setGeometry(QRect(10, 60, 530, 570))
        self.verticalLayout = QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)

        self.conList = QListWidget(self.verticalLayoutWidget)
        self.conList.setFont(font)
        self.conList.setStyleSheet("QListView::item{margin:2px;}")
        self.conList.setMinimumSize(421, 200)
        self.verticalLayout.addWidget(self.conList)

        self.figure = figure(figsize=(6, 3))
        self.upload_plot = self.figure.add_subplot(1, 1, 1)
        self.upload_plot.set_xlabel("Time (s)")
        self.upload_plot.set_ylabel("Speed (kB/s)")
        self.figure.tight_layout()
        self.canvas = FigureCanvas(self.figure)
        self.toolbar = NavigationToolbar(
            self.canvas,
            self.verticalLayoutWidget
            )
        self.toolbar.hide()
        self.verticalLayout.addWidget(self.toolbar)
        self.verticalLayout.addWidget(self.canvas)
        self.comboBox.addItems(self.monitor.getProcessList())
        self.show_process_tree()
        self.timer = QTimer(Form)
        self.timer.timeout.connect(self.conList.scrollToBottom)

    def show_process_tree(self):
        """
        添加节点
        """
        self.App_Tree.clear()
        process_name, process_conn = self.monitor.getProcessConnections()
        for name in process_name:
            item1 = QTreeWidgetItem(self.App_Tree)
            item1.setText(0, name)
            for connections in process_conn[name]:
                item1_1 = QTreeWidgetItem(item1)
                item1_1.setText(0, connections)

    def alert(self, info):
        """
        警告信息
        """
        alert_font = QFont()
        alert_font.setFamily("Lucida Sans Typewriter")
        alert_font.setPointSize(14)
        now = time_to_formal(time())
        item = QListWidgetItem(
            f"{now}\n{info}",
            self.conList
            )
        item.setForeground(QColor('red'))
        item.setFont(alert_font)

    def refresh_process(self):
        """
        刷新进程列表
        """
        self.comboBox.clear()
        self.comboBox.addItems(self.monitor.getProcessList())
        self.show_process_tree()

    def setSpeed(self):
        """
        设置速度图
        """
        upload = []
        download = []
        speed = int(self.warn_line.text())
        # 警告线
        alert = [speed for _ in range(60)]
        while not self.monitor.start_flag.is_set():
            info = get_rate(None)
            cla()
            self.upload_plot.set_xlabel("Time (s)")
            self.upload_plot.set_ylabel("Speed (kB/s)")
            info[1] >>= 10
            info[0] >>= 10
            upload.append(info[1])
            download.append(info[0])
            if len(upload) >= 60:
                upload.pop(0)
                download.pop(0)
            self.upload_plot.plot(
                alert,
                'red',
                linewidth='2',
                label="Warning"
                )
            self.upload_plot.legend(loc='upper right')
            self.upload_plot.plot(
                upload,
                'darkorange',
                linewidth='1',
                label="Upload"
                )
            self.upload_plot.legend(loc='upper right')
            self.upload_plot.plot(
                download,
                'blue',
                linewidth='1',
                label="Download"
                )
            self.upload_plot.legend(loc='upper right')
            self.canvas.draw()
            # 流量警告
            # 当速度大于设定值时流量警告
            if info[1] > speed or info[0] > speed:
                self.alert(
                    f"警告: 流量已超过预警线 {speed}kB/s!"
                    )

    def start(self):
        """
        开始检测
        """
        if self.monitor.start_flag.is_set():
            self.start_button.setEnabled(False)
            self.stop_button.setEnabled(True)
            self.comboBox.setEnabled(False)
            self.warn_line.setEnabled(False)
            self.monitor.start(self.comboBox.currentText())
            Thread(
                target=self.setSpeed,
                daemon=True
                ).start()
            self.timer.start(1000)

    def stop(self):
        """
        停止检测
        """
        if not self.monitor.start_flag.is_set():
            self.monitor.stop()
            self.timer.stop()
            self.start_button.setEnabled(True)
            self.stop_button.setEnabled(False)
            self.comboBox.setEnabled(True)
            self.warn_line.setEnabled(True)

def start_monitor():
    """
    调用监测系统
    """
    app = QApplication()
    widget = QWidget()
    Ui_Form().setupUi(widget)
    widget.show()
    app.exec_()


if __name__ == "__main__":
    start_monitor()
