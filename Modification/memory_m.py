import random
from collections import deque

from Modification.pcb_m import PCBManager,PCB
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

        self.memory = [{"pcb":None,"page":-1}] * USABLE_BLOCKS  # 前 USABLE_BLOCKS 个块为空
        self.memory.extend([1] * (MEMORY_BLOCKS - USABLE_BLOCKS))  # 剩余块已满
        self.virtual_memory = [f"Page {i} empty" for i in range(VIRTUAL_PAGES)]
        self.bitmap = [0] * USABLE_BLOCKS + [1] * (MEMORY_BLOCKS - USABLE_BLOCKS)
        self.memory_stack = deque()

    def request_pages_for_process(self, pcb):
        """根据 PCB 请求分配的页面"""
        if pcb.page_count == 0:
            log.append(f"进程 {pcb.process_name} 没有分配页面。")
            return

        pages = list(range(0, pcb.page_count))
        # 随机选择一个页面号
        selected_page = random.choice(pages)


        log.append(f"进程 {pcb.process_name} 请求页面{selected_page} ")

        # 请求选中的页面
        self.request_page(selected_page,pcb)

    def deal_with_write(self,pcb:PCB,number):
        pcb.page_table[number]["modification"] = 1
        log.append(f"执行WRITE进程，进程{pcb.process_name}的{number}页修改为置1 ")

    def release_memory(self, pcb):

        block_list = []
        """清空进程的页表"""
        for page_table_item in pcb.page_table:
            page_table_item["exist"] = 0
            page_table_item["frame"] = -1

        """清空主存列表"""
        for i,memory_item in enumerate(self.memory[:USABLE_BLOCKS]):
            if memory_item["pcb"] == pcb:
                memory_item["page"] = -1
                memory_item["pcb"] = None
                self.bitmap[i] = 0
                block_list.append(i)


        """清空在主存栈中的相关内容"""
        # 创建一个需要移除的元素的集合
        blocks_to_remove = set(block_list)

        # 迭代 self.memory_stack 的副本，以避免在迭代过程中修改原 deque
        for item in list(self.memory_stack):
            if item["block"] in blocks_to_remove:
                self.memory_stack.remove(item)
        log.append(f"进程 {pcb.process_name} 的页面已释放(main memory and bitmap)")


    def request_page(self, page_index , pcb:PCB):

        print(f"请求进程{pcb.process_name}页号{page_index}")
        """请求单个页面并按需加载到主存"""
        exist = pcb.page_table[page_index]['exist']

        if exist == 1 :
            log.append(f"页面{page_index}已在主存中")
            print(f"页面{page_index}已在主存中")
            self._update_lru(page_index)
        else:
            self._load_page(page_index,pcb)

    def _load_page(self, page_index , pcb):
        """将页面加载到主存，并进行 LRU 页面置换"""
        if len(self.memory_stack) >= USABLE_BLOCKS:  # 主存已满

            # print(f"lru前{self.memory_stack}")

            evicted_item = self.memory_stack.popleft()
            block_index = evicted_item["block"]
            print(f"最久未使用的块号为{block_index},最久未使用的页面为{evicted_item}")
            log.append(f"最久未使用的块号为{block_index},最久未使用的页面为{evicted_item}")
            evicted_page = evicted_item["page"]
            evicted_pcb = self.memory[block_index]["pcb"]
            evicted_pcb.page_table[evicted_page]["exist"] = 0
            log.append(f"进程{evicted_pcb.process_name}的页面{evicted_page}写回外存") if \
                evicted_pcb.page_table[evicted_page]["modification"] == 1 else None
            print(f"进程{evicted_pcb.process_name}的页面{evicted_page}写回外存") if \
            evicted_pcb.page_table[evicted_page]["modification"] == 1 else None
            self.bitmap[block_index] = 0  # 将对应的 bitmap 位置设置为 0
            print("LRU")
            log.append(" ")
            log.append("************* LRU *************")
            log.append(f"页面置换: 驱逐{evicted_pcb.process_name} 页面 {evicted_page}")
            # print(f"lru中:{self.memory_stack}")
            log.append("*********** FINISH ************")
            log.append(" ")

        else:
            block_index = 0

            for i in range(USABLE_BLOCKS):
                if self.memory[i]["pcb"] is None:
                    block_index = i
                    break

        self.memory_stack.append({"block":block_index,"page":page_index,"pcb":pcb.process_name})
        self.memory[block_index] = {"pcb":pcb,"page":page_index}  # 更新 memory 数组
        self.bitmap[block_index] = 1  # 将对应的 bitmap 位置设置为 1
        pcb.page_table[page_index]["exist"] = 1
        pcb.page_table[page_index]["frame"] = block_index
        log.append(f"{pcb.process_name} 页面 {page_index} 加载到主存块 {block_index}")

        # print(f"lru后{self.memory_stack}")

    def _update_lru(self, page_index):
        """更新页面在 LRU 栈中的位置"""
        r_item = None
        for item in self.memory_stack:
            if item["page"] == page_index:
                self.memory_stack.remove(item)
                r_item = item
                break
        self.memory_stack.append(r_item)
