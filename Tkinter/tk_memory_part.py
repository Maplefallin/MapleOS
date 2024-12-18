from memory import MemoryManager
import tkinter as tk
from tkinter import ttk

class MemoryVisualizer(tk.Frame):
    def __init__(self, parent, memory_manager, **kwargs):
        super().__init__(parent, **kwargs)

        # 将外部传入的 memory_manager 实例赋值给类属性
        self.memory_manager = memory_manager

        # 创建顶部框架用于显示bitmap
        self.top_frame = tk.Frame(self)
        self.top_frame.pack(fill=tk.X, padx=10, pady=10)

        # 创建顶部标题
        self.top_title = tk.Label(self.top_frame, text="主存图", font=("Arial", 14))
        self.top_title.pack(pady=7)  # 添加一些间距

        # 创建画布（用于显示bitmap）并加上滚动条
        self.canvas_frame = tk.Frame(self.top_frame)
        self.canvas_frame.pack(fill=tk.X, expand=True)

        self.canvas = tk.Canvas(self.canvas_frame)
        self.canvas.pack(side="left", fill=tk.BOTH, expand=True)

        # 创建垂直滚动条
        self.canvas_scroll = tk.Scrollbar(self.canvas_frame, orient="vertical", command=self.canvas.yview)
        self.canvas_scroll.pack(side="right", fill="y")
        self.canvas.configure(yscrollcommand=self.canvas_scroll.set)

        # 创建底部框架用于显示memory数据
        self.bottom_frame = tk.Frame(self)
        self.bottom_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 创建底部标题
        self.bottom_title = tk.Label(self.bottom_frame, text="主存块", font=("Arial", 14))
        self.bottom_title.pack(pady=7)  # 添加一些间距

        # Treeview显示memory内容
        self.tree = ttk.Treeview(self.bottom_frame, columns=("Block", "Page Frame"), show="headings", height=6)
        self.tree.heading("Block", text="Memory Block")
        self.tree.heading("Page Frame", text="Page Frame")
        self.tree.pack(fill=tk.BOTH, expand=True)

        # 调整Treeview列宽度
        self.tree.column("Block", width=120, anchor="center")
        self.tree.column("Page Frame", width=120, anchor="center")

        # 每秒更新显示
        self.after(1000, self.update_display)

        # 填充数据
        self.update_bitmap()
        self.update_memory_table()

    def update_bitmap(self):
        """更新bitmap的显示"""
        self.canvas.delete("all")  # 清空画布
        size = 30  # 每个小块的尺寸
        rows = (len(self.memory_manager.bitmap) + 7) // 8  # 计算总行数
        canvas_width = self.canvas.winfo_width()  # 获取画布的宽度
        canvas_height = self.canvas.winfo_height()  # 获取画布的高度

        self.canvas.config(scrollregion=(0, 0, canvas_width, size * rows))

        for i, bit in enumerate(self.memory_manager.bitmap):
            x = (i % 8) * (size + 5)
            y = (i // 8) * (size + 5)
            color = "green" if bit == 0 else "red"
            self.canvas.create_rectangle(x, y, x + size, y + size, fill=color)

    def update_memory_table(self):
        """更新memory表格"""
        for row in self.tree.get_children():
            self.tree.delete(row)  # 清空现有表格
        for i, page_frame in enumerate(self.memory_manager.memory):
            self.tree.insert("", "end", values=(i, page_frame))

    def update_display(self):
        """每秒清空画布和表格，重新遍历"""
        self.update_bitmap()
        self.update_memory_table()

        # 再次设置定时更新
        self.after(1000, self.update_display)

# 主窗口
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Memory Visualizer")
    root.geometry("300x700")  # 设置主窗口的大小

    # 实例化 MemoryManager
    memory_manager = MemoryManager()

    # 创建并显示 MemoryVisualizer
    app = MemoryVisualizer(root, memory_manager)
    app.pack(fill=tk.BOTH, expand=True)

    # 启动主事件循环
    root.mainloop()