from PyQt5.QtWidgets import QMessageBox, QListWidgetItem, QTextBrowser
from datetime import datetime
import asyncio
import websocket
import json
import markdown2
from views.ChatView import ChatView
import untils.getData as getData
import untils.postData as postData

class ChatController:
    def __init__(self, userId):
        self.view = ChatView()
        self.view.new_chat_button.clicked.connect(self.create_new_chat)     # 按下新建聊天按钮时触发create_new_chat
        self.view.send_button.clicked.connect(self.send_message)     # 按下发送按钮时触发send_message
        self.view.sessions_list.itemClicked.connect(self.load_session)      # 选中会话时触发load_session
        self.view.rename_session_signal.connect(self.rename_session)        # 重命名会话信号
        self.view.remove_session_signal.connect(self.remove_session)        # 删除会话信号

        self.current_user_id = userId       # 当前用户的ID
        self.sessionsList = []              # 存储用户的会话列表
        self.current_session_id = None      # 当前会话的ID
        self.sent_message_count = 0         # 当前用户已发送消息数
        self.message_limit = -9999          # 当前用户的消息限制数
        self.webSocket = None               # 用于连接到聊天服务器的WebSocket
        
        self.refresh_sessions_list()                            # 刷新会话列表

        # 连接到聊天服务器的WebSocket
        try:
            # self.webSocket=asyncio.run(self.connect_server_websocket(uri = "ws://121.36.74.190:8088"))
            self.webSocket = websocket.create_connection("ws://121.36.74.190:8088")
            print("Connected to server websocket")
        except Exception as e:
            self.view.show_error(str(e)+'\nfrom websocket_connect')
            return

    def show(self):
        self.view.show()
    
    def refresh_sessions_list(self):
        try:
            self.sessionsList = getData.get_user_sessions_list(self.current_user_id)                # 获取用户会话列表
        except Exception as e:
            self.view.show_error(str(e)+'\nfrom getData.get_user_sessions_list()')
            return
        self.view.sessions_list.clear()                                                             # 清空会话列表
        for session in self.sessionsList:
            last_active = datetime.strptime(session['last_active'], '%a, %d %b %Y %H:%M:%S %Z')     # 转换为datetime对象
            self.view.add_session(session['name'],last_active)                                      # 添加会话到会话列表
        self.refresh_message_count()                                                                # 刷新消息计数

    def refresh_message_count(self):
        try:
            self.sent_message_count = getData.get_user_message_count(self.current_user_id)  # 当前用户已发送消息数
            self.message_limit = getData.get_user_limit(self.current_user_id)               # 当前用户的消息限制数
        except Exception as e:
            self.view.show_error(str(e)+'\nfrom getData.get_user_message_count()')
            return
        self.view.update_message_count(self.sent_message_count, self.message_limit)         # 更新消息计数视图

    def create_new_chat(self):
        session_name = f'会话 {len(self.sessionsList) + 1}'
        try:
            new_session_id = postData.create_new_session(self.current_user_id, session_name)
        except Exception as e:
            self.view.show_error(str(e)+'\nfrom postData.create_new_session()')
            return
        self.refresh_sessions_list()
        if new_session_id == None:
            QMessageBox.warning(self.view, '未知错误', '会话创建失败')
            return
        self.current_session_id = new_session_id
        self.view.chat_history.clear()


    def send_message(self):
        message = self.view.message_input.text()
        if message and self.current_session_id:
            if self.message_limit != -9999 and self.sent_message_count >= self.message_limit:
                QMessageBox.warning(self.view, '错误', '已达到消息限制数,请联系管理员增加额度')
                return
            
            self.view.add_chat_history('user', message)  # 在界面上显示用户发送的消息
            self.view.clear_message_input()             # 清空输入框
            self.view.send_button.setEnabled(False)     # 禁用发送按钮
            self.webSocket.send(json.dumps({'session_id':self.current_session_id, 'message':message}))  # 向服务器发送消息
            contentText = ""
            model = self.webSocket.recv()
            contentText += model
            contentText += ':\n'
            item = QListWidgetItem()
            content = QTextBrowser()
            content.setHtml(markdown2.markdown(contentText, extras=['tables', 'fenced-code-blocks']))
            item.setSizeHint(content.sizeHint())
            self.view.chat_history.addItem(item)
            self.view.chat_history.setItemWidget(item, content)

            while True:
                replay_chunk = self.webSocket.recv()   
                contentText += replay_chunk
                content.setHtml(markdown2.markdown(contentText, extras=['tables', 'fenced-code-blocks']))
                if replay_chunk == "_END_":
                    # 结束循环读取chatGPT_websocket里的数据片段
                    break

            self.view.send_button.setEnabled(True)      # 启用发送按钮
            

    def load_session(self, item):
        self.current_session_id = self.sessionsList[self.view.sessions_list.row(item)]['id']
        self.view.chat_history.clear()
        try:
            current_session_content = getData.get_chat_history(self.current_session_id)
        except Exception as e:
            self.view.show_error(str(e)+'\nfrom getData.get_chat_history()')
            return
        for message in current_session_content:
            self.view.add_chat_history(message['sender'], message['message'])

    def rename_session(self, item, new_name):
        session_id = self.sessionsList[self.view.sessions_list.row(item)]['id']
        try:
            res=postData.rename_session(session_id, new_name)
        except Exception as e:
            self.view.show_error(e+'\nfrom postData.rename_session()')
            return
        if res:
            self.refresh_sessions_list()
        else:
            QMessageBox.warning(self.view, '未知错误', '重命名失败')

    def remove_session(self, item):
        session_id = self.sessionsList[self.view.sessions_list.row(item)]['id']
        try:
            res=postData.delete_session(session_id)
        except Exception as e:
            self.view.show_error(str(e)+'\nfrom postData.delete_session()')
            return
        if res:
            self.refresh_sessions_list()
        else:
            QMessageBox.warning(self.view, '未知错误', '删除失败')

    # async def connect_server_websocket(self, uri):
    #     async with websocket.connect(uri) as server_websocket:
    #         print("Connected to server websocket")
    #         return server_websocket 
