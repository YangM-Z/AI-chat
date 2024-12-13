from flask import Flask, request, jsonify
from flask_cors import CORS
import asyncio
import websockets
import pymysql
import json
import threading
from functools import partial

app = Flask(__name__)
CORS(app)


# 配置数据库连接
db = pymysql.connect(
    host='localhost',       # 数据库地址
        port=3306,          # 数据库端口
        user='',            # 数据库用户名
        passwd='',          # 数据库密码
        db='AiChatDB',      # 数据库名   
        charset='utf8mb4'
)

# 定义一个通用的数据库查询方法
def query_db(query, args=(), one=False):
    cursor = db.cursor(pymysql.cursors.DictCursor)
    cursor.execute(query, args)
    result = cursor.fetchall()
    cursor.close()
    return (result[0] if result else None) if one else result

# 定义一个通用的数据库执行方法
def execute_db(query, args=()):
    cursor = db.cursor()
    cursor.execute(query, args)
    db.commit()
    cursor.close()

# 获取总消息数
@app.route('/total_messages_count', methods=['GET'])
def get_total_messages_count():
    result = query_db('SELECT SUM(total_messages) as total_messages FROM user_statistics')
    if result[0]['total_messages'] is None:
        return jsonify({'total_messages': 0})
    return jsonify(result[0])

# 获取消息条数最多的前五名用户数据
@app.route('/top_users', methods=['GET'])
def get_top_users():
    result = query_db('SELECT username, total_messages FROM users u JOIN user_statistics us ON u.id = us.user_id WHERE us.delete_flag = FALSE ORDER BY total_messages DESC LIMIT 5')
    return jsonify({'top_users': result})

# 获取用户活跃度列表
@app.route('/users_activity_list', methods=['GET'])
def get_users_activity_list():
    result = query_db('SELECT u.username as username, us.total_messages as message_count, us.last_active, us.user_limit FROM users u JOIN user_statistics us ON u.id = us.user_id WHERE us.delete_flag = FALSE ORDER BY us.last_active DESC')
    return jsonify({'users_activity': result})

# 获取用户已发送消息数量
@app.route('/user_message_count', methods=['GET'])
def get_user_message_count():
    user_id = request.args.get('user_id')
    result = query_db('SELECT total_messages as message_count FROM user_statistics WHERE user_id = %s', [user_id], one=True)
    return jsonify(result)

# 获取用户消息限制数量
@app.route('/user_limit', methods=['GET'])
def get_user_limit():
    user_id = request.args.get('user_id')
    result = query_db('SELECT user_limit FROM user_statistics WHERE user_id = %s', [user_id], one=True)
    return jsonify(result)

# 获取用户会话列表
@app.route('/user_sessions_list', methods=['GET'])
def get_user_sessions_list():
    user_id = request.args.get('user_id')
    result = query_db('SELECT id, session_name as name, last_active FROM sessions WHERE user_id = %s ORDER BY last_active DESC', [user_id])
    if not result :
        return jsonify({'sessions_list':[]})
    return jsonify({'sessions_list': result})

# 获取会话聊天记录
@app.route('/chat_history', methods=['GET'])
def get_chat_history():
    session_id = request.args.get('session_id')
    result = query_db('SELECT sender, message_text as message FROM messages WHERE session_id = %s ORDER BY created_at', [session_id])
    if not result:
        return jsonify({'chat_history': []})
    return jsonify({'chat_history': result})

# 登录验证
@app.route('/login', methods=['POST'])
def get_login_status():
    data = request.get_json()
    username = data['username']
    password = data['password']
    user = query_db('SELECT id, role FROM users WHERE username = %s AND password = %s AND delete_flag = FALSE', [username, password], one=True)
    if user:
        if user['role'] == 'admin':
            return jsonify({'status': 2, 'user_id': ''})
        else:
            return jsonify({'status': 1, 'user_id': user['id']})
    return jsonify({'status': 0, 'user_id': ''})

# 创建新用户
@app.route('/create_user', methods=['POST'])
def create_new_user():
    data = request.get_json()
    user_id = data['user_id']
    username = data['username']
    password = data['password']
    role = data.get('role', 'user')  # 默认角色为'user'，如果提供了role则使用提供的角色
    
    existing_user = query_db('SELECT id FROM users WHERE username = %s', [username], one=True)
    if existing_user:
        return jsonify({'status': 0})
    # 调用存储过程创建新用户
    execute_db('CALL create_user_proc(%s, %s, %s, %s)', [user_id, username, password, role])
    return jsonify({'status': 1})

# 限制用户消息数
@app.route('/limit_user_message', methods=['POST'])
def limit_user_message():
    data = request.get_json()
    username = data['user_name']
    limit = data['limit']
    # 获取用户ID
    user = query_db('SELECT id FROM users WHERE username = %s', [username], one=True)
    if not user:
        return jsonify({'status': False})
    user_id = user['id']
    
    # 更新用户消息限制
    execute_db('UPDATE user_statistics SET user_limit = %s WHERE user_id = %s', [limit, user_id])
    return jsonify({'status': True})

# 删除用户
@app.route('/delete_user', methods=['POST'])
def delete_user():
    data = request.get_json()
    username = data['user_name']
    print(f"prepare to delete_user: {username}")
    # 获取用户ID
    user = query_db('SELECT id FROM users WHERE username = %s', [username], one=True)
    if not user:
        print(f"{username} not found")
        return jsonify({'status': False})
    user_id = user['id']
    cursor = db.cursor()
    cursor.callproc('delete_user_proc', [user_id])
    print(f"successfully deleted user: {username} id: {user_id}")
    db.commit()
    cursor.close()
    return jsonify({'status': True})

