'''
文件名: getData.py
描述: 所有后端数据通过这个文件中的方法获取
'''

import requests
from untils.common import md5

BASE_URL = "http://localhost:8087"

def get_total_messages_count():
    """
    获取总消息数

    Args:
        None

    Returns:
        int: 总消息数

    Raises:
        networkError: 网络错误
    """
    response = requests.get(f"{BASE_URL}/total_messages_count")
    if response.status_code == 200:
        return response.json().get('total_messages')
    else:
        raise Exception("Network Error")

def get_top_users():
    """
    获取消息条数最多的前五名用户数据

    Args:
        None
    
    Returns:
        list: 前五名用户数据，格式为[{'username':'用户名', 'total_messages':'用户已发送消息条数'}, ...]
        应当按照消息数从高到低排序
    
    Raises:
        networkError: 网络错误
    """
    response = requests.get(f"{BASE_URL}/top_users")
    if response.status_code == 200:
        return response.json().get('top_users')
    else:
        raise Exception("Network Error")

def get_users_activity_list():
    """
    获取用户活跃度列表

    Args:
        None
    
    Returns:
        list: 用户活跃度列表，格式为[{'username':'用户名', 'message_count':'用户已发送消息条数','limit':'用户限制条数','last_active':'最后活跃时间'}, ...]
        应当按照最后活跃时间排序，最近活跃的用户排在最前面

    Raises:
        networkError: 网络错误
    """
    response = requests.get(f"{BASE_URL}/users_activity_list")
    if response.status_code == 200:
        return response.json().get('users_activity')
    else:
        raise Exception("Network Error")

def get_user_message_count(user_id):
    """
    获取用户已发送消息数量

    Args:
        user_id (int): 用户ID
    
    Returns:
        int: 用户已发送消息数量
    
    Raises:
        networkError: 网络错误
    """
    response = requests.get(f"{BASE_URL}/user_message_count", params={'user_id': user_id})
    if response.status_code == 200:
        return response.json().get('message_count')
    else:
        raise Exception("Network Error")

def get_user_limit(user_id):
    """
    获取用户消息限制数量

    Args:
        user_id (int): 用户ID
    
    Returns:
        int: 用户消息限制数量
    
    Raises:
        networkError: 网络错误
    """
    response = requests.get(f"{BASE_URL}/user_limit", params={'user_id': user_id})
    if response.status_code == 200:
        return response.json().get('user_limit')
    else:
        raise Exception("Network Error")

def get_user_sessions_list(user_id):
    """
    获取用户会话列表

    Args:
        user_id (int): 用户ID
    
    Returns:
        list: 用户会话列表，格式为[{'id':'会话id','name':'会话名','last_active':'该会话最后活跃时间'} ,...]
        应当按照最后活跃时间排序，最近活跃的会话排在最前面
    
    Raises:
        networkError: 网络错误
    """
    response = requests.get(f"{BASE_URL}/user_sessions_list", params={'user_id': user_id})
    if response.status_code == 200:
        return response.json().get('sessions_list')
    else:
        raise Exception("Network Error")
    

def get_chat_history(session_id):
    """
    获取会话聊天记录

    Args:
        session_id (int): 会话ID
    
    Returns:
        list: 会话聊天记录，格式为[{'sender': 'user', 'message': '消息内容'}, ...]
    
    Raises:
        networkError: 网络错误
    """
    response = requests.get(f"{BASE_URL}/chat_history", params={'session_id': session_id})
    if response.status_code == 200:
        return response.json().get('chat_history')
    else:
        raise Exception("Network Error")

def get_login_status(username, password):
    """
    获取登录状态,将用户名和md5加密后的密码发送给后端

    Args:
        username (str): 用户名
        password (str): 密码
    
    Returns:
        int: 管理员登录成功返回2和'',用户登录成功返回1和'user_id',用户名或密码错误返回0和''
    
    Raises:
        networkError: 网络错误
    """
    response = requests.post(f"{BASE_URL}/login", json={
        'username': username,
        'password': md5(password)
    })
    if response.status_code == 200:
        return response.json().get('status'), response.json().get('user_id')
    else:
        raise Exception("Network Error")