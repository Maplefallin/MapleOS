import math
import random
from typing import List, Optional
from buffer import generate_random_address, log, VIRTUAL_PAGES, PAGE_SIZE



class PCB:
    """进程控制块类，记录进程的基本信息"""

    def __init__(self, process_name: str, arrive_time: int, need_time: int, task_name: str, size: int):
        self.process_name = process_name
        self.arrive_time = arrive_time
        self.need_time = need_time
        self.task_name = task_name
        self.size = size
        self.begin = -1  # 页框号的起始地址
        self.page_count = 0  # 分配的页面数
        self.page_table = []  # 地址表 [{"page":None,"frame"：-1,"exist":0}]
        self.status = "Ready"  # 默认状态为就绪
        self.remaining_time = need_time  # 剩余执行时间
        self.memory_index = -1

        # 计算 page_total 并向上取整
        page_total = int(math.ceil(self.size / PAGE_SIZE))
        self.page_count = page_total

        # 指令集：生成约10条随机指令
        self.instructions = self._generate_instruction_set()

    def __repr__(self):
        return (f"PCB(process_name={self.process_name}, arrive_time={self.arrive_time}, "
                f"need_time={self.need_time}, remaining_time={self.remaining_time}, "
                f"status={self.status}, begin={self.begin}, "
                f"size={self.size}, page_count={self.page_count}, page_table={self.page_table}, "
                f"instructions={self.instructions})")

    def _generate_instruction_set(self):
        """生成一个随机指令集，每条指令以字典形式存储"""
        instructions = []
        for _ in range(20):  # 生成约 10 条指令
            # 生成随机数来决定是读写操作还是输入输出操作
            if random.random() < 0.9:  # 70% 的概率生成读写指令
                operation = random.choice(["READ", "WRITE"])
                # 生成随机地址，0 到 32*1024
                address = generate_random_address(self.page_count)
            else:  # 30% 的概率生成输入输出指令
                operation = random.choice(["INPUT", "OUTPUT"])
                address = -1  # 输入输出指令地址固定为 -1
            instructions.append({"operation": operation, "address": address})
        return instructions

    def run(self):
        """将状态置为运行，并执行一条指令"""
        if self.status in ["Ready", "Blocked"]:
            self.status = "Running"
            log.append(f"当前状态 ***** {self.status} *****")

        if self.status == "Running" and self.remaining_time > 0:
            # 执行下一条指令
            if self.instructions:
                instruction = self.instructions.pop(0)
                operation = instruction["operation"]
                address = instruction["address"]
                log.append(" ")
                log.append(f"------------- {self.process_name} EXECUTE --------------")
                log.append(f"进程 {self.process_name} 执行指令: {operation}, 地址: {address}")

                # 根据操作类型执行对应指令
                if operation == "READ":
                    self.read_memory(address)
                elif operation == "WRITE":
                    self.write_memory(address)
                elif operation == "INPUT":
                    self.input_data()
                elif operation == "OUTPUT":
                    self.output_data()

                log.append(f"进程 {self.process_name} 执行完毕，剩余时间: {self.remaining_time}")
                log.append("--------------- FINSIH ---------------")
                log.append(" ")
                return instruction

            else:
                log.append(f"进程 {self.process_name} 无指令可执行")

        if self.remaining_time == 0:
            self.status = "Finished"
            log.append(f"进程 {self.process_name} 已完成执行")

    def block(self):
        self.status = "Blocked"

    def ready(self):
        self.status = "Ready"

    def read_memory(self, address):
        """模拟读内存操作"""
        log.append(f"进程 {self.process_name} 执行 'READ' 操作，地址: {address}")

    def write_memory(self, address):
        """模拟写内存操作"""
        log.append(f"进程 {self.process_name} 执行 'WRITE' 操作，地址: {address}")

    def input_data(self):
        """模拟输入操作"""
        log.append(f"进程 {self.process_name} 执行 'INPUT' 操作")

    def output_data(self):
        """模拟输出操作"""
        log.append(f"进程 {self.process_name} 执行 'OUTPUT' 操作")


class PCBManager:
    """进程管理器类，用于管理多个 PCB"""

    def __init__(self):
        self.processes: List[PCB] = []
        self.running_process: Optional[PCB] = None
        self.ready_queue: List[PCB] = []
        self.blocked_queue: List[PCB] = []

    def create_process(self, process_name: str, arrive_time: int, need_time: int, task_name: str, size: int,
                       ) -> Optional[PCB]:
        """创建新进程并分配页面"""
        pcb = PCB(process_name, arrive_time, need_time, task_name, size)

        for i in range(pcb.page_count):
            pcb.page_table.append({"page":i,"frame":-1,"exist":0,"modification":0})

        self.processes.append(pcb)

        log.append(f"{pcb.process_name}进程创建成功")
        return pcb


    def terminate_process(self, process_name: str, memory_manager):
        """终止进程并释放资源"""

        for pcb in self.processes:
            if pcb.process_name == process_name:

                for item in pcb.page_table:
                    item["frame"] = -1
                    item["exist"] = 0

                memory_manager.release_memory(pcb)  #修改
                self.processes.remove(pcb)
                return


    def request_pages_for_process(self, process_name: str, memory_manager):
        """根据进程名请求页面"""
        for pcb in self.processes:
            if pcb.process_name == process_name:
                memory_manager.request_pages_for_process(pcb)
                return
        log.append(f"进程 {process_name} 未找到！")


if __name__ == "__main__":
    pcb_manager = PCBManager()
    pcb = pcb_manager.create_process("p1",1,6,"t1",1000,)
    print(pcb)