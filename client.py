import  random
from typing import List
from prettytable import PrettyTable
from pcb import PCBManager,PCB
from scheduler import Scheduler
from buffer import PAGE_SIZE,VIRTUAL_PAGES,PHYSICAL_BLOCKS

class Client:
    """与用户交互的客户端"""
    def __init__(self, pcb_manager: PCBManager, memory_manager,scheduler:Scheduler):
        self.pcb_manager = pcb_manager
        self.memory_manager = memory_manager
        self.scheduler = scheduler

    def display_ready_processes(self):
        """为每个队列等级显示进程信息"""
        table = PrettyTable()
        table.field_names = ["队列名", "进程名", "到达时间", "需求时间", "剩余时间", "状态", "起始页号", "页数"]
        table.add_row(["", "", "", "", "", "", "", ""])
        # 遍历多级反馈队列
        for level, queue in enumerate(self.scheduler.feedback_queues):
            table.add_row(["-", "-", "-", "-", "-", "-", "-", "-"])
            for pcb in queue:
                table.add_row([
                    "队列" + str(level),  # 队列名为空，因为已经在标题行显示
                    pcb.process_name,
                    pcb.arrive_time,
                    pcb.need_time,
                    pcb.remaining_time,
                    pcb.status,
                    pcb.begin,
                    pcb.page_count
                ])

        print(f"\n多级反馈队列队列 的进程信息:")
        print(table)

    def display_block_processes(self):
        # 创建一个表格对象
        table = PrettyTable()
        # 设置表格的列名
        table.field_names = ["队列名", "进程名", "等待时间", "下一级队列", "需要时间", "剩余时间", "状态"]
        # 遍历阻塞队列中的每个进程控制块（PCB）
        for pcb in self.scheduler.block_queues:
            # 向表格中添加一行数据
            table.add_row([
                "阻塞队列",  # 队列名
                pcb["pcb"].process_name,  # 进程名
                pcb["wait"],  # 等待时间
                pcb["next_level"],  # 下一级队列
                pcb["pcb"].need_time,  # 需要时间
                pcb["pcb"].remaining_time,  # 剩余时间
                pcb["pcb"].status  # 状态
            ])
        # 打印表格
        print(f"\n阻塞队列的进程信息:")
        print(table)

    def display_finished_processes(self):
        # 创建一个表格对象
        table = PrettyTable()
        # 设置表格的列名
        table.field_names = ["队列名", "进程名", "状态"]
        # 遍历阻塞队列中的每个进程控制块（PCB）
        for pcb in self.scheduler.finished_queues:
            # 向表格中添加一行数据
            table.add_row([
                "已完成",  # 队列名
                pcb.process_name,  # 进程名
                pcb.status  # 状态
            ])
        # 打印表格
        print(f"\n已完成的进程信息:")
        print(table)

    def display_page_tables(self):
        """显示每个进程的页表"""
        for pcb in self.pcb_manager.processes:
            table = PrettyTable()
            table.field_names = ["页号", "起始地址", "分配大小"]
            for page in pcb.page_table:
                table.add_row(page)
            print(f"\n进程 {pcb.process_name} 的页表:")
            print(table)

    def display_queues(self):
        """显示队列状态"""
        table = PrettyTable()
        table.field_names = ["队列名", "进程数量", "进程列表"]
        table.add_row(["就绪队列", len(self.pcb_manager.ready_queue), [pcb.process_name for pcb in self.pcb_manager.ready_queue]])
        table.add_row(["阻塞队列", len(self.pcb_manager.blocked_queue), [pcb.process_name for pcb in self.pcb_manager.blocked_queue]])
        table.add_row(["运行队列", 1 if self.pcb_manager.running_process else 0,
                       [self.pcb_manager.running_process.process_name] if self.pcb_manager.running_process else []])
        print("\n队列状态:")
        print(table)

    def display_bitmap(self):
        """显示bitmap，表示每个物理块的使用情况"""
        print("\nBitmap: (1 表示已占用，0 表示空闲)")
        print(self.memory_manager.bitmap)

    def display_memory_stack(self):
        """显示主存栈 (LRU)"""
        print("\n主存栈 (LRU):")
        print(self.memory_manager.memory_stack)




