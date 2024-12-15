import tkinter as tk
from tkinter import scrolledtext
import random
import sys
from buffer import log  # 确保buffer.py中有一个名为log的列表

class LogTextEdit(scrolledtext.ScrolledText):
    """自定义的日志文本编辑器，继承自 scrolledtext.ScrolledText"""

    def __init__(self, master=None):
        super().__init__(master, state='disabled')  # 只读模式，不能编辑

        # 设置字体大小
        self.font = ("Helvetica", 10)
        self.configure(font=self.font)

        # 设置背景颜色
        self.configure(bg='#f0f0f0')

        # 启动一个定时器，定期检查log是否更新
        self.update_log()

    def update_log(self):
        """更新日志显示框"""
        current_log_content = "\n".join(log)  # 获取当前所有日志内容
        # 清空当前文本框内容
        self.delete(1.0, tk.END)
        # 将所有日志内容添加到 scrolledtext.ScrolledText 中
        self.insert(tk.END, current_log_content)
        # 自动滚动到文本框的底部
        self.see(tk.END)
        # 每秒钟检查一次
        self.after(1000, self.update_log)

    def add_log(self, message: str):
        """添加一条日志到日志列表"""
        log.append(message)

# 确保你的buffer.py文件中的log是一个列表，例如：
# log = []

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Log Viewer")

    log_text = LogTextEdit(root)
    log_text.pack(fill=tk.BOTH, expand=True)

    # 模拟日志添加
    def simulate_log_addition():
        log_text.add_log(f"Log entry {random.randint(1, 100)} at {random.randint(1, 60)}s")
        random_delay = random.randint(1, 3) * 1000  # 随机延迟1到3秒
        root.after(random_delay, simulate_log_addition)

    # 启动日志模拟
    simulate_log_addition()

    root.mainloop()