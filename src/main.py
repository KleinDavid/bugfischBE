import asyncio
import websockets
from services.requestService import RequestService


requestService = RequestService()


async def response(websocket, path):
    message = await websocket.recv()
    req = requestService.handleExecuteAction(message)
    await websocket.send(req)


start_server = websockets.serve(response, 'localhost', 1111)
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()

