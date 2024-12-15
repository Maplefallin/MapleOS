import tkinter as tk
from tkinter import messagebox,ttk
from scheduler import Scheduler
from memory import MemoryManager
from pcb import PCB,PCBManager


class ProcessDialog(tk.Toplevel):
    """弹出框用于输入新进程的参数"""
    def __init__(self, scheduler, parent=None):
        super().__init__(parent)
        self.geometry("300x250")  # 增加高度使得布局更舒适
        self.scheduler = scheduler  # 接收 Scheduler 实例

        # 创建一个框架用于存放所有的输入框和标签
        frame = tk.Frame(self)
        frame.pack(pady=20)  # 增加顶部的间距

        # 创建输入框
        tk.Label(frame, text="进程名称:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        self.process_name_input = tk.Entry(frame)
        self.process_name_input.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(frame, text="到达时间:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        self.arrive_time_input = tk.Entry(frame)
        self.arrive_time_input.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(frame, text="需要时间:").grid(row=2, column=0, sticky="e", padx=5, pady=5)
        self.need_time_input = tk.Entry(frame)
        self.need_time_input.grid(row=2, column=1, padx=5, pady=5)

        tk.Label(frame, text="任务名称:").grid(row=3, column=0, sticky="e", padx=5, pady=5)
        self.task_name_input = tk.Entry(frame)
        self.task_name_input.grid(row=3, column=1, padx=5, pady=5)

        tk.Label(frame, text="内存大小:").grid(row=4, column=0, sticky="e", padx=5, pady=5)
        self.size_input = tk.Entry(frame)
        self.size_input.grid(row=4, column=1, padx=5, pady=5)

        # 创建确认按钮并放置在输入框下方
        confirm_button = tk.Button(self, text="完成",width=10, command=self.on_confirm)
        confirm_button.pack(pady=15)  # 增加按钮与输入框之间的距离

    def on_confirm(self):
        """确认按钮点击事件"""
        try:
            process_name = self.process_name_input.get()
            arrive_time = int(self.arrive_time_input.get())
            need_time = int(self.need_time_input.get())
            task_name = self.task_name_input.get()
            size = int(self.size_input.get())

            # 创建进程
            pcb = self.scheduler.create_process(process_name, arrive_time, need_time, task_name, size,self.scheduler.memory_manager)
            if pcb:
                messagebox.showinfo("进程创建", f"进程 {pcb.process_name} 被创建并加入调度")
                self.destroy()  # 关闭弹窗
        except Exception as e:
            messagebox.showerror("错误", f"创建进程时出错: {e}")


class SchedulerGUI(tk.Frame):
    def __init__(self, parent, scheduler):
        super().__init__(parent)  # 继承自 Frame 类并传递父组件
        self.scheduler = scheduler  # 接收外部传入的 Scheduler 实例
        self.initUI()

    def initUI(self):
        # self.title('进程调度器')
        # self.geometry('800x800')

        # 创建主布局
        layout = tk.Frame(self)
        layout.pack(fill="both", expand=True, padx=20, pady=20)

        # 添加进程和调度按钮
        button_layout = tk.Frame(layout)
        self.add_process_button = tk.Button(button_layout, text='添加进程', width=15, command=self.show_process_dialog)
        self.add_process_button.pack(side="left", padx=10)

        self.schedule_button = tk.Button(button_layout, text='调度', width=15, command=self.schedule_process)
        self.schedule_button.pack(side="left", padx=10)

        button_layout.pack(pady=10)

        # 创建显示反馈队列
        queue_layout = tk.Frame(layout)
        queue_layout.pack(fill="both", expand=True)

        self.feedback_list_widgets = []
        for i in range(len(self.scheduler.feedback_queues)):  # 根据反馈队列数量创建
            label = tk.Label(queue_layout, text=f"队列{i + 1}(时间片为 {self.scheduler.time_slices[i]})")
            label.grid(row=0, column=i, padx=10, pady=10)
            treeview = ttk.Treeview(queue_layout, columns=("Process", "Remaining Time"), show="headings")
            treeview.heading("Process", text="进程名称")
            treeview.heading("Remaining Time", text="剩余时间")
            treeview.column("Process", width=120)  # 设置进程名称列宽度
            treeview.column("Remaining Time", width=80)  # 设置剩余时间列宽度
            treeview.grid(row=1, column=i, padx=10, pady=10)
            self.feedback_list_widgets.append(treeview)

        # 阻塞队列和完成队列
        block_layout = tk.Frame(layout)
        block_layout.pack(fill="both", expand=True, pady=20)

        # 使用一个容器布局来居中标签和对应的队列
        block_and_finished_layout = tk.Frame(block_layout)
        block_and_finished_layout.pack(side="top", fill="both", expand=True)

        # 阻塞队列标签和队列
        block_container = tk.Frame(block_and_finished_layout)
        block_container.pack(side="left", padx=10, pady=10, expand=True)

        block_label = tk.Label(block_container, text="阻塞队列", font=("Arial", 12))
        block_label.pack(side="top", pady=5)
        self.block_widget = ttk.Treeview(block_container, columns=("Process", "Remaining Time"), show="headings")
        self.block_widget.heading("Process", text="进程名称")
        self.block_widget.heading("Remaining Time", text="剩余时间")
        self.block_widget.column("Process", width=120)  # 设置进程名称列宽度
        self.block_widget.column("Remaining Time", width=80)  # 设置剩余时间列宽度
        self.block_widget.pack(side="top", padx=10, pady=10)

        # 完成队列标签和队列
        finished_container = tk.Frame(block_and_finished_layout)
        finished_container.pack(side="right", padx=10, pady=10, expand=True)

        finished_label = tk.Label(finished_container, text="完成队列", font=("Arial", 12))
        finished_label.pack(side="top", pady=5)
        self.finished_widget = ttk.Treeview(finished_container, columns=("Process", "Remaining Time"), show="headings")
        self.finished_widget.heading("Process", text="进程名称")
        self.finished_widget.heading("Remaining Time", text="剩余时间")
        self.finished_widget.column("Process", width=120)  # 设置进程名称列宽度
        self.finished_widget.column("Remaining Time", width=80)  # 设置剩余时间列宽度
        self.finished_widget.pack(side="top", padx=10, pady=10)

        # 定时器，用于每隔1秒刷新队列
        self.after(1000, self.update_queues)

    def show_process_dialog(self):
        """显示添加进程的弹框"""
        dialog = ProcessDialog(self.scheduler, self)
        dialog.grab_set()  # 确保模态窗口
        self.wait_window(dialog)  # 等待窗口关闭
        self.update_queues()

    def schedule_process(self):
        """开始调度进程"""
        try:
            self.scheduler.schedule()
            self.update_queues()
        except Exception as e:
            messagebox.showerror("调度错误", f"调度时出错: {e}")

    def update_queues(self):
        """更新队列的显示"""
        try:
            # 清空所有队列数据
            for treeview in self.feedback_list_widgets:
                for item in treeview.get_children():
                    treeview.delete(item)
            self.block_widget.delete(*self.block_widget.get_children())
            self.finished_widget.delete(*self.finished_widget.get_children())

            # 更新反馈队列
            for i, queue_widget in enumerate(self.feedback_list_widgets):
                queue = self.scheduler.feedback_queues[i]  # 直接获取 Scheduler 中的队列
                for pcb in queue:
                    queue_widget.insert("", "end", values=(pcb.process_name, pcb.remaining_time))

            # 更新阻塞队列
            for pcb in self.scheduler.block_queues:
                self.block_widget.insert("", "end", values=(pcb['pcb'].process_name, pcb['pcb'].remaining_time))

            # 更新完成队列
            for pcb in self.scheduler.finished_queues:
                self.finished_widget.insert("", "end", values=(pcb.process_name, pcb.remaining_time))

        except Exception as e:
            print(f"Error updating queues: {e}")




if __name__ == "__main__":
    pcb_manager = PCBManager()
    memory = MemoryManager()
    scheduler = Scheduler(memory_manager=memory,pcb_manager=pcb_manager)
    app = SchedulerGUI(scheduler)
    app.mainloop()
