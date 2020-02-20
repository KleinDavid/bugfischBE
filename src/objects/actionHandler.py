from models.ServerAction import ServerAction
from models.ServerActionDescription import ServerActionDescription
from models.ServerResult import ServerResult
from objects.actionParser import ActionParser
from services.dataService import DataService
from services.loggingService import LoggingService
from services.sessionService import SessionService


class ActionHandler:
    action = ServerAction()
    session = {}
    serverResult = {}
    actionResultData = {}
    loggingService = LoggingService()
    actionParser = {}
    dataService = DataService.getInstance()
    sessionService = SessionService.getInstance()
    component = {}

    def __init__(self, action, session):
        self.actionResultData = {}
        self.serverResult = ServerResult()
        self.action = action
        self.session = session
        self.actionParser = ActionParser(self.actionResultData)
        self.component = self.session.getCurrentComponent()

    def executeAction(self, from_client):

        self.loggingService.log('execute Action ' + str(self.action.Type) + ' | Input: ' + str(self.action.Input))

        action_description = ServerActionDescription()
        self.dataService.mapDataBaseResultToObject('serveractions', 'Type', self.action.Type, action_description)
        action_description.OutputClientAction = action_description.OutputClientAction.replace(' ', '').split(",")
        self.actionResultData[action_description.OutputData] = self.runAction(self.action)

        for client_action in self.actionParser.getActionsByArray(action_description.OutputClientAction):
            self.setActionToScreenContext(client_action)

        for action_object in self.actionParser.getActionsByArray(action_description.OutputServerAction.split(',')):
            self.setActionToScreenContext(action_object)

        for action_object in self.actionParser.getActionsByArray(action_description.UseAction.split(',')):
            self.action = action_object
            self.executeAction(False)

        if from_client:
            self.serverResult.Actions = self.session.getActionsForResult()
            self.serverResult.ActionIds = self.session.getCurrentActionIds()
            self.loggingService.logServerResult(self.serverResult)

    def setActionToScreenContext(self, action):
        action.Execute = self.dataService.getServerActionDescription(action.Type)['Execute']
        if self.component is not None and action.Context == 'Component':
            action.ComponentId = self.component.Id
        self.session.setNewAction(action)

    def runAction(self, action):
        switcher = {
            "LoginAction": self.loginAction,
            "ChangeRoute": self.changeRouteAction,
            "RouteAfterLogin": self.routeAfterLoginAction,
            "SaveDataAction": self.saveDataAction,
            "GetDataAction": self.getDataAction,
            "InitializeSessionAction": self.initializeSessionAction,
            "LogoutAction": self.logoutAction,
            "FilterDataAction": self.filterDataActoin
        }
        func = switcher.get(action.Type, lambda: "Invalid month")
        return func(action.Input)

    # Main Action
    def initializeSessionAction(self, data):
        token = data['Token']
        if token == '':
            self.session = self.sessionService.getSessionByToken(self.sessionService.generate_session_and_token())
            screen = self.dataService.getScreenByStartScreen('Init')
            return {'Token': self.session.token, 'ComponentName': screen['ComponentName']}
        else:
            self.session = self.sessionService.getSessionByToken(token)
            self.session.setNoActionInClient()
            return {'Token': self.session.token, 'ComponentName': self.session.getCurrentComponent().name}

    def loginAction(self, data):
        password = data['Password']
        result = ServerResult()
        login_data = self.session.login(password)

        if login_data is None:
            result.Error = 'Not Login'
            return {'Role': 'Init', 'Token': ''}
        return login_data

    def getDataAction(self, data):
        data_object = self.dataService.getDataPackage(data['DataType'], data['WhereStatement'])
        self.component.data[data['DataType']] = data_object
        return {'Name': data['DataType'], 'Data': data_object}

    def saveDataAction(self, data):
        table_name = data['DataType']
        data = data['Data']
        self.dataService.saveDataPackageInDataBase(table_name, data)
        return {'Name': 'SaveSucces', 'Data': 'True'}

    def routeAfterLoginAction(self, data):
        role = data['Role']
        screen = self.dataService.getScreenByStartScreen(role)
        if role == 'Admin':
            return {'ComponentName': screen['ComponentName']}
        if role == 'User':
            return {'ComponentName': screen['ComponentName']}

        return {'ComponentName': screen['ComponentName']}

    def changeRouteAction(self, data):
        component_name = data['ComponentName']
        routedata = self.dataService.getRouteData(component_name)
        self.component = self.session.createNewComponent(component_name)
        if routedata is None:
            self.serverResult.Error = 'Component not Found'
            return{'ComponentName': ''}
        for action in self.actionParser.getActionsByArray(routedata["OutputServerActions"].split(",")):
            self.setActionToScreenContext(action)
        for action_object in self.actionParser.getActionsByArray(routedata['UseAction'].split(',')):
            self.action = action_object
            self.executeAction(False)

        return {'ComponentName': component_name, 'DeleteActionIds': []}

    def logoutAction(self, data):
        token = data['Token']
        self.sessionService.logout(token)

    def filterDataActoin(self, data):
        data_package = self.component.getDataByName(data['DataType'])
        return_data_package = {}
        property_path = data['Property'].split('.')
        condition = data['Condition']
        counter = 0
        for value_id in data_package:
            data_value = data_package[value_id]
            for _property in property_path:
                if len(data_value) > 0:
                    print(_property, data_value)
                    data_value = data_value[_property]
                    if str(data_value) == str(condition):
                        return_data_package[counter] = data_package[value_id]
                        counter = counter + 1
        return {'Name': data['DataType'], 'Data': return_data_package}
