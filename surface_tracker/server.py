import nest_asyncio
nest_asyncio.apply()

import asyncio
import json
import websockets
from marker_mapper import MarkerMapper



async def handler(websocket):
    mapper = MarkerMapper()
    while True:
        result = mapper()
        result = list(result.mapped_gaze.values())[0]
        if len(result) > 0:
            await asyncio.sleep(0.1)
            point = {"x": result[0].x, "y": result[0].y}
            # point = {"x": 200, "y": 200}
            print("Sending: ", point)
            await websocket.send(json.dumps(point))


async def main():
    async with websockets.serve(handler, "", 8001):
        await asyncio.Future()  # run forever


if __name__ == "__main__":
    asyncio.run(main())
    # await main()