from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, QDialog, \
    QFormLayout, QListWidget, QListWidgetItem, QLabel, QFrame
from PyQt5.QtCore import Qt, QTimer
from pcb import PCB, PCBManager
from memory import MemoryManager
from buffer import log
from scheduler import Scheduler
from qt_pcb import PCBWidget, ProcessInfoWindow


class ProcessDialog(QDialog):
    """弹出框用于输入新进程的参数"""
    def __init__(self, scheduler: Scheduler, parent=None):
        super().__init__(parent)
        self.setWindowTitle("添加进程")
        self.setGeometry(400, 400, 300, 200)

        self.scheduler = scheduler  # 接收 Scheduler 实例

        # 创建输入框
        self.process_name_input = QLineEdit(self)
        self.arrive_time_input = QLineEdit(self)
        self.need_time_input = QLineEdit(self)
        self.task_name_input = QLineEdit(self)
        self.size_input = QLineEdit(self)

        # 布局
        layout = QFormLayout(self)
        layout.addRow("进程名称:", self.process_name_input)
        layout.addRow("到达时间:", self.arrive_time_input)
        layout.addRow("需要时间:", self.need_time_input)
        layout.addRow("任务名称:", self.task_name_input)
        layout.addRow("内存大小:", self.size_input)

        # 确认按钮
        self.confirm_button = QPushButton("完成", self)
        self.confirm_button.clicked.connect(self.on_confirm)
        layout.addWidget(self.confirm_button)

    def on_confirm(self):
        """确认按钮点击事件"""
        try:
            process_name = self.process_name_input.text()
            arrive_time = int(self.arrive_time_input.text())
            need_time = int(self.need_time_input.text())
            task_name = self.task_name_input.text()
            size = int(self.size_input.text())

            # 创建进程
            pcb = self.scheduler.create_process(process_name, arrive_time, need_time, task_name, size, self.scheduler.memory_manager)

            if pcb:
                log.append(f"进程 {pcb.process_name} 被创建并加入调度")
                self.accept()  # 关闭弹窗
        except Exception as e:
            print(f"Error creating process: {e}")


