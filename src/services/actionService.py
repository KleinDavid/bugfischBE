from models.ServerAction import ServerAction
from models.ServerResult import ServerResult
from objects.actionHandler import ActionHandler
from services.loggingService import LoggingService
from services.sessionService import SessionService


class ActionService:
    dataService = {}
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

    def executeAction(self, action):
        session = self.sessionService.getSessionByToken(action.Token)
        if session is None:
            action = ServerAction()
            action.Type = 'InitializeSessionAction'
            action.Input = {}
            action.Input['Token'] = ''
            session = self.sessionService.getSessionByToken(self.sessionService.generate_session_and_token())
        if not session.checkIfActionIsAvailable(action):
            result = ServerResult()
            result.Error = 'Action Not Available'
            return result
        action_handler = ActionHandler(action, session)
        action_handler.executeAction(True)
        return action_handler.serverResult

