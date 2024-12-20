import tkinter as tk
from tkinter import ttk

# 假设这是你的表格数据，每个键对应下拉框的一个选项
table_data = {
    'Option1': [('Row1', 'Data1'), ('Row2', 'Data2')],
    'Option2': [('Row1', 'Data3'), ('Row2', 'Data4')],
    # ... 其他选项和数据
}

# 表格更新函数，根据下拉框的选项更新表格内容
def update_table(event=None):  # event=None 允许在程序启动时调用此函数
    selected_option = combo_box.get()
    if selected_option:  # 确保selected_option不是空字符串
        tree.delete(*tree.get_children())  # 清空表格
        for row_data in table_data.get(selected_option, []):  # 使用get方法安全访问字典
            tree.insert('', 'end', values=row_data)
    else:
        tree.delete(*tree.get_children())  # 如果没有选项被选中，清空表格

# 创建主窗口
root = tk.Tk()
root.title("Tkinter with Combobox and Table")

# 创建下拉框，并设置默认值
combo_box = ttk.Combobox(root, values=list(table_data.keys()))
combo_box.grid(column=0, row=0, padx=10, pady=10)
combo_box.set('Option1')  # 设置默认选项，确保不会传递空字符串
combo_box.bind("<<ComboboxSelected>>", update_table)

# 创建表格
tree = ttk.Treeview(root, columns=('Column1', 'Column2'), show='headings')
tree.heading('Column1', text='Column 1')
tree.heading('Column2', text='Column 2')
tree.grid(column=0, row=1, padx=10, pady=10)

# 默认加载第一个选项的数据
update_table()

# 运行主循环
root.mainloop()