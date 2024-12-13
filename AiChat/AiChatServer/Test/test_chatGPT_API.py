import asyncio
import websockets
import json

async def test():
    uri = "ws://localhost:8089"
    async with websockets.connect(uri) as websocket:
        # 构造测试消息
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Tell me a joke."}
        ]
        await websocket.send(json.dumps(messages))

        # 接收和打印服务器响应
        async for message in websocket:
            print(message)
            if message == "_END_":
                break

# 运行测试
asyncio.get_event_loop().run_until_complete(test())