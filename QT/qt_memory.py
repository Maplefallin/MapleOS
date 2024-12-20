import sys
import random
from collections import deque
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QSplitter, QHBoxLayout, \
    QLabel, QLineEdit, QFormLayout, QPushButton, QDialog, QScrollArea, QHeaderView
from PyQt5.QtCore import Qt, QTimer
from buffer import log, VIRTUAL_PAGES, PAGE_SIZE, MEMORY_BLOCKS, USABLE_BLOCKS
from memory import MemoryManager


class MemoryManager:
    def __init__(self):
        # 初始化 page_table
        self.page_table = [
            {"valid": "empty", "block": -1, "used": 0} if i < VIRTUAL_PAGES // 2
            else {"valid": "full", "block": -1, "used": 1024}
            for i in range(VIRTUAL_PAGES)
        ]

        # 初始化 memory
        self.memory = [{"pcb": None, "page": -1}] * USABLE_BLOCKS  # 前 USABLE_BLOCKS 个块为空
        self.memory.extend([{"pcb": None, "page": 1}] * (MEMORY_BLOCKS - USABLE_BLOCKS))  # 剩余块已满

        # 虚拟内存（只是一个示例）
        self.virtual_memory = [f"Page {i} empty" for i in range(VIRTUAL_PAGES)]

        # 位图表示内存是否已满
        self.bitmap = [0] * USABLE_BLOCKS + [1] * (MEMORY_BLOCKS - USABLE_BLOCKS)

        # 初始化内存栈
        self.memory_stack = deque()


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
        self.page_table.setRowCount(USABLE_BLOCKS)  # 使用 VIRTUAL_PAGES 来设定页表行数
        self.page_table.setColumnCount(3)
        self.page_table.setHorizontalHeaderLabels(["物理块","进程", "页面号"])
        self.page_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.page_table)

        # 内存栈
        self.memory_stack_table = QTableWidget(self)
        self.memory_stack_table.setRowCount(USABLE_BLOCKS)  # 使用 MEMORY_BLOCKS 来设定内存栈行数
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
        for i in range(USABLE_BLOCKS):
            # Ensure that memory[i] is properly initialized and contains necessary keys.
            pcb = self.memory_manager.memory[i].get("pcb", None)
            page = self.memory_manager.memory[i].get("page", None)

            # If there is a PCB, use its process_name; otherwise, display 'None'
            process_name = pcb.process_name if pcb else 'None'

            # Set the values in the page table
            self.page_table.setItem(i, 0, QTableWidgetItem(str(i)))  # 页框号
            self.page_table.setItem(i, 1, QTableWidgetItem(process_name))  # 进程
            self.page_table.setItem(i, 2, QTableWidgetItem(str(page)))  # 页面

        # 更新内存栈
        for i in range(USABLE_BLOCKS):
            # 先检查 memory 是否为空
            if not self.memory_manager.memory:
                self.memory_stack_table.setItem(i, 0, QTableWidgetItem("None"))  # 显示 None
                self.memory_stack_table.setItem(i, 1, QTableWidgetItem("None"))  # 显示 None
            else:
                # 如果 memory 不为空，则展示 memory_stack 中的内容
                page = self.memory_manager.memory[i].get("page", "None")
                block = self.memory_manager.memory[i].get("block", "None")

                # 设置内存栈表格的显示项
                self.memory_stack_table.setItem(i, 0, QTableWidgetItem(str(page)))  # 页面
                self.memory_stack_table.setItem(i, 1, QTableWidgetItem(str(block)))  # 对应主存块

                # 如果 memory_stack 中存在内容，遍历并显示
                if len(self.memory_manager.memory_stack) > 0:
                    for j, item in enumerate(self.memory_manager.memory_stack):
                        self.memory_stack_table.setItem(j, 0, QTableWidgetItem(str(item.get("page", "None"))))
                        self.memory_stack_table.setItem(j, 1, QTableWidgetItem(str(item.get("block", "None"))))


if __name__ == "__main__":
    app = QApplication(sys.argv)

    memory = MemoryManager()  # 创建 MemoryManager 实例
    window = MemoryManagerGUI(memory)  # 创建 GUI 窗口
    window.show()  # 显示窗口

    sys.exit(app.exec_())
