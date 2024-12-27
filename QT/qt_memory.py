import sys
import random
from collections import deque
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QSplitter, QHBoxLayout, \
    QLabel, QLineEdit, QFormLayout, QPushButton, QDialog, QScrollArea, QHeaderView
from PyQt5.QtCore import Qt, QTimer
from buffer import log, VIRTUAL_PAGES, PAGE_SIZE, MEMORY_BLOCKS, USABLE_BLOCKS
from Modification.memory_m import MemoryManager



class MemoryManagerGUI(QWidget):
    def __init__(self, memory_manager):
        super().__init__()
        self.memory_manager = memory_manager
        self.initUI()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.updateMemoryStatus)
        self.timer.start(1000)  # 每秒更新一次

    def initUI(self):
        self.setWindowTitle("内存管理器")
        self.setGeometry(400, 400, 800, 600)
        layout = QVBoxLayout(self)

        # 内存页表
        self.page_table = QTableWidget(self)
        self.page_table.setRowCount(MEMORY_BLOCKS)  # 显示完整的内存块列表
        self.page_table.setColumnCount(3)
        self.page_table.setHorizontalHeaderLabels(["物理块", "进程", "页面号"])
        self.page_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.page_table)

        # 内存栈
        self.memory_stack_table = QTableWidget(self)
        self.memory_stack_table.setRowCount(USABLE_BLOCKS)
        self.memory_stack_table.setColumnCount(2)
        self.memory_stack_table.setHorizontalHeaderLabels(["页面", "对应主存块"])
        self.memory_stack_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.memory_stack_table)

        # 滚动区域
        scroll_area = QScrollArea(self)
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(self.page_table)
        layout.addWidget(scroll_area)

        self.setLayout(layout)

    def updateMemoryStatus(self):
        """更新内存页表和内存栈的状态"""

        # 更新内存页表
        for i in range(MEMORY_BLOCKS):
            if i < MEMORY_BLOCKS - USABLE_BLOCKS:
                # 前 (MEMORY_BLOCKS - USABLE_BLOCKS) 个块显示固定内容
                process_name = "p10"
                page = i % 10
            else:
                # 后续块按照 memory_manager.memory 中的内容显示
                pcb = self.memory_manager.memory[i].get("pcb", None)
                page = self.memory_manager.memory[i].get("page", None)
                process_name = pcb.process_name if pcb else "None"

            self.page_table.setItem(i, 0, QTableWidgetItem(str(i)))  # 物理块
            self.page_table.setItem(i, 1, QTableWidgetItem(process_name))  # 进程
            self.page_table.setItem(i, 2, QTableWidgetItem(str(page)))  # 页面号

        # 更新内存栈
        for i in range(USABLE_BLOCKS):
            if not self.memory_manager.memory_stack:
                # 如果内存栈为空
                self.memory_stack_table.setItem(i, 0, QTableWidgetItem("None"))
                self.memory_stack_table.setItem(i, 1, QTableWidgetItem("None"))
            else:
                # 如果内存栈中存在内容
                if i < len(self.memory_manager.memory_stack):
                    item = self.memory_manager.memory_stack[i]
                    page = item.get("page", "None")
                    block = item.get("block", "None")
                else:
                    page = "None"
                    block = "None"

                self.memory_stack_table.setItem(i, 0, QTableWidgetItem(str(page)))
                self.memory_stack_table.setItem(i, 1, QTableWidgetItem(str(block)))



if __name__ == "__main__":
    app = QApplication(sys.argv)

    memory = MemoryManager()  # 创建 MemoryManager 实例
    window = MemoryManagerGUI(memory)  # 创建 GUI 窗口
    window.show()  # 显示窗口

    sys.exit(app.exec_())