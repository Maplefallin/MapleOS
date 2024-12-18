import sys
import random
from collections import deque
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QSplitter, QHBoxLayout, \
    QLabel, QLineEdit, QFormLayout, QPushButton, QDialog, QScrollArea, QHeaderView
from PyQt5.QtCore import Qt, QTimer
from buffer import log, VIRTUAL_PAGES, PAGE_SIZE,MEMORY_BLOCKS
from memory import MemoryManager


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
        self.page_table.setRowCount(VIRTUAL_PAGES)
        self.page_table.setColumnCount(3)
        self.page_table.setHorizontalHeaderLabels(["页框号", "状态", "块号"])
        self.page_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.page_table)

        # 内存栈
        self.memory_stack_table = QTableWidget(self)
        self.memory_stack_table.setRowCount(MEMORY_BLOCKS)
        self.memory_stack_table.setColumnCount(2)
        self.memory_stack_table.setHorizontalHeaderLabels(["块号", "使用状态"])
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
        for i in range(VIRTUAL_PAGES):
            self.page_table.setItem(i, 0, QTableWidgetItem(str(i)))
            self.page_table.setItem(i, 1, QTableWidgetItem(self.memory_manager.page_table[i]["valid"]))
            self.page_table.setItem(i, 2, QTableWidgetItem(str(self.memory_manager.page_table[i]["block"])))

        for i in range(MEMORY_BLOCKS):
            self.memory_stack_table.setItem(i, 0, QTableWidgetItem(str(i)))
            self.memory_stack_table.setItem(i, 1, QTableWidgetItem("使用" if self.memory_manager.bitmap[i] else "空闲"))


