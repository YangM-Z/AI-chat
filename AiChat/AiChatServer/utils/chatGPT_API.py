'''
文件名: chatGPT_API.py
描述: 通过OpenAI的API调用GPT模型进行聊天
备注: 生产服务器上需要通过proxychains运行该脚本,以将http请求转为socks5协议,再通过ssr的socket5代理转发到OpenAI的API
参数: 需要openai的api_key, 以及指定的模型名称，前往官网注册账号获取
'''


import asyncio
import websockets
import json
from openai import OpenAI

'''
1,000 tokens is about 750 words.

model list:
gpt-4o-2024-05-13:          128K context      October 2023 knowledge cutoff     US$5.00/1M input tokens     US$15.00/1M output tokens
gpt-4-turbo-2024-04-09:     128K context      October 2023 knowledge cutoff     
gpt-4-0613:                   8K context    September 2021 knowledge cutoff     
gpt-3.5-turbo-0125:          16k context    September 2021 knowledge cutoff     US$0.50/1M input tokens     US$1.50/1M output tokens
'''
use_model = "gpt-4o"    # 请填入模型名称
ws_uri = "localhost"    # 请填入服务器地址
ws_port = 8080          # 请填入服务器端口
openAI_api_key = ''     # 请填入openai的api_key

############################## 以下无需修改 #################################

client = OpenAI(
    api_key= openAI_api_key
)

async def chatGPT_API(websocket, path):
    try:
        async for message in websocket:
            messages_data = json.loads(message)
            stream = client.chat.completions.create(
                model = use_model,
                messages=messages_data,
                stream=True,
            )
            await websocket.send(use_model)
            for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    await websocket.send(chunk.choices[0].delta.content)
                    print(chunk.choices[0].delta.content, end="")
            await websocket.send("_END_")
            print("\n")
    except websockets.ConnectionClosed:
        print("Connection with client closed")
    except Exception as e:
        print(f"Error: {e}")

start_server = websockets.serve(chatGPT_API, ws_uri, ws_port)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()