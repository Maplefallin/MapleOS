import sys

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QSplitter, QApplication
from PyQt5.QtCore import Qt
from scheduler import Scheduler
from pcb import PCBManager
from memory import MemoryManager
from QT import LogTextEdit
from QT import SchedulerGUI
from QT import MemoryManagerGUI

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        # 创建 PCBManager 和 MemoryManager 实例
        self.pcb_manager = PCBManager()
        self.memory_manager = MemoryManager()

        # 创建 Scheduler 实例
        self.scheduler = Scheduler(self.pcb_manager, self.memory_manager)

        # 创建各个组件
        self.scheduler_gui = SchedulerGUI(self.scheduler)
        self.log_text = LogTextEdit()
        self.memory_gui = MemoryManagerGUI(self.memory_manager)

        # 初始化主窗口
        self.initUI()

    def initUI(self):

        print("初始化对象")
        # 主窗口的布局
        main_layout = QHBoxLayout(self)

        # 创建分割器，调度组件在左，日志和内存组件在右
        splitter = QSplitter(Qt.Horizontal)

        # 将调度组件添加到左侧
        splitter.addWidget(self.scheduler_gui)

        # 创建右侧的垂直布局，包含日志和内存管理
        right_layout = QVBoxLayout()
        right_layout.addWidget(self.log_text)
        right_layout.addWidget(self.memory_gui)

        # 创建右侧窗口，并添加布局
        right_widget = QWidget()
        right_widget.setLayout(right_layout)

        # 将右侧窗口添加到分割器中
        splitter.addWidget(right_widget)

        # 将分割器添加到主布局中
        main_layout.addWidget(splitter)

        # 设置窗口布局
        self.setLayout(main_layout)

        # 设置窗口标题和大小
        self.setWindowTitle("主窗口")
        self.setGeometry(400, 400, 1000, 800)

        # 设置分割器的初始比例
        splitter.setSizes([300, 700])  # 左侧300，右侧700



app = QApplication(sys.argv)
window = MainWindow()
window.show()
sys.exit(app.exec_())