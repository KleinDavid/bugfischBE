import asyncio
import websockets
# from services.requestService import RequestService


import sys
print(sys.path)

async def response(websocket, path):
    message = await websocket.recv()
    print(f'have message {message}')
    # requestService.handleExecuteAction(message)
    await websocket.send('danke')


start_server = websockets.serve(response, 'localhost', 1111)
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()

