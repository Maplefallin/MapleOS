import tkinter as tk
from tkinter import ttk

from Tkinter.tk_memory_part import MemoryVisualizer
from memory import MemoryManager


class MemoryViewer(tk.Frame):
    def __init__(self, master, memory_manager):
        super().__init__(master)
        self.memory_manager = memory_manager
        self.pack(fill=tk.BOTH, expand=True)

        # 创建一个PanedWindow用于分割左侧和右侧
        self.paned_window = tk.PanedWindow(self, orient=tk.HORIZONTAL)
        self.paned_window.pack(fill=tk.BOTH, expand=True)

        # 左侧部分：页表和主存栈
        self.left_frame = tk.Frame(self.paned_window)
        self.left_frame.pack(fill=tk.BOTH, expand=True)

        # 创建一个Frame用于页表部分
        self.page_table_frame = tk.Frame(self.left_frame)
        self.page_table_frame.pack(pady=20, padx=10, fill=tk.BOTH, expand=True)

        self.page_table_label = tk.Label(self.page_table_frame, text="页框表", font=("Arial", 14))
        self.page_table_label.pack(pady=10)

        # 创建一个Treeview表格显示页表
        self.page_table_tree = ttk.Treeview(self.page_table_frame, columns=("页框号", "状态", "物理块"), show="headings")
        self.page_table_tree.heading("页框号", text="页框号")
        self.page_table_tree.heading("状态", text="状态")
        self.page_table_tree.heading("物理块", text="物理块")

        self.page_table_tree.column("页框号", width=100, anchor=tk.CENTER)
        self.page_table_tree.column("状态", width=100, anchor=tk.CENTER)
        self.page_table_tree.column("物理块", width=100, anchor=tk.CENTER)

        self.page_table_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # 创建一个Frame用于主存栈部分
        self.memory_stack_frame = tk.Frame(self.left_frame)
        self.memory_stack_frame.pack(pady=20, padx=10, fill=tk.BOTH, expand=True)

        self.memory_stack_label = tk.Label(self.memory_stack_frame, text="已经载入内存的页面", font=("Arial", 14))
        self.memory_stack_label.pack(pady=10)

        # 创建一个Treeview表格显示主存栈
        self.memory_stack_tree = ttk.Treeview(self.memory_stack_frame, columns=("主存页号"), show="headings")
        self.memory_stack_tree.heading("主存页号", text="主存页号")

        self.memory_stack_tree.column("主存页号", width=120, anchor=tk.CENTER)

        self.memory_stack_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # 右侧部分：MemoryVisualizer
        self.memory_visualizer = MemoryVisualizer(self.paned_window, self.memory_manager)
        self.memory_visualizer.pack(fill=tk.BOTH, expand=True)

        # 将左侧和右侧框架添加到PanedWindow
        self.paned_window.add(self.left_frame)
        self.paned_window.add(self.memory_visualizer)

        # 启动监听，定期每秒更新显示
        self.listen_updates()

    def listen_updates(self):
        """每秒监听一次内存更新"""
        self.update_display()  # 更新界面显示
        self.after(1000, self.listen_updates)  # 每秒钟再次调用监听

    def update_display(self):
        """更新页表和内存栈的展示"""
        # 更新页表展示
        for row in self.page_table_tree.get_children():
            self.page_table_tree.delete(row)

        for i, entry in enumerate(self.memory_manager.page_table):
            self.page_table_tree.insert("", "end", values=(i, entry['valid'], entry['block']))

        # 更新主存栈展示
        for row in self.memory_stack_tree.get_children():
            self.memory_stack_tree.delete(row)

        for page_num in self.memory_manager.memory_stack:
            self.memory_stack_tree.insert("", "end", values=(page_num,))


# 主窗口
class MainWindow(tk.Tk):
    def __init__(self, memory_manager):
        super().__init__()
        self.title("内存展示器")
        self.geometry("700x500")

        # 创建MemoryViewer作为主窗口的子组件
        self.memory_viewer = MemoryViewer(self, memory_manager)
        self.memory_viewer.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)


if __name__ == "__main__":
    memory_manager = MemoryManager()
    # 启动主窗口
    app = MainWindow(memory_manager)
    app.mainloop()
