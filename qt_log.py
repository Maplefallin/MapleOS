import sys
import random
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QTextEdit
from PyQt5.QtCore import QTimer, Qt
from typing import List
from buffer import log  # 确保buffer.py中有一个名为log的列表

class LogTextEdit(QTextEdit):
    """自定义的日志文本编辑器，继承自 QTextEdit"""
    def __init__(self):
        super().__init__()
        self.setReadOnly(True)  # 只读模式，不能编辑
        self.setStyleSheet("background-color: #f0f0f0; font-size: 12px;")

        # 启动一个定时器，定期检查log是否更新
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_log)
        self.timer.start(1000)  # 每秒钟检查一次

        # 存储上一次的日志内容
        self.last_log_content = ""

    def update_log(self):
        """更新日志显示框"""
        current_log_content = "\n".join(log)  # 获取当前所有日志内容
        if current_log_content != self.last_log_content:  # 检查是否有更新
            # 更新上一次的日志内容
            self.last_log_content = current_log_content
            # 清空当前文本框内容
            self.clear()
            # 将所有日志内容添加到 QTextEdit 中
            self.append(current_log_content)
            # 自动滚动到文本框的底部
            self.moveCursor(self.textCursor().End)

    def add_log(self, message: str):
        """添加一条日志到日志列表"""
        log.append(message)

# 确保你的buffer.py文件中的log是一个列表，例如：
# log = []