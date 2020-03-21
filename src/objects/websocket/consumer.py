from json import JSONEncoder

from channels.generic.websocket import WebsocketConsumer


class Consumer(WebsocketConsumer):

    async def connect(self):
        ''

    async def websocket_connect(self, event):
        ''

    async def websocket_receive(self, event):
        await self.send({
            "type": "websocket.send",
            "text": event["text"],
        })

    async def websocket_disconnect(self, message):
        print(message)



class MyEncoder(JSONEncoder):
    def default(self, o):
        return o.__dict__
