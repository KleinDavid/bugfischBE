from models.ServerAction import ServerAction
from models.ServerResult import ServerResult
from objects.actionHandler import ActionHandler
from services.dataService import DataService
from services.loggingService import LoggingService
from services.sessionService import SessionService


class ActionService:
    dataService = DataService.getInstance()
    sessionService = SessionService.getInstance()
    actionResultData = {}
    loggingService = LoggingService()

    __instance = None

    @staticmethod
    def getInstance():
        if ActionService.__instance is None:
            ActionService()
        return ActionService.__instance

    def __init__(self):
        if ActionService.__instance is not None:
            raise Exception("This class is a singleton!")
        else:
            ActionService.__instance = self

    def executeAction(self, output_action):
        session = self.sessionService.getSessionByToken(output_action.Token)
        if session is None:
            output_action = ServerAction()
            output_action.Type = 'InitializeSessionAction'
            output_action.Input = {}
            output_action.Input['Token'] = ''

            session = self.sessionService.getSessionByToken(self.sessionService.generate_session_and_token())
        action = session.getActionByOutputAction(output_action)
        if action is None:
            result = ServerResult()
            result.Error = 'Action Not Available'
            return result
        action.Input = output_action.Input

        action_handler = ActionHandler(action, session)
        action_handler.executeAction(action, True)
        return action_handler.serverResult

