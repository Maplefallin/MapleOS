import random
from typing import List, Optional
from buffer import generate_random_address,log


class PCB:
    """进程控制块类，记录进程的基本信息"""

    def __init__(self, process_name: str, arrive_time: int, need_time: int, task_name: str, size: int):
        self.process_name = process_name
        self.arrive_time = arrive_time
        self.need_time = need_time
        self.task_name = task_name
        self.size = size
        self.begin = -1  # 起始页号
        self.page_count = 0  # 分配的页面数
        self.page_table = []  # 地址表 [(页号, 起始地址, 分配长度)]
        self.status = "Ready"  # 默认状态为就绪
        self.remaining_time = need_time  # 剩余执行时间

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
            if random.random() < 0.8:  # 70% 的概率生成读写指令
                operation = random.choice(["READ", "WRITE"])
                # 生成随机地址，0 到 32*1024
                address = generate_random_address()
            else:  # 30% 的概率生成输入输出指令
                operation = random.choice(["INPUT", "OUTPUT"])
                address = -1  # 输入输出指令地址固定为 -1
            instructions.append({"operation": operation, "address": address})
        return instructions

    def run(self):
        """将状态置为运行，并执行一条指令"""
        if self.status in ["Ready", "Blocked"]:
            self.status = "Running"

        if self.status == "Running" and self.remaining_time > 0:
            # 执行下一条指令
            if self.instructions:
                instruction = self.instructions.pop(0)
                operation = instruction["operation"]
                address = instruction["address"]
                log.append(f"------- {self.process_name} EXECUTE -------")
                log.append(" ")
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
                log.append(" ")
                log.append("--------- FINSIH ---------")
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
                       memory_manager) -> Optional[PCB]:
        """创建新进程并分配页面"""
        allocation_result = memory_manager.allocate_pages(size)
        if allocation_result is None:
            log.append(f"进程 {process_name} 创建失败: 内存不足")
            return None

        start_page, page_table = allocation_result
        pcb = PCB(process_name, arrive_time, need_time, task_name, size)
        pcb.begin = start_page
        pcb.page_count = len(page_table)
        pcb.page_table = page_table
        self.processes.append(pcb)
        log.append(f"进程 {process_name} 创建成功，起始页号: {start_page}")
        return pcb

    def terminate_process(self, process_name: str, memory_manager):
        """终止进程并释放资源"""
        for pcb in self.processes:
            if pcb.process_name == process_name:
                memory_manager.release_memory(pcb)
                self.processes.remove(pcb)
                return

    def change_status(self, process_name: str, action: str):
        """更改进程状态"""
        for pcb in self.processes:
            if pcb.process_name == process_name:
                if action == "run":
                    if self.running_process:
                        self.ready_queue.append(self.running_process)
                        self.running_process.status = "Ready"
                    self.running_process = pcb
                    if pcb in self.ready_queue:
                        self.ready_queue.remove(pcb)
                elif action == "block":
                    if self.running_process == pcb:
                        pcb.block()
                        self.blocked_queue.append(pcb)
                        self.running_process = None
                elif action == "ready":
                    if pcb in self.blocked_queue:
                        pcb.ready()
                        self.blocked_queue.remove(pcb)
                        self.ready_queue.append(pcb)
                return

    def request_pages_for_process(self, process_name: str, memory_manager):
        """根据进程名请求页面"""
        for pcb in self.processes:
            if pcb.process_name == process_name:
                memory_manager.request_pages_for_process(pcb)
                return
        log.append(f"进程 {process_name} 未找到！")
