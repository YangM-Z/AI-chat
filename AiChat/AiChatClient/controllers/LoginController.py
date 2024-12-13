from PyQt5.QtCore import pyqtSlot
from threading import Thread
from PyQt5.QtWidgets import QMessageBox
from views.LoginView import LoginView
from controllers.ChatController import ChatController
from controllers.AdminController import AdminController
import untils.getData as getData

class LoginController:
    def __init__(self):
        self.view = LoginView()
        self.view.login_button.clicked.connect(self.handle_login)
        self.adminController = None
        self.chatController = None

    def show(self):
        self.view.show()

    def handle_login(self):
        username = self.view.username_input.text()
        password = self.view.password_input.text()

        try:
            login_status,userId = getData.get_login_status(username, password)
        except Exception as e:
            self.view.show_error(str(e)+'\nfrom getData.get_login_status()')
            return
        if login_status == 2:
            print('管理员登录成功')
            self.adminController = AdminController()
            self.adminController.show()
            self.view.close()

        elif login_status == 1:
            print(f'用户{userId}登录成功')
            self.chatController = ChatController(userId)
            self.chatController.show()
            self.view.close()
        else:
            QMessageBox.information(self.view, '错误', '用户名或密码错误')