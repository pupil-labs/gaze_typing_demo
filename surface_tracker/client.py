import asyncio
import websockets

async def hello():
    async with websockets.connect("ws://localhost:8765") as websocket:
        # print("send hello")
        # await websocket.send("Hello world!")
        print("response: ", await websocket.recv())

asyncio.run(hello())