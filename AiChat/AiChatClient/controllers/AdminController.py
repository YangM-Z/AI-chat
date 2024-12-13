from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QMessageBox
from views.AdminView import AdminView
import untils.getData as getData
import untils.postData as postData
import untils.common as common

class AdminController:
    def __init__(self):
        self.view = AdminView()
        self.view.add_user_signal.connect(self.add_user)
        self.view.refresh_signal.connect(self.refresh_data)
        self.view.limit_user_signal.connect(self.limit_user)
        self.view.delete_user_signal.connect(self.delete_user)

        self.total_messages = 0
        self.top_users = []
        self.users = []

        self.load_data()

    def show(self):
        self.view.show()

    def load_data(self):
        # 总消息计数
        try:
            self.total_messages = getData.get_total_messages_count()
        except Exception as e:
            self.view.show_error(str(e)+'\nfrom getData.get_total_messages_count()')
            return

        self.view.set_total_messages(self.total_messages)

        # 获取前五名用户数据用于绘图
        try:
            self.top_users = getData.get_top_users()
        except Exception as e:
            print(e)
            self.view.show_error(str(e)+'\nfrom getData.get_top_users()')
            return
        self.view.update_canvas(self.top_users)

        # 获取用户列表数据
        try:
            self.users = getData.get_users_activity_list()
        except Exception as e:
            print(e)
            self.view.show_error(str(e)+'\nfrom getData.get_users_activity_list()')
            return
        self.view.populate_user_table(self.users)

    def add_user(self, user_info):
        print(f'新增用户: {user_info}')
        try:
            res = postData.create_new_user(common.get_uuid(),user_info['name'], user_info['password'])
        except Exception as e:
            print(e)
            self.view.show_error(str(e)+'\nfrom postData.create_new_user()')
            return
        if res==1 :
            QMessageBox.information(self.view, '成功', '用户添加成功')
            self.refresh_data()
        else:
            QMessageBox.warning(self.view, '错误', '用户名已存在')

    def refresh_data(self):
        print('刷新数据')
        self.load_data()

    def limit_user(self, user_name, limit):
        print(f'限制用户 {user_name} 到 {limit} 条消息')
        try:
            res = postData.limit_user_message(user_name, limit)
        except Exception as e:
            print(e)
            self.view.show_error(str(e)+'\nfrom postData.limit_user_message()')
            return
        if res:
            QMessageBox.information(self.view, '成功', '更改用户限制成功')
            self.refresh_data()
        else:
            QMessageBox.warning(self.view, '未知错误', '无法更改用户限制')

    def delete_user(self, user_name):
        print(f'删除用户 {user_name}')
        try:
            res = postData.delete_user(user_name)
        except Exception as e:
            print(e)
            self.view.show_error(str(e)+'\nfrom postData.delete_user()')
            return
        if res:
            QMessageBox.information(self.view, '成功', '用户删除成功')
            self.refresh_data()
        else:
            QMessageBox.warning(self.view, '未知错误', '无法删除用户')