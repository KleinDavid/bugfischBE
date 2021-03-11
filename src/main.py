import asyncio
import websockets
from services.requestService import RequestService

requestService = RequestService()


async def response(websocket, path):
    message = await websocket.recv()
    print(f'have message {message}')
    req = requestService.handleExecuteAction(message)
    print('kkkk    '+req)
    await websocket.send(req)


start_server = websockets.serve(response, 'localhost', 1111)
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()