# 创建新会话
@app.route('/create_session', methods=['POST'])
def create_new_session():
    data = request.get_json()
    user_id = data['user_id']
    session_name = data['session_name']
    execute_db('INSERT INTO sessions (user_id, session_name) VALUES (%s, %s)', [user_id, session_name])
    session_id = query_db('SELECT LAST_INSERT_ID() as session_id', one=True)
    return jsonify(session_id)

# 重命名会话
@app.route('/rename_session', methods=['POST'])
def rename_session():
    data = request.get_json()
    session_id = data['session_id']
    new_name = data['new_name']
    execute_db('UPDATE sessions SET session_name = %s WHERE id = %s', [new_name, session_id])
    return jsonify({'status': True})

# 删除会话
@app.route('/delete_session', methods=['POST'])
def delete_session():
    data = request.get_json()
    session_id = data['session_id']
    execute_db('DELETE FROM messages WHERE session_id = %s', [session_id])
    execute_db('DELETE FROM sessions WHERE id = %s', [session_id])
    return jsonify({'status': True})

# 连接到chatGPT_API
async def connect_to_chatGPT_API(uri):
    async with websockets.connect(uri) as chatGPT_websocket:
        print("Connected to chatGPT_API")
        return chatGPT_websocket

# 开启客户端websocket服务
async def start_client_websocket_server(host, port, a_chatGPT_websocket):
    server = await websockets.serve(partial(handle_client, chatGPT_websocket=a_chatGPT_websocket), host, port)
    print("client websocket server started")
    await server.wait_closed()

# 循环开启客户端websocket服务并处理异常
async def run_client_websocket_server(host,port,chatGPT_websocket):
    while True:
        try:
            await start_client_websocket_server(host,port,chatGPT_websocket)
        except Exception as e:
            print(f"Server error: {e}")
            await asyncio.sleep(0.1)  # 遇到异常时等待0.1秒后重试

# 处理客户端websocket连接的消息接发
async def handle_client(client_websocket, path, chatGPT_websocket):
    try:
        print("Client websocket connected")
        async for data in client_websocket:
            # data应该是json序列化的字典：{'session_id':'xxx', 'message':'xxxxx'}
            print(f"Received from client: {data}")
            real_data=json.loads(data)
            session_id=real_data['session_id']
            message=real_data['message']
            # 添加消息到聊天记录
            execute_db('INSERT INTO messages (session_id, sender, message_text, created_at) VALUES (%s, %s, %s, CURRENT_TIMESTAMP)', [session_id, 'user', message])
            # 导出会话的全部聊天记录
            messages = query_db('SELECT sender, message_text FROM messages WHERE session_id = %s ORDER BY created_at', [session_id])
            # 转换为所需的列表格式
            chat_history = [
                {
                    "role": "system",
                    "content": "你是一个由OpenAI训练的大语言模型，能够帮助回答问题，提供信息，完成任务等。可靠且专业的AI助手。在用户没有要求的情况下，一般只用中文回答。"
                }
            ]
            for msg in messages:
                chat_history.append({
                    "role": msg['sender'],
                    "content": msg['message_text']
                })
            # 向chatGPT_API发送消息
            # await chatGPT_websocket.send(json.dumps(chat_history))###############这里有问题,debug不好,放弃了
            # print("Sent to chatGPT_API")
            # 接收chatGPT_API的模型
            # model = await chatGPT_websocket.recv()
            # print(f"Received model: {model}")
            # 将模型转发给客户端
            # await client_websocket.send(model)
            # 接收chatGPT_API的回复
            # replay = ""
            # async for replay_chunk in chatGPT_websocket:
            #     # 将回复片段不停转发给客户端
            #     await client_websocket.send(replay_chunk)
            #     replay += replay_chunk
            #     if replay_chunk == "_END_":
            #         # 结束循环读取chatGPT_websocket里的数据片段
            #         break
            ############################################# 模拟gpt ##########################################
            model = "chatGPT-4o"
            await client_websocket.send("chatGPT-4o")
            replay = "test"
            await client_websocket.send(replay)
            await client_websocket.send("_END_")
            ############################################# 模拟gpt ##########################################
            # 将回复插入数据库
            execute_db('INSERT INTO messages (session_id, sender, message_text, created_at) VALUES (%s, %s, %s, CURRENT_TIMESTAMP)', [session_id, model, replay])
    except Exception as e:
        print(f"Error: {e}")

def start_flask_app():
    # 启动flask服务
    print("Flask server started")
    app.run(host='0.0.0.0', port=8087)
    # app.run(host='localhost',port=8087)

if __name__ == '__main__':

    # 创建和chatGPT_API的websocket连接,端口为8089
    chatGPT_websocket=asyncio.run(connect_to_chatGPT_API(uri = "ws://localhost:8089"))

    
    # 启动 Flask 服务器在一个单独的线程中
    flask_thread = threading.Thread(target=start_flask_app)
    flask_thread.start()

    # 开启循环等待客户端连接的websocket,端口为8088
    asyncio.run(run_client_websocket_server("0.0.0.0", 8088,chatGPT_websocket))
    # asyncio.run(run_client_websocket_server("localhost", 8088,chatGPT_websocket))