from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QTableWidget, QTableWidgetItem, QHeaderView, QMenu, QAction, QDialog, QLineEdit, QFormLayout, QMessageBox, QInputDialog
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt, pyqtSignal
from datetime import datetime
import os
import untils.dataVisualization as dv

class AdminView(QWidget):
    # 定义信号，用于添加用户、限制用户和删除用户
    add_user_signal = pyqtSignal(dict)
    limit_user_signal = pyqtSignal(str, int)
    delete_user_signal = pyqtSignal(str)
    refresh_signal = pyqtSignal(int)

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Admin Panel')
        self.setGeometry(650, 350, 1500, 1000)

        # 创建主布局
        main_layout = QHBoxLayout(self)
        left_layout = QVBoxLayout()
        right_layout = QVBoxLayout()

        # 左侧部分：总消息数标签和统计图
        self.total_messages_label = QLabel('总消息数: 0')
        self.total_messages_label.setAlignment(Qt.AlignCenter)
        self.total_messages_label.setFixedHeight(50)

        self.canvas = dv.MplCanvas(self, width=5, height=4, dpi=100)

        left_layout.addWidget(self.total_messages_label)
        left_layout.addWidget(self.canvas)

        # 右侧部分：新增用户按钮和用户列表
        self.add_user_button = QPushButton('新增用户')
        self.add_user_button.setFixedHeight(40)
        self.refresh_button = QPushButton('刷新')
        self.refresh_button.setFixedHeight(40)
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.add_user_button)
        button_layout.addWidget(self.refresh_button)

        self.user_table = QTableWidget()
        self.user_table.setColumnCount(4)
        self.user_table.setHorizontalHeaderLabels(['用户ID', '已发送条数','限制消息数', '最后活动日期'])
        self.user_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)    # 自动调整列宽
        self.user_table.setContextMenuPolicy(Qt.CustomContextMenu)                      # 开启上下文菜单
        
        right_layout.addLayout(button_layout)
        right_layout.addWidget(self.user_table)

        # 添加到主布局
        main_layout.addLayout(left_layout, 5)
        main_layout.addLayout(right_layout, 5)

        self.setLayout(main_layout)

        # 上下文菜单动作
        self.user_table.customContextMenuRequested.connect(self.open_context_menu)
        self.add_user_button.clicked.connect(self.open_add_user_dialog)
        self.refresh_button.clicked.connect(self.refresh)


    def set_total_messages(self, total):
        self.total_messages_label.setText(f'总消息数: {total}')

    def update_canvas(self, data):
        # 清除原有canvas
        self.canvas.ax.clear()
        self.canvas.draw_chart(data)
        self.canvas.draw()

    def populate_user_table(self, users):
        self.user_table.setRowCount(len(users))
        for row, user in enumerate(users):
            last_active = datetime.strptime(user['last_active'], '%a, %d %b %Y %H:%M:%S %Z')    # 转换为datetime对象
            formatted_last_active = last_active.strftime('%Y-%m-%d %H:%M:%S')

            username=QTableWidgetItem(str(user['username']))
            message_count=QTableWidgetItem(str(user['message_count']))
            limit=QTableWidgetItem('未限制' if user['user_limit'] == -9999 else str(user['user_limit']))
            last_active=QTableWidgetItem(formatted_last_active)

            username.setFlags(Qt.ItemIsEnabled)   # 设置为不可编辑
            message_count.setFlags(Qt.ItemIsEnabled)
            limit.setFlags(Qt.ItemIsEnabled)
            last_active.setFlags(Qt.ItemIsEnabled)

            username.setTextAlignment(Qt.AlignCenter)  # 居中对齐
            message_count.setTextAlignment(Qt.AlignCenter)
            limit.setTextAlignment(Qt.AlignCenter)
            last_active.setTextAlignment(Qt.AlignCenter)

            self.user_table.setItem(row, 0, username)
            self.user_table.setItem(row, 1, message_count)
            self.user_table.setItem(row, 2, limit)
            self.user_table.setItem(row, 3, last_active)

    def open_context_menu(self, position):
        menu = QMenu()
        
        # 获取AiChatClient的路径
        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        limit_action = QAction('限制', self)
        # limit_action.setIcon(QIcon('AiChatClient/resources/icons/limit.png'))   # 这个路径是取决于工作目录的，如果工作目录不是AiChatSystem，需要修改路径
        limit_action.setIcon(QIcon(root_dir + '/resources/icons/limit.png'))
        limit_action.triggered.connect(self.limit_user)
        menu.addAction(limit_action)

        delete_action = QAction('删除', self)
        delete_action.setIcon(QIcon(root_dir + '/resources/icons/delete.png'))
        delete_action.triggered.connect(self.delete_user)
        menu.addAction(delete_action)

        menu.exec_(self.user_table.viewport().mapToGlobal(position))

    def limit_user(self):
        current_row = self.user_table.currentRow()
        if current_row >= 0:
            user_name = self.user_table.item(current_row, 0).text()
            limit, ok = QInputDialog.getInt(self, '限制用户', '请输入消息限制条数:')
            if ok:
                if limit < 0 and self.user_table.item(current_row, 2).text()!= '未限制':
                    reply=QMessageBox.question(self, '确认', '请确认是否要解除限制？', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                    if reply == QMessageBox.Yes:
                        self.limit_user_signal.emit(user_name, -9999)
                    return
                elif limit < 0 and self.user_table.item(current_row, 2).text() == '未限制':
                    QMessageBox.warning(self, '提示', '用户未被限制！')
                    return
                elif limit >=0 and self.user_table.item(current_row, 2).text()=='未限制':
                    self.limit_user_signal.emit(user_name, limit)
                elif limit == int(self.user_table.item(current_row, 2).text()):
                    QMessageBox.warning(self, '提示', '限制数未改变！')
                    return

    def delete_user(self):
        current_row = self.user_table.currentRow()
        if current_row >= 0:
            user_name = self.user_table.item(current_row, 0).text()
            self.delete_user_signal.emit(user_name)

    def open_add_user_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle('新增用户')

        layout = QFormLayout(dialog)

        name_input = QLineEdit()
        password_input = QLineEdit()
        confirm_password_input = QLineEdit()
        password_input.setEchoMode(QLineEdit.Password)
        confirm_password_input.setEchoMode(QLineEdit.Password)

        layout.addRow('用户名:', name_input)
        layout.addRow('密码:', password_input)
        layout.addRow('确认密码:', confirm_password_input)

        buttons = QHBoxLayout()
        add_button = QPushButton('添加')
        cancel_button = QPushButton('取消')
        buttons.addWidget(add_button)
        buttons.addWidget(cancel_button)

        layout.addRow(buttons)

        add_button.clicked.connect(lambda: self.add_user(dialog, name_input.text(), password_input.text(), confirm_password_input.text()))
        cancel_button.clicked.connect(dialog.reject)

        dialog.exec_()

    def add_user(self, dialog, user_name, password, confirm_password):
        if password != confirm_password:
            QMessageBox.warning(self, '错误', '密码不匹配！')
            return

        self.add_user_signal.emit({'name': user_name, 'password': password})
        dialog.accept()

    def refresh(self):
        self.refresh_signal.emit(1)

    def show_error(self, message):
        error_dialog = QMessageBox()
        error_dialog.setIcon(QMessageBox.Critical)
        error_dialog.setText(message)
        error_dialog.setWindowTitle('Error')
        error_dialog.exec_()