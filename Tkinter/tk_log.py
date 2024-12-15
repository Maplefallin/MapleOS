import tkinter as tk
import random
import time
import threading
from buffer import log

# 创建日志查看器，继承自tk.Frame，用于嵌入主窗口
class LogViewer(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # 添加一个居中的标题
        self.title_label = tk.Label(self, text="日志查看器", font=("Arial", 16))
        self.title_label.pack(pady=10, anchor='center', padx=10)

        # 创建一个文本框，设置为只读
        self.text_box = tk.Text(self, wrap=tk.WORD, height=15, width=60)
        self.text_box.pack(pady=10, fill=tk.BOTH, expand=True)  # 使文本框自适应父容器大小
        self.text_box.config(state=tk.DISABLED)  # 禁止编辑

        # 启动监听日志更新
        self.check_log()

    def check_log(self):
        """每秒检查日志是否更新"""
        if len(log) > 0:
            self.update_log_output()
        # 每隔1000ms（1秒）再次调用check_log
        self.after(1000, self.check_log)

    def update_log_output(self):
        """清空文本框并重新显示日志内容"""
        self.text_box.config(state=tk.NORMAL)  # 允许编辑
        self.text_box.delete(1.0, tk.END)  # 清空文本框
        for line in log:
            self.text_box.insert(tk.END, line + "\n")  # 重新插入日志内容
        self.text_box.config(state=tk.DISABLED)  # 禁止编辑

        # 滚动到文本框的底部
        self.text_box.yview(tk.END)


# 主窗口
class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("主窗口")
        self.geometry("600x400")

        # 创建LogViewer作为主窗口的子组件
        self.log_viewer = LogViewer(self)
        self.log_viewer.pack(fill=tk.BOTH, expand=True)

if __name__ == "__main__":
    # 模拟日志更新的函数
    def simulate_log_updates():
        """模拟每3秒更新一次日志"""
        while True:
            # 模拟一些随机的日志消息
            new_log = f"新日志条目：{random.choice(['成功', '失败', '警告', '信息'])} - {time.strftime('%Y-%m-%d %H:%M:%S')}"
            log.append(new_log)
            time.sleep(3)  # 每3秒钟更新一次

    # 启动模拟日志更新线程
    log_thread = threading.Thread(target=simulate_log_updates, daemon=True)
    log_thread.start()

    # 创建主窗口并启动应用
    app = MainWindow()
    app.mainloop()
