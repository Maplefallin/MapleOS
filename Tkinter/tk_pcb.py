from Modification.pcb_m import PCB,PCBManager
import tkinter as tk
from tkinter import ttk

class ProcessInfoWindow(tk.Toplevel):
    """显示进程详细信息和页表的窗口"""

    def __init__(self, pcb: PCB, parent=None):
        super().__init__(parent)
        self.pcb = pcb
        self.title(f"进程 {self.pcb.process_name} 信息")

        # 设置窗口大小和布局
        layout = tk.Frame(self)
        layout.pack(padx=10, pady=10, fill="both", expand=True)

        # PCB基本信息表格
        self.pcb_info_table = ttk.Treeview(layout, columns=("Field", "Value"), show="headings")
        self.pcb_info_table.heading("Field", text="字段")
        self.pcb_info_table.heading("Value", text="值")
        self.fill_basic_info()
        self.pcb_info_table.pack(padx=10, pady=10, fill="x")

        # 页表和指令集布局
        tables_layout = tk.Frame(layout)
        tables_layout.pack(padx=10, pady=10, fill="both", expand=True)

        # 页表信息表格
        self.page_table = ttk.Treeview(tables_layout, columns=("Page", "Frame", "Exist","Modification"), show="headings")
        self.page_table.heading("Page", text="页号")
        self.page_table.heading("Frame",text="页框号")
        self.page_table.heading("Exist", text="存在位")
        self.page_table.heading("Modification", text="修改位")
        self.fill_page_table()
        self.page_table.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        # 指令集信息表格
        self.instruction_table = ttk.Treeview(tables_layout, columns=("Operation", "Address"), show="headings")
        self.instruction_table.heading("Operation", text="操作")
        self.instruction_table.heading("Address", text="地址")
        self.fill_instruction_table()
        self.instruction_table.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        # 添加关闭按钮
        close_button = ttk.Button(layout, text="关闭", command=self.destroy)
        close_button.pack(pady=10)

        # 设置grid的权重
        tables_layout.columnconfigure(0, weight=1)
        tables_layout.columnconfigure(1, weight=1)

        # 调整列宽
        self.adjust_column_width()

    def adjust_column_width(self):
        """调整表格列的宽度"""
        self.page_table.column("Page", width=80, anchor="center")
        self.page_table.column("Frame", width=80, anchor="center")
        self.page_table.column("Exist", width=80, anchor="center")
        self.page_table.column("Modification", width=80, anchor="center")


        self.instruction_table.column("Operation", width=100, anchor="center")
        self.instruction_table.column("Address", width=120, anchor="center")

    def fill_basic_info(self):
        """填充 PCB 的基本信息表格"""
        basic_info = {
            "进程名称": self.pcb.process_name,
            "到达时间": self.pcb.arrive_time,
            "需求时间": self.pcb.need_time,
            "任务名称": self.pcb.task_name,
            "大小": self.pcb.size,
            "分配的页面数": self.pcb.page_count,
            "状态": self.pcb.status,
            "剩余执行时间": self.pcb.remaining_time
        }
        for field, value in basic_info.items():
            self.pcb_info_table.insert("", "end", values=(field, str(value)))

    def fill_page_table(self):
        """填充 PCB 的页表信息表格"""
        for item in self.pcb.page_table:
            self.page_table.insert("", "end", values=(item["page"], item["frame"], item["exist"],item["modification"]))

    def fill_instruction_table(self):
        """填充 PCB 的指令集信息表格"""
        for instruction in self.pcb.instructions:
            self.instruction_table.insert("", "end", values=(instruction["operation"], instruction["address"]))




class ProcessListWindow(tk.Frame):
    """显示所有进程的列表，点击某项显示进程的详细信息窗口"""

    def __init__(self, parent, pcb_manager: PCBManager):
        super().__init__(parent)
        self.pcb_manager = pcb_manager
        self.pack(padx=10, pady=10, fill="both", expand=True)

        # 添加“全部进程”标签
        self.title_label = tk.Label(self, text="全部进程", font=("Arial", 14, "bold"))
        self.title_label.pack(pady=(0, 10))  # 在标签下方加一点间距

        # 创建表格，显示进程列表
        self.process_table = ttk.Treeview(self, columns=("Process", "Start Time", "Remaining Time"), show="headings")

        # 设置表头
        self.process_table.heading("Process", text="进程")
        self.process_table.heading("Start Time", text="开始时间")
        self.process_table.heading("Remaining Time", text="剩余时间")

        # 设置列宽度
        self.process_table.column("Process", width=150, anchor="center", stretch=tk.NO)
        self.process_table.column("Start Time", width=100, anchor="center", stretch=tk.NO)
        self.process_table.column("Remaining Time", width=100, anchor="center", stretch=tk.NO)

        self.fill_process_list()  # 初始填充进程列表
        self.process_table.pack(padx=10, pady=10, fill="both", expand=True)

        # 为表格项添加点击事件
        self.process_table.bind("<ButtonRelease-1>", self.on_process_select)

        # 启动定时器，每秒刷新一次
        self.refresh_process_list()

    def fill_process_list(self):
        """填充进程列表表格"""
        # 清空现有的表格数据
        for row in self.process_table.get_children():
            self.process_table.delete(row)

        # 获取进程并填充表格
        for pcb in self.pcb_manager.processes:
            self.process_table.insert("", "end", values=(pcb.process_name, pcb.arrive_time, pcb.remaining_time))

    def refresh_process_list(self):
        """每秒刷新一次进程列表"""
        self.fill_process_list()  # 更新进程列表

        # 每1000ms（即1秒）再次调用 refresh_process_list
        self.after(1000, self.refresh_process_list)

    def on_process_select(self, event):
        """点击表格项，显示进程的详细信息窗口"""
        selected_item = self.process_table.selection()
        if selected_item:
            item_values = self.process_table.item(selected_item[0], "values")
            process_name = item_values[0]

            # 遍历所有进程列表，找到与进程名称匹配的 PCB 对象
            selected_pcb = None
            for pcb in self.pcb_manager.processes:
                if pcb.process_name == process_name:
                    selected_pcb = pcb
                    break

            if selected_pcb:
                ProcessInfoWindow(selected_pcb, self)

class PCBApp(tk.Tk):
    """主应用程序窗口"""

    def __init__(self):
        super().__init__()
        self.title("进程控制块展示")
        self.geometry("400x300")

        pcb1 = PCB("进程1", 0, 50, "任务A", 1000)
        pcb2 = PCB("进程2", 5, 30, "任务B", 800)

        # 创建 PCBManager 并添加进程
        self.pcb_manager = PCBManager()
        self.pcb_manager.processes.append(pcb1)
        self.pcb_manager.processes.append(pcb2)

        # 创建进程列表窗口并嵌入到主窗口
        self.process_list_window = ProcessListWindow(self, self.pcb_manager)


if __name__ == "__main__":
    app = PCBApp()
    app.mainloop()
