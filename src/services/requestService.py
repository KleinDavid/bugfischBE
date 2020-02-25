from models.ServerAction import ServerAction
from services.actionService import ActionService
import json
from rest_framework.response import Response
from json import JSONEncoder

from services.configService import ConfigService


class RequestService:
    actionService = ActionService.getInstance()
    configService = ConfigService.getInstance()

    @staticmethod
    def get_data_from_request(request):
        return json.loads(request.body.decode('utf-8'))['data']

    def handleExecuteAction(self, request):
        self.configService.initConfig()
        data = self.get_data_from_request(request)
        server_action = ServerAction
        server_action.Type = data["Type"]
        server_action.Input = data["Input"]
        server_action.Name = data["Name"]
        server_action.Token = data["Token"]
        server_action.Id = data["Id"]
        return Response(json.loads(MyEncoder().encode(self.actionService.executeAction(server_action))))


class MyEncoder(JSONEncoder):
    def default(self, o):
        return o.__dict__
