from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout

class ChildWindow(QWidget):
    """子窗体类"""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("子窗口")
        self.setGeometry(500, 500, 300, 200)

        # 在子窗口中设置一个简单的布局
        layout = QVBoxLayout(self)

        label = QLabel("这是子窗口", self)
        layout.addWidget(label)

        self.setLayout(layout)


class MainWindow(QWidget):
    """主窗体类"""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("主窗口")
        self.setGeometry(100, 100, 500, 400)

        # 在主窗口中设置布局
        layout = QVBoxLayout(self)

        label = QLabel("这是主窗口", self)
        layout.addWidget(label)

        # 创建并添加子窗口
        self.child_window = ChildWindow()  # 创建子窗口
        self.child_window.setParent(self)  # 设置父窗口为主窗口
        self.child_window.move(150, 100)  # 移动子窗口到主窗口中的某个位置
        self.child_window.show()  # 显示子窗口

        button = QPushButton("关闭子窗口", self)
        button.clicked.connect(self.close_child_window)
        layout.addWidget(button)

        self.setLayout(layout)

    def close_child_window(self):
        """关闭子窗口"""
        self.child_window.close()


# 创建 PyQt 应用并运行
app = QApplication([])
window = MainWindow()
window.show()
app.exec_()