class SchedulerGUI(QWidget):
    def __init__(self, scheduler: Scheduler):
        super().__init__()
        self.scheduler = scheduler  # 接收外部传入的 Scheduler 实例
        self.initUI()

    def initUI(self):
        self.setWindowTitle('进程调度器')
        self.setGeometry(400, 400, 800, 800)

        # 创建主布局
        layout = QVBoxLayout(self)

        # 添加进程按钮
        button_layout = QHBoxLayout(self)
        self.add_process_button = QPushButton('添加进程', self)
        self.add_process_button.setFixedSize(100, 50)
        self.add_process_button.clicked.connect(self.show_process_dialog)

        self.schedule_button = QPushButton('调度', self)
        self.schedule_button.setFixedSize(100, 50)
        self.schedule_button.clicked.connect(self.schedule_process)

        button_layout.addWidget(self.add_process_button)
        button_layout.addWidget(self.schedule_button)

        layout.addLayout(button_layout)

        # 创建一个水平布局用于容纳所有队列
        queue_layout = QHBoxLayout()

        # 创建显示三个反馈队列
        self.feedback_labels = []  # 保存队列标签
        self.feedback_list_widgets = []  # 保存队列列表显示

        for i in range(3):  # 创建三个队列
            label = QLabel(f"队列{i + 1}(时间片为 {2*(i+1)})", self)
            queue_widget = QListWidget(self)
            queue_widget.setFixedSize(100, 300)  # 设置固定大小
            queue_widget.setAutoFillBackground(True)
            queue_widget.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
            self.feedback_labels.append(label)
            self.feedback_list_widgets.append(queue_widget)
            queue_layout.addWidget(label, alignment=Qt.AlignCenter)
            queue_layout.addWidget(queue_widget, alignment=Qt.AlignCenter)

        layout.addLayout(queue_layout)

        divider1 = QFrame(self)
        divider1.setGeometry(0, 80, 800, 8)  # 设置分界线的位置和大小
        divider1.setFrameShape(QFrame.HLine)  # 设置分界线的形状为水平线
        divider1.setFrameShadow(QFrame.Sunken)  # 可以设置分界线的阴影样式
        divider1.setLineWidth(3)  # 设置分界线的宽度为3

        divider2 = QFrame(self)
        divider2.setGeometry(0, 430, 800, 8)  # 设置分界线的位置和大小
        divider2.setFrameShape(QFrame.HLine)  # 设置分界线的形状为水平线
        divider2.setFrameShadow(QFrame.Sunken)  # 可以设置分界线的阴影样式
        divider2.setLineWidth(3)  # 设置分界线的宽度为3

        # 阻塞队列和完成队列
        block_layout = QHBoxLayout()
        block_label = QLabel(f"阻塞队列", self)
        self.block_widget = QListWidget(self)
        self.block_widget.setFixedSize(100, 300)  # 设置固定大小
        self.block_widget.setAutoFillBackground(True)
        self.block_widget.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        block_layout.addWidget(block_label, alignment=Qt.AlignCenter)
        block_layout.addWidget(self.block_widget, alignment=Qt.AlignCenter)

        finished_label = QLabel(f"完成队列", self)
        self.finished_widget = QListWidget(self)
        self.finished_widget.setFixedSize(100, 300)  # 设置固定大小
        self.finished_widget.setAutoFillBackground(True)
        self.finished_widget.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        block_layout.addWidget(finished_label, alignment=Qt.AlignCenter)
        block_layout.addWidget(self.finished_widget, alignment=Qt.AlignCenter)

        layout.addLayout(block_layout)

        self.setLayout(layout)

        # 初始化进程和队列状态
        self.cached_queues = [list(self.scheduler.feedback_queues[i]) for i in range(3)]  # 缓存初始队列状态
        self.update_feedback_queues()

        # 设置定时器，每隔一秒检查队列是否变化
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.check_feedback_queues)
        self.timer.start(1000)  # 每1000毫秒（即1秒）检查一次

    def show_process_dialog(self):
        """显示添加进程的弹框"""
        dialog = ProcessDialog(self.scheduler, self)  # 传递外部的 scheduler
        if dialog.exec_() == QDialog.Accepted:
            # 更新进程列表显示
            self.update_feedback_queues()

    def check_feedback_queues(self):
        """检查反馈队列是否发生变化"""
        try:
            for i, current_queue in enumerate(self.scheduler.feedback_queues):
                # 获取当前队列和缓存队列进行比较
                if list(current_queue) != self.cached_queues[i]:
                    # 队列发生变化，更新缓存并刷新显示
                    self.cached_queues[i] = list(current_queue)
                    self.update_feedback_queues()
                    self.update_block_queues()
                    self.update_finish_queues()
        except Exception as e:
            print(f"Error checking feedback queues: {e}")

    def update_feedback_queues(self):
        """更新反馈队列的显示"""
        try:
            for i, queue_widget in enumerate(self.feedback_list_widgets):
                queue_widget.clear()
                queue = self.scheduler.feedback_queues[i]  # 获取当前队列
                for pcb in queue:
                    # 为每个进程创建一个 PCBWidget
                    qt_pcb = PCBWidget(pcb, self)
                    list_item = QListWidgetItem(queue_widget)
                    list_item.setSizeHint(qt_pcb.sizeHint())  # 设置列表项的大小
                    queue_widget.addItem(list_item)
                    queue_widget.setItemWidget(list_item, qt_pcb)  # 将 PCBWidget 作为项添加到列表中
        except Exception as e:
            print(f"Error updating feedback queues: {e}")

    def update_block_queues(self):
        """更新阻塞队列的显示"""
        try:
            self.block_widget.clear()
            for pcb in self.scheduler.block_queues:
                # 为每个进程创建一个 PCBWidget
                qt_pcb = PCBWidget(pcb["pcb"], self)
                list_item = QListWidgetItem(self.block_widget)
                list_item.setSizeHint(qt_pcb.sizeHint())  # 设置列表项的大小
                self.block_widget.addItem(list_item)
                self.block_widget.setItemWidget(list_item, qt_pcb)  # 将 PCBWidget 作为项添加到列表中
        except Exception as e:
            print(f"Error updating block queues: {e}")

    def update_finish_queues(self):
        """更新完成队列的显示"""
        try:
            self.finished_widget.clear()
            for pcb in self.scheduler.finished_queues:
                # 为每个进程创建一个 PCBWidget
                qt_pcb = PCBWidget(pcb, self)
                list_item = QListWidgetItem(self.finished_widget)
                list_item.setSizeHint(qt_pcb.sizeHint())  # 设置列表项的大小
                self.finished_widget.addItem(list_item)
                self.finished_widget.setItemWidget(list_item, qt_pcb)  # 将 PCBWidget 作为项添加到列表中
        except Exception as e:
            print(f"Error updating finish queues: {e}")

    def schedule_process(self):
        try:
            self.scheduler.schedule()
        except Exception as e:
            print(f"Error scheduling process: {e}")
