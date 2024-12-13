'''
文件名：postData.py
描述：所有需要向后端发送数据的操作通过这个文件中的方法实现
'''

import requests
from untils.common import md5

BASE_URL = "http://localhost:8087"

def create_new_user(user_id,username, password):
    """
    创建新用户,将userId,用户名和md5加密后的密码发送给后端
    通过username检查用户名是否已存在

    Args:
        userId (str): 用户ID
        username (str): 用户名
        password (str): 密码

    Returns:
        int: 创建成功返回1,用户名已存在则返回0

    Raises:
        networkError: 网络错误
    """
    response = requests.post(
        f"{BASE_URL}/create_user",
        json={
            'user_id': user_id,
            'username': username,
            'password': md5(password)
        }
    )
    if response.status_code == 200:
        return response.json().get('status')
    else:
        raise Exception("Network Error")

def limit_user_message(user_name, limit):
    """
    限制用户消息数

    Args:
        user_id (str): 用户名
        limit (int): 限制消息数,范围为正整数或-9999(解除限制)

    Returns:
        bool: 限制成功返回True

    Raises:
        networkError: 网络错误
    """
    response = requests.post(
        f"{BASE_URL}/limit_user_message",
        json={
            'user_name': user_name,
            'limit': limit
        }
    )
    if response.status_code == 200:
        return response.json().get('status')
    else:
        raise Exception("Network Error")

def delete_user(user_name):
    """
    删除用户以及该用户的所有会话和消息记录，但不应减少总消息计数

    Args:
        user_id (int): 用户ID

    Returns:
        bool: 删除成功返回True

    Raises:
        networkError: 网络错误
    """
    response = requests.post(
        f"{BASE_URL}/delete_user",
        json={
            'user_name': user_name
        }
    )
    if response.status_code == 200:
        return response.json().get('status')
    else:
        raise Exception("Network Error")


def create_new_session(user_id, session_name):
    """
    创建新会话

    Args:
        user_id (int): 用户ID
        session_name (str): 会话名

    Returns:
        int: 创建成功返回会话ID

    Raises:
        networkError: 网络错误
    """
    response = requests.post(
        f"{BASE_URL}/create_session",
        json={
            'user_id': user_id,
            'session_name': session_name
        }
    )
    if response.status_code == 200:
        return response.json().get('session_id')
    else:
        raise Exception("Network Error")

def rename_session(session_id, new_name):
    """
    重命名会话

    Args:
        session_id (int): 会话ID
        new_name (str): 新会话名

    Returns:
        bool: 重命名成功返回True

    Raises:
        networkError: 网络错误
    """
    response = requests.post(
        f"{BASE_URL}/rename_session",
        json={
            'session_id': session_id,
            'new_name': new_name
        }
    )
    if response.status_code == 200:
        return response.json().get('status')
    else:
        raise Exception("Network Error")

def delete_session(session_id):
    """
    删除会话

    Args:
        session_id (int): 会话ID

    Returns:
        bool: 删除成功返回True

    Raises:
        networkError: 网络错误
    """
    response = requests.post(
        f"{BASE_URL}/delete_session", 
        json={
            'session_id': session_id
        }
    )
    if response.status_code == 200:
        return response.json().get('status')
    else:
        raise Exception("Network Error")
    
def websocket_connect():
    """
    与服务器建立websocket连接

    Args:
        None

    Returns:
        WebSocket: 返回websocket对象

    Raises:
        networkError: 网络错误
    """
    # 不在这里实现，因为websocket需要在整个程序中共享，而不是每次发送消息都重新连接

def send_user_message(websocket, session_id, message):
    """
    发送用户消息,并返回服务器响应结果
    后端应该根据会话ID查找会话,然后将消息存入数据库,将该会话最后50条聊天记录合并发送给chatGPT,并返回一个ChatGPT回复

    Args:
        websocket (WebSocket): websocket对象
        session_id (int): 会话ID
        message (str): 消息内容

    Returns:
        Respone: 返回服务器响应结果

    Raises:
        networkError: 网络错误
    """
    # 不在这里实现，因为websocket需要在整个程序中共享，而不是每次发送消息都重新连接
    