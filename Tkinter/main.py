import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

from memory import MemoryManager
# 引用其他组件类
from pcb import PCB, PCBManager
from scheduler import Scheduler
from tk_pcb import ProcessListWindow
from tk_memory import MemoryViewer
from tk_scheduler import SchedulerGUI
from tk_log import LogViewer


class MainWindow(tk.Tk):
    """主应用程序窗口，包含所有子组件"""

    def __init__(self):
        super().__init__()
        self.title("系统控制面板")
        self.geometry("1200x800")  # 设置合适的窗口大小

        # 创建 PCBManager 并添加进程
        pcb1 = PCB("进程1", 0, 50, "任务A", 1000)
        pcb2 = PCB("进程2", 5, 30, "任务B", 800)
        self.pcb_manager = PCBManager()
        self.memory = MemoryManager()
        self.scheduler = Scheduler(memory_manager=self.memory, pcb_manager=self.pcb_manager)

        # 创建组件
        self.create_widgets()

    def create_widgets(self):
        """创建和布局所有子组件"""
        main_layout = tk.Frame(self)
        main_layout.pack(fill=tk.BOTH, expand=True)

        # 使用三个子布局分别表示左、中、右区域
        left_layout = tk.Frame(main_layout)
        left_layout.pack(side="left", fill=tk.BOTH, expand=True, padx=10, pady=10)

        center_layout = tk.Frame(main_layout)
        center_layout.pack(side="left", fill=tk.BOTH, expand=True, padx=10, pady=10)

        right_layout = tk.Frame(main_layout)
        right_layout.pack(side="left", fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 左侧：PCB进程列表窗口
        self.process_list_window = ProcessListWindow(left_layout, self.pcb_manager)
        self.process_list_window.pack(fill=tk.BOTH, expand=True)

        # 左侧：日志查看器窗口
        self.log_viewer = LogViewer(left_layout)
        self.log_viewer.pack(fill=tk.BOTH, expand=True, pady=20)

        # 中间：调度器GUI
        scheduler_gui = SchedulerGUI(center_layout, self.scheduler)  # 将中间布局传递给 SchedulerGUI
        scheduler_gui.pack(fill="both", expand=True)

        # 右侧：内存视图
        self.memory_viewer = MemoryViewer(right_layout, self.memory)
        self.memory_viewer.pack(fill=tk.BOTH, expand=True)


if __name__ == "__main__":
    app = MainWindow()
    app.mainloop()
