from Modification.pcb_m import PCB, PCBManager
from typing import List, Optional
from buffer import log
from buffer import address_to_page_number
from Modification.memory_m import MemoryManager


class Scheduler:
    """多级反馈队列调度器"""

    def __init__(self, pcb_manager: PCBManager, memory_manager: MemoryManager, time_slices: List[int] = [1, 3, 5]):
        """
        :param pcb_manager: PCBManager 实例
        :param memory_manager: MemoryManager 实例
        :param time_slices: 每一级队列对应的时间片大小
        """
        self.pcb_manager = pcb_manager
        self.memory_manager = memory_manager
        self.time_slices = time_slices
        self.feedback_queues: List[List[PCB]] = [[] for _ in time_slices]  # 初始化多级反馈队列
        self.block_queues: List[dict] = []  # 阻塞队列，存储进程及其等待时间和下次移进的就绪队列等级
        self.finished_queues = []
        self.count = 0

    def create_process(self, process_name: str, arrive_time: int, need_time: int, task_name: str, size: int,
                       memory_manager: MemoryManager) -> Optional[PCB]:
        pcb = self.pcb_manager.create_process(process_name, arrive_time, need_time, task_name, size)
        self.insert_high_priority_process(pcb)
        return pcb

    def add_to_ready_queue(self, pcb: PCB, queue_level: int = 0):
        """将进程添加到指定队列"""
        if 0 <= queue_level < len(self.feedback_queues):
            self.feedback_queues[queue_level].append(pcb)
            pcb.ready()
            log.append(f"进程 {pcb.process_name} 被加入队列 {queue_level+1}（时间片: {self.time_slices[queue_level]}）")

            # 如果是初级队列，则根据到达时间进行排序
            if queue_level == 0:
                self.feedback_queues[queue_level] = sorted(self.feedback_queues[queue_level],
                                                           key=lambda x: x.arrive_time)

    def schedule(self):

        # 检查阻塞队列，将等待值减一
        self._decrement_block_queue_wait()

        """主调度逻辑"""
        for level, queue in enumerate(self.feedback_queues):
            if queue:
                process = queue.pop(0)
                self._execute_process(process, level)
                return

        # 若所有队列均为空，则表示没有可调度进程
        log.append("当前无可调度进程")


    def _decrement_block_queue_wait(self):
        """减少阻塞队列中进程的等待时间"""
        i = 0
        while i < len(self.block_queues):
            block_queue = self.block_queues[i]
            block_queue['wait'] -= 1

            if block_queue['wait'] == 0:
                # 等待值为 0，将进程移入其下次该移进的就绪队列
                pcb = block_queue['pcb']
                next_level = block_queue['next_level']
                pcb.remaining_time -= 1
                log.append(f"{pcb.process_name}获得I/O资源，从阻塞队列中释放,剩余时间{pcb.remaining_time}")
                pcb.ready()
                self.block_queues.pop(i)  # 从阻塞队列中移除
                self.add_to_ready_queue(pcb, next_level)
            else:
                i += 1  # 只有当没有删除元素时才增加索引

    def _execute_process(self, pcb: PCB, level: int):
        """页面请求"""
        self.pcb_manager.request_pages_for_process(pcb.process_name, self.memory_manager)

        """执行进程"""
        time_slice = self.time_slices[level]
        for _ in range(time_slice):


            page_values = [entry["page"] for entry in self.memory_manager.memory_stack]
            log.append(" ")
            log.append(f"当前主存栈为{page_values}")

            if pcb.remaining_time > 0:
                executed_instruction = pcb.run()
                if executed_instruction:  # 如果run方法返回了指令，则处理指令
                    operation = executed_instruction["operation"]
                    address = executed_instruction["address"]
                    if operation in ["READ", "WRITE"]:
                        page_number = address_to_page_number(address)  # 假设address_to_page是将地址转换为页号的函数

                        if operation == "WRITE":
                            self.memory_manager.deal_with_write(pcb,page_number)

                        self.memory_manager.request_page(page_number,pcb)  # 请求页号
                        log.append(f"进程 {pcb.process_name} 执行{operation}指令,请求页面 {page_number}")
                        # 执行完毕后减少剩余时间
                        pcb.remaining_time -= 1
                    elif operation in ["INPUT", "OUTPUT"]:
                        pcb.block()
                        self.block_queues.append(
                            {'pcb': pcb, 'wait': 3, 'next_level': min(level + 1, len(self.feedback_queues) - 1)})
                        log.append(f"进程 {pcb.process_name} 执行{operation}指令,阻塞进程")
                        log.append("--------------- FINSIH ---------------")
                        log.append(" ")
                        break

                log.append(f"进程 {pcb.process_name} 执行中，剩余时间: {pcb.remaining_time}")
                log.append("--------------- FINSIH ---------------")
                log.append(" ")

            else:
                break

        """判断执行结果"""
        if pcb.remaining_time == 0:
            # 进程完成，释放资源
            pcb.status = "Finished"
            log.append(f"进程 {pcb.process_name} 已完成执行")
            self.pcb_manager.terminate_process(pcb.process_name, self.memory_manager)
            self.finished_queues.append(pcb)
            log.append(f"进程 {pcb.process_name} 执行完成并被销毁")
        else:
            if pcb.status != "Blocked":
                pcb.ready()
                # 时间片用尽，将其降级到下一队列
                next_level = min(level + 1, len(self.feedback_queues) - 1)
                self.add_to_ready_queue(pcb, next_level)

    def terminate_process(self, process_name: str):
        for queue in self.feedback_queues:
            for pcb in queue:
                if pcb.process_name == process_name:
                    self.pcb_manager.terminate_process(process_name, self.memory_manager)
                    queue.remove(pcb)
                    log.append(f"将进程{pcb.process_name}销毁并释放内存")
                    return
        log.append(f"并没有找到{process_name}进程")

    def block_process(self, pcb: PCB):
        """阻塞进程"""
        # 这里可以添加阻塞进程的其他处理逻辑

    def insert_high_priority_process(self, pcb: PCB):
        """插入高优先级任务"""
        self.add_to_ready_queue(pcb, queue_level=0)
        log.append(f"插入高优先级进程 {pcb.process_name} 到队列 0")


if __name__ == "__main__":
    pcb_manager = PCBManager()
    memory = MemoryManager()
    scheduler = Scheduler(memory_manager=memory, pcb_manager=pcb_manager)

    scheduler.create_process("p1", 1, 7, "", 1000, memory_manager=memory)
    scheduler.create_process("p2", 2, 8, "", 1000, memory_manager=memory)
    scheduler.create_process("p3", 1, 7, "", 1000, memory_manager=memory)
    scheduler.create_process("p4", 2, 8, "", 1000, memory_manager=memory)

    for i in range(50):
        scheduler.schedule()