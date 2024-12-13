from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QListWidget, QListWidgetItem, QTextBrowser, QLineEdit, QLabel, QInputDialog, QMessageBox, QMenu, QAction, QSizePolicy
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QIcon
import markdown2
import os

class SessionItem(QWidget):
    def __init__(self, session_name, last_active, parent=None):
        super(SessionItem, self).__init__(parent)

        # 创建水平布局
        layout = QHBoxLayout(self)

        # 创建会话名称标签
        name_label = QLabel(session_name)
        name_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

        # 创建最后活动时间标签
        last_active_label = QLabel(last_active)
        last_active_label.setAlignment(Qt.AlignRight)

        # 将标签添加到布局中
        layout.addWidget(name_label)
        layout.addWidget(last_active_label)

        # 设置布局
        self.setLayout(layout)

class ChatView(QWidget):
    # 定义信号，用于删除会话和重命名会话
    remove_session_signal = pyqtSignal(QListWidgetItem)
    rename_session_signal = pyqtSignal(QListWidgetItem, str)

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Chat Application')
        self.setGeometry(650, 350, 1500, 1000)

        # 创建主布局
        main_layout = QHBoxLayout(self)
        
        left_layout = QVBoxLayout()
        right_layout = QVBoxLayout()

        # 左侧部分：新建聊天按钮、会话列表和消息计数显示
        self.message_count_label_sent = QLabel('已发送消息: 0')
        self.message_count_label_limit = QLabel('限制条数: 未限制')
        self.message_count_label_sent.setAlignment(Qt.AlignCenter)
        self.message_count_label_limit.setAlignment(Qt.AlignCenter)
        self.message_count_label_sent.setFixedHeight(40)
        self.message_count_label_limit.setFixedHeight(40)

        self.new_chat_button = QPushButton('创建新聊天')
        self.new_chat_button.setFixedHeight(40)
        self.new_chat_button.setStyleSheet("border-radius: 10px; border: 1px solid black;")

        self.sessions_list = QListWidget()
        self.sessions_list.setStyleSheet("border: 1px solid black; border-radius: 10px;")
        self.sessions_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.sessions_list.customContextMenuRequested.connect(self.open_context_menu)

        left_layout.addWidget(self.message_count_label_sent)
        left_layout.addWidget(self.message_count_label_limit)
        left_layout.addWidget(self.new_chat_button)
        left_layout.addWidget(self.sessions_list)
        left_layout.setStretch(2, 8)  # 设置sessions_list占左侧布局80%的高度

        # 右侧部分：聊天记录和输入区域
        self.chat_history = QListWidget()

        self.message_input = QLineEdit()
        self.send_button = QPushButton('发送')

        input_layout = QHBoxLayout()
        input_layout.addWidget(self.message_input)
        input_layout.addWidget(self.send_button)

        right_layout.addWidget(self.chat_history)
        right_layout.addLayout(input_layout)

        # 添加到主布局
        main_layout.addLayout(left_layout, 2)  # 左侧占20%宽度
        main_layout.addLayout(right_layout, 8)  # 右侧占80%宽度

        self.setLayout(main_layout)

    def update_message_count(self, sent_count, limit_count):
        if limit_count != -9999:
            self.message_count_label_sent.setText(f'已发送消息: {sent_count}')
            self.message_count_label_limit.setText(f'限制条数: {limit_count}')
        else:
            self.message_count_label_sent.setText(f'已发送消息: {sent_count}')
            self.message_count_label_limit.setText(f'限制条数: 未限制')

    def add_session(self, session_name, last_active):
        # 将last_active格式化为YYYY-MM-DD形式
        formatted_last_active = last_active.strftime('%Y-%m-%d')

        item = QListWidgetItem(self.sessions_list)
        item_widget = SessionItem(session_name, formatted_last_active)
        item.setSizeHint(item_widget.sizeHint())
        self.sessions_list.addItem(item)
        self.sessions_list.setItemWidget(item, item_widget)

    def remove_session(self, item):
        session_name = item.text()
        reply = QMessageBox.question(self, '删除会话', f'确定删除会话 {session_name} 吗?', QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.remove_session_signal.emit(item)

    # def display_message(self, sender, message):
    #     if sender == 'user':
    #         formatted_message = f'<div style="text-align: right; color: blue;">user:<br>{message}</div>'
    #     else:
    #         formatted_message = f'<div style="text-align: left; color: green;">{sender}:<br>{markdown2.markdown(message)}</div>'
    #     self.chat_history.append(formatted_message)

    # 向聊天记录中添加一条消息
    def add_chat_history(self, sender, message):
        item = QListWidgetItem()
        content = QTextBrowser()
        contentText = f'{sender}:\n{message}'
        content.setHtml(markdown2.markdown(contentText, extras=['tables', 'fenced-code-blocks']))
        item.setSizeHint(content.sizeHint())
        self.chat_history.addItem(item)
        self.chat_history.setItemWidget(item, content)



    def clear_message_input(self):
        self.message_input.clear()

    def open_context_menu(self, position):
        menu = QMenu()

        # 获取AiChatClient的路径
        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        rename_action = QAction('重命名', self)
        rename_action.setIcon(QIcon(root_dir + '/resources/icons/rename.png'))
        rename_action.triggered.connect(lambda: self.rename_session_dialog(self.sessions_list.itemAt(position)))
        menu.addAction(rename_action)

        delete_action = QAction('删除', self)
        delete_action.setIcon(QIcon(root_dir + '/resources/icons/delete.png'))
        delete_action.triggered.connect(lambda: self.remove_session(self.sessions_list.itemAt(position)))
        menu.addAction(delete_action)

        menu.exec_(self.sessions_list.viewport().mapToGlobal(position))

    def rename_session_dialog(self, item):
        if item:
            new_name, ok = QInputDialog.getText(self, '重命名会话', '输入新的会话名称:')
            if ok and new_name:
                self.rename_session_signal.emit(item, new_name)

    def show_error(self, message):
        error_dialog = QMessageBox()
        error_dialog.setIcon(QMessageBox.Critical)
        error_dialog.setText(message)
        error_dialog.setWindowTitle('Error')
        error_dialog.exec_()

