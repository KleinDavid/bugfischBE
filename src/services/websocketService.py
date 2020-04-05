import asyncio
import json


class WebsocketService:
    
    def __init__(self):
        self.websocket_list = []
    
    async def onMessage(self, websocket, path):
        self.websocket_list.append(websocket)
        async for message in websocket:
            for ws in self.websocket_list:
                await ws.send(message + path)

    def startServer(self):
        print()
        with open('config/config.json', 'r') as config_file:
            content = json.loads(config_file.read())
            # start_server = websockets.serve(self.onMessage, content['websocket-ip'].replace(':', ''), int(content['websocket-port']))
            # asyncio.get_event_loop().run_until_complete(start_server)
            # asyncio.get_event_loop().run_forever()
