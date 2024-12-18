import random
from collections import deque
from buffer import log
from buffer import VIRTUAL_PAGES, PAGE_SIZE,MEMORY_BLOCKS,USABLE_BLOCKS
"""内存管理器类"""


class MemoryManager:

    def __init__(self):
        # 初始化 page_table
        self.page_table = [
            {"valid": "empty", "block": -1, "used": 0} if i < VIRTUAL_PAGES // 2
            else {"valid": "full", "block": -1, "used": 1024}
            for i in range(VIRTUAL_PAGES)
        ]
        self.memory = [-1] * USABLE_BLOCKS  # 前 USABLE_BLOCKS 个块为空
        self.memory.extend([1] * (MEMORY_BLOCKS - USABLE_BLOCKS))  # 剩余块已满
        self.virtual_memory = [f"Page {i} empty" for i in range(VIRTUAL_PAGES)]
        self.bitmap = [0] * USABLE_BLOCKS + [1] * (MEMORY_BLOCKS - USABLE_BLOCKS)
        self.memory_stack = deque()

    def allocate_pages(self, memory_size):
        """分配页面，按照首次适应算法。"""
        required_memory = memory_size
        start_page = None
        allocated_pages = []
        remaining_memory = required_memory

        for page_index in range(VIRTUAL_PAGES):
            page = self.page_table[page_index]

            if page["valid"] in ["using", "empty"]:
                available_memory = PAGE_SIZE - page["used"]

                if available_memory > 0:
                    allocation = min(remaining_memory, available_memory)
                    remaining_memory -= allocation

                    if start_page is None:
                        start_page = page_index

                    allocated_pages.append((page_index, page["used"], allocation))
                    page["used"] += allocation

                    if page["used"] == PAGE_SIZE:
                        page["valid"] = "full"
                    else:
                        page["valid"] = "using"

                    if remaining_memory <= 0:
                        break
                else:
                    start_page = None
                    allocated_pages = []
                    remaining_memory = required_memory

        if remaining_memory > 0:
            # 分配失败，回滚所有已经分配的页面
            for page_index, start_address, allocation in allocated_pages:
                self.page_table[page_index]["used"] -= allocation
                if self.page_table[page_index]["used"] == 0:
                    self.page_table[page_index]["valid"] = "empty"
            return None

        return start_page, allocated_pages

    def assign_memory_to_process(self, pcb, size):
        """为进程分配具体内存位置"""
        remaining_size = size
        page_table = []
        for page in range(pcb.begin, pcb.begin + pcb.page_count):
            allocated_size = min(remaining_size, PAGE_SIZE - self.page_table[page]["used"])
            page_table.append((page, self.page_table[page]["used"], allocated_size))
            self.page_table[page]["used"] += allocated_size
            remaining_size -= allocated_size

            if self.page_table[page]["used"] == PAGE_SIZE:
                self.page_table[page]["valid"] = "full"
            else:
                self.page_table[page]["valid"] = "using"

            if remaining_size <= 0:
                break
        return page_table

    def request_pages_for_process(self, pcb):
        """根据 PCB 请求分配的页面"""
        if pcb.page_count == 0:
            log.append(f"进程 {pcb.process_name} 没有分配页面。")
            return

        pages = list(range(0, pcb.page_count))
        # 随机选择一个页面号
        selected_page = random.choice(pages)
        selected_page_frame = selected_page+pcb.begin

        log.append(f"进程 {pcb.process_name} 请求页面{selected_page} || 页框号为{selected_page_frame}")

        # 请求选中的页面
        self.request_page(selected_page_frame)

    def release_memory(self, pcb):
        """释放进程占用的页面"""
        for page in range(pcb.begin, pcb.begin + pcb.page_count):
            # 检查页面是否在主存栈中，如果在，则移除
            if page in self.memory_stack:
                self.memory_stack.remove(page)

            # 检查页面是否有对应的物理块索引，如果有，则更新 bitmap
            if self.page_table[page]["block"] != -1:
                block_index = self.page_table[page]["block"]
                self.bitmap[block_index] = 0  # 将对应的 bitmap 位置设置为 0
                self.page_table[page]["block"] = -1  # 重置页面的 block 索引为 -1

            # 重置页面状态为 "empty"
            if pcb.page_table[page - pcb.begin][2] == 1024:
                self.page_table[page] = {"valid": "empty", "block": -1, "used": 0}
            else:
                if self.page_table[page]["valid"] == "using":
                    self.page_table[page] = {"valid": "empty", "block": -1, "used": 0}
                else:
                    used = self.page_table[page]["used"]
                    self.page_table[page] = {"valid": "using", "block": -1,
                                             "used": used - pcb.page_table[page - pcb.begin][2]}

        log.append(f"进程 {pcb.process_name} 的页面已释放(main memory and bitmap)")

    def request_page(self, page_index):
        """请求单个页面并按需加载到主存"""
        if self.page_table[page_index]["valid"]:
            if self.page_table[page_index]["block"] != -1:
                log.append(f"页框 {page_index} 已在主存。")
                self._update_lru(page_index)
            else:
                self._load_page(page_index)
        else:
            log.append(f"页框 {page_index} 无效 (未分配)，无法加载")

    def _load_page(self, page_index):
        """将页面加载到主存，并进行 LRU 页面置换"""
        if len(self.memory_stack) >= USABLE_BLOCKS:  # 主存已满
            evicted_page = self.memory_stack.popleft()
            block_index = self.page_table[evicted_page]["block"]
            self.page_table[evicted_page]["block"] = -1
            # 更新 memory 数组，将被驱逐的页面位置置为 -1
            self.memory[block_index] = -1
            self.bitmap[block_index] = 0  # 将对应的 bitmap 位置设置为 0
            print("LRU")
            log.append(" ")
            log.append("************* LRU *************")
            log.append(f"页面置换: 驱逐页框号 {evicted_page}")
            self.page_table[page_index]["block"] = block_index
            log.append("*********** FINISH ************")
            log.append(" ")

        else:
            block_index = len(self.memory_stack)
            self.page_table[page_index]["block"] = block_index

        self.memory[block_index] = page_index  # 更新 memory 数组
        self.memory_stack.append(page_index)
        self.bitmap[block_index] = 1  # 将对应的 bitmap 位置设置为 1
        log.append(f"页框号 {page_index} 加载到主存块 {block_index}")

    def _update_lru(self, page_index):
        """更新页面在 LRU 栈中的位置"""
        if page_index in self.memory_stack:
            self.memory_stack.remove(page_index)
        self.memory_stack.append(page_index)
