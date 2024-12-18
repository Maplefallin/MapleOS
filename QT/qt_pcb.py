from client import PCB
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QDialog, QHBoxLayout, QTableWidget, QTableWidgetItem, QPushButton
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont

class ProcessInfoWindow(QDialog):
    """显示进程详细信息和页表的窗口"""
    def __init__(self, pcb: PCB, parent=None):
        super().__init__(parent)
        self.pcb = pcb
        self.initUI()

    def initUI(self):
        # 设置窗口标题
        self.setWindowTitle(f"进程 {self.pcb.process_name} 信息")
        layout = QVBoxLayout(self)

        # PCB基本信息表格
        self.pcb_info_table = QTableWidget(self)
        self.pcb_info_table.setRowCount(8)  # 基本信息有8个字段
        self.pcb_info_table.setColumnCount(2)
        self.pcb_info_table.setHorizontalHeaderLabels(["字段", "值"])
        self.fill_basic_info()
        layout.addWidget(self.pcb_info_table)

        # 创建一个水平布局用于并排显示页表和指令集
        tables_layout = QHBoxLayout()

        # 页表信息表格
        self.page_table = QTableWidget(self)
        self.page_table.setRowCount(len(self.pcb.page_table))
        self.page_table.setColumnCount(4)
        self.page_table.setHorizontalHeaderLabels(["页号", "页框号","起始地址", "分配长度"])
        self.fill_page_table()
        tables_layout.addWidget(self.page_table)

        # 指令集信息表格
        self.instruction_table = QTableWidget(self)
        self.instruction_table.setRowCount(len(self.pcb.instructions))
        self.instruction_table.setColumnCount(2)
        self.instruction_table.setHorizontalHeaderLabels(["操作", "地址"])
        self.fill_instruction_table()
        tables_layout.addWidget(self.instruction_table)

        layout.addLayout(tables_layout)

        # 添加关闭按钮
        close_button = QPushButton("关闭", self)
        close_button.clicked.connect(self.close)
        layout.addWidget(close_button)

        self.setLayout(layout)

    def fill_basic_info(self):
        """填充 PCB 的基本信息表格"""
        basic_info = {
            "进程名称": self.pcb.process_name,
            "到达时间": self.pcb.arrive_time,
            "需求时间": self.pcb.need_time,
            "任务名称": self.pcb.task_name,
            "大小": self.pcb.size,
            "起始页号": self.pcb.begin,
            "分配的页面数": self.pcb.page_count,
            "状态": self.pcb.status,
            "剩余执行时间": self.pcb.remaining_time
        }
        row = 0
        for field, value in basic_info.items():
            self.pcb_info_table.setItem(row, 0, QTableWidgetItem(field))
            self.pcb_info_table.setItem(row, 1, QTableWidgetItem(str(value)))
            row += 1

    def fill_page_table(self):
        """填充 PCB 的页表信息表格"""
        for row, (page_number,page_frame, start_address, length) in enumerate(self.pcb.page_table):
            self.page_table.setItem(row, 0, QTableWidgetItem(str(page_number)))
            self.page_table.setItem(row, 1, QTableWidgetItem(str(page_frame)))
            self.page_table.setItem(row, 2, QTableWidgetItem(str(start_address)))
            self.page_table.setItem(row, 3, QTableWidgetItem(str(length)))

    def fill_instruction_table(self):
        """填充 PCB 的指令集信息表格"""
        for row, instruction in enumerate(self.pcb.instructions):
            self.instruction_table.setItem(row, 0, QTableWidgetItem(instruction["operation"]))
            self.instruction_table.setItem(row, 1, QTableWidgetItem(str(instruction["address"])))


class PCBWidget(QWidget):
    """进程控制块的GUI组件，显示为一个自适应大小的小块，并显示进程名称"""
    def __init__(self, pcb: PCB, parent=None):
        super().__init__(parent)
        self.pcb = pcb
        self.initUI()

    def initUI(self):
        # 设置背景样式
        self.setStyleSheet(
            "background-color: #f0f0f0; "
            "border: 2px solid #000000; "  # 设置边框厚度为 2px，颜色为黑色
            "border-radius: 10px;"  # 设置圆角
        )

        # 创建一个标签显示进程名称
        self.label = QLabel(self.pcb.process_name, self)
        self.label.setAlignment(Qt.AlignCenter)
        font = QFont()
        font.setBold(True)
        self.label.setFont(font)

        # 布局管理器，将标签居中显示
        layout = QVBoxLayout(self)
        layout.addWidget(self.label)

    def sizeHint(self) -> QSize:
        """根据进程名称的长度动态调整组件大小"""
        label_width = self.label.fontMetrics().horizontalAdvance(self.pcb.process_name) + 20  # 为了保证足够的空间显示名称
        label_height = 60  # 设定固定高度
        return QSize(label_width, label_height)

    def mousePressEvent(self, event):
        """鼠标点击事件时，显示进程详细信息窗口"""
        print(f"进程 {self.pcb.process_name} 被点击")
        self.showProcessInfo()

    def showProcessInfo(self):
        """显示进程详细信息的窗口"""
        self.info_window = ProcessInfoWindow(self.pcb)
        self.info_window.exec_()



