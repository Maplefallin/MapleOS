import tkinter as tk
from tkinter import ttk
from buffer import USABLE_BLOCKS
from memory import MemoryManager


class MemoryViewer(tk.Frame):
    def __init__(self, master, memory_manager):
        super().__init__(master)
        self.memory_manager = memory_manager
        self.pack(fill=tk.BOTH, expand=True)

        # Create a frame for the left section (Page Table, Memory Stack, and Canvas)
        self.left_frame = tk.Frame(self)
        self.left_frame.pack(fill=tk.BOTH, expand=True)

        # Create Canvas for displaying bitmap (place above or below the tables)
        self.canvas_frame = tk.Frame(self.left_frame)
        self.canvas_frame.pack(fill=tk.X, expand=True, pady=20)

        self.canvas = tk.Canvas(self.canvas_frame)
        self.canvas.pack(side="left", fill=tk.BOTH, expand=True)

        # Create vertical scrollbar for the canvas
        self.canvas_scroll = tk.Scrollbar(self.canvas_frame, orient="vertical", command=self.canvas.yview)
        self.canvas_scroll.pack(side="right", fill="y")
        self.canvas.configure(yscrollcommand=self.canvas_scroll.set)

        # Page Table Section
        self.page_table_frame = tk.Frame(self.left_frame)
        self.page_table_frame.pack(pady=20, padx=10, fill=tk.BOTH, expand=True)

        self.page_table_label = tk.Label(self.page_table_frame, text="主存", font=("Arial", 14))
        self.page_table_label.pack(pady=10)

        self.page_table_tree = ttk.Treeview(self.page_table_frame, columns=("Physical Block", "Process", "Page Number"), show="headings")
        self.page_table_tree.heading("Physical Block", text="Physical Block")
        self.page_table_tree.heading("Process", text="Process")
        self.page_table_tree.heading("Page Number", text="Page Number")

        self.page_table_tree.column("Physical Block", width=100, anchor=tk.CENTER)
        self.page_table_tree.column("Process", width=100, anchor=tk.CENTER)
        self.page_table_tree.column("Page Number", width=100, anchor=tk.CENTER)

        self.page_table_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Memory Stack Section
        self.memory_stack_frame = tk.Frame(self.left_frame)
        self.memory_stack_frame.pack(pady=20, padx=10, fill=tk.BOTH, expand=True)

        self.memory_stack_label = tk.Label(self.memory_stack_frame, text="主存栈", font=("Arial", 14))
        self.memory_stack_label.pack(pady=10)

        self.memory_stack_tree = ttk.Treeview(self.memory_stack_frame, columns=("Block Number", "Page Number"), show="headings")
        self.memory_stack_tree.heading("Block Number", text="Block Number")
        self.memory_stack_tree.heading("Page Number", text="Page Number")

        self.memory_stack_tree.column("Block Number", width=100, anchor=tk.CENTER)
        self.memory_stack_tree.column("Page Number", width=100, anchor=tk.CENTER)

        self.memory_stack_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Start listening for updates
        self.listen_updates()


    def listen_updates(self):
        """Listen for memory updates every second"""
        self.update_display()  # Update the UI display
        self.after(1000, self.listen_updates)  # Re-run every second

    def update_display(self):
        """Update the page table and memory stack display"""
        # Update Page Table display
        for row in self.page_table_tree.get_children():
            self.page_table_tree.delete(row)

        for i, entry in enumerate(self.memory_manager.memory[:USABLE_BLOCKS]):
            process_name = entry["pcb"].process_name if entry["pcb"] else "Empty"

            self.page_table_tree.insert("", "end", values=(i, process_name, entry["page"]))

        # Update Memory Stack display
        for row in self.memory_stack_tree.get_children():
            self.memory_stack_tree.delete(row)

        for page_num in self.memory_manager.memory_stack:
            self.memory_stack_tree.insert("", "end", values=(page_num["block"], page_num["page"]))

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
