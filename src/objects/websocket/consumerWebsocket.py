import json
import random
import string


class CostumerWebsocket:

    def __init__(self):
        self.readyState = False
        self.websocket = ''
        with open('config/config.json', 'r') as config_file:
            content = config_file.read()
            content = json.loads(content)
            self.path = 'ws://' + content['websocket-ip'] + content['websocket-port'] + '/' + self.__getRandomString__()

    def sendMessage(self, message):
        self.websocket.send(message)

    @staticmethod
    def __getRandomString__():
        letters = string.ascii_letters + string.digits
        return ''.join(random.choice(letters) for i in range(40))
