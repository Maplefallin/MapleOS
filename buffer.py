import random
from typing import List

log: List[str] = []  # 记录调度日志
PAGE_SIZE = 256  # 每页大小
VIRTUAL_PAGES = 64  # 虚拟页框总数
MEMORY_BLOCKS = 64  #主存块述
USABLE_BLOCKS = 10

def generate_random_address(page_count):
    """生成一个 0 到 32 * 1024 之间的随机整数"""
    return random.randint(0*PAGE_SIZE, (page_count-2)*PAGE_SIZE)

def generate_hex_address(address):
    """生成一个十六进制地址"""
    hex_address = f"0x{address:04X}"  # 转换为四位十六进制
    return hex_address

def address_to_page_number(address: int, page_size: int = PAGE_SIZE) -> int:
    """
    将地址转换为所在页号。

    :param address: 要转换的地址（整数类型）。
    :param page_size: 页面大小，默认为 1024。
    :return: 地址所在的页号。
    """
    if address < 0:
        raise ValueError("地址不能为负数")
    return address // page_size