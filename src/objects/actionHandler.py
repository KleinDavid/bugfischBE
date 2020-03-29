from models.ServerAction import ServerAction
from models.ServerActionDescription import ServerActionDescription
from models.ServerResult import ServerResult
from objects.actionParser import ActionParser
from services.configService import ConfigService
from services.dataService import DataService
from services.loggingService import LoggingService
from services.sessionService import SessionService
from services.taskService import TaskService


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
    configService = ConfigService.getInstance()
    __taskService = TaskService.getInstance()

    def __init__(self, action, session):
        self.actionResultData = {}
        self.actionOutputData = {}
        self.serverResult = ServerResult()
        self.action = action
        self.session = session
        self.actionParser = ActionParser(self.actionResultData)
        self.component = self.session.getCurrentComponent()
        self.updateGlobalData()

    def updateGlobalData(self):
        # add current Task
        self.actionOutputData['Global'] = {}
        self.actionOutputData['Global']['Tasks'] = self.__taskService.getCurrentTasksBySessionTotalId(self.session.totalId)

    def executeAction2(self, from_client):
        self.loggingService.log('execute Action ' + str(self.action.Type) + ' | Input: ' + str(self.action.Input))
        action_config = self.configService.getActionConfigByType(self.action.Type)
        self.actionOutputData[action_config.outputData] = self.runAction(self.action)

        # config
        for client_action in action_config.outputClientActions:
            client_action.setBindings(self.actionOutputData, self.configService.dataPackageConfigs)
            self.setActionToScreenContext(client_action)

        for action_object in action_config.outputServerActions:
            action_object.setBindings(self.actionOutputData, self.configService.dataPackageConfigs)
            self.setActionToScreenContext(action_object)

        for action_object in action_config.useActions:
            self.action = action_object
            self.action.setBindings(self.actionOutputData, self.configService.dataPackageConfigs)
            self.executeAction2(False)

        # action specific
        for action_object in self.action.OutputServerActions:
            action_object.setBindings(self.actionOutputData, self.configService.dataPackageConfigs)
            self.setActionToScreenContext(action_object)

        for action_object in self.action.NextActions:
            self.action = action_object
            self.action.setBindings(self.actionOutputData, self.configService.dataPackageConfigs)
            self.executeAction2(False)

        if from_client:
            self.serverResult.Actions = self.session.getActionsForResult()
            self.serverResult.ActionIds = self.session.getCurrentActionIds()
            self.loggingService.logServerResult(self.serverResult)

    def executeAction(self, from_client):
        self.loggingService.log('execute Action ' + str(self.action.Type) + ' | Input: ' + str(self.action.Input))

        action_description = ServerActionDescription()
        self.dataService.mapDataBaseResultToObject('serveractions', 'Type', self.action.Type, action_description)
        action_description.OutputClientActions = action_description.OutputClientActions.replace(' ', '').split(",")
        self.actionResultData[action_description.OutputData] = self.runAction(self.action)

        for client_action in self.actionParser.getActionsByArray(action_description.OutputClientActions):
            self.setActionToScreenContext(client_action)

        for action_object in self.actionParser.getActionsByArray(action_description.OutputServerActions.split(',')):
            self.setActionToScreenContext(action_object)

        for action_object in self.actionParser.getActionsByArray(action_description.UseActions.split(',')):
            self.action = action_object
            self.executeAction(False)

        if from_client:
            self.serverResult.Actions = self.session.getActionsForResult()
            self.serverResult.ActionIds = self.session.getCurrentActionIds()
            self.loggingService.logServerResult(self.serverResult)

    def setActionToScreenContext(self, action):
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
            "FilterDataAction": self.filterDataAction,
            "StartNewTaskAction": self.startNewTaskAction
        }
        func = switcher.get(action.Type, lambda: "Invalid month")
        return func(action.Input)

    # Main Action
    def initializeSessionAction(self, data):
        token = data['Token']
        if token == '':
            self.session = self.sessionService.getSessionByToken(self.sessionService.generate_session_and_token())
            screen = self.dataService.getScreenByStartScreen('Init')
            return {'Token': self.session.token, 'ComponentName': screen['ComponentName'], 'WebsocketPath': self.session.websocket.path}
        else:
            self.session = self.sessionService.getSessionByToken(token)
            self.session.setNoActionInClient()
            return {'Token': self.session.token, 'ComponentName': self.session.getCurrentComponent().name, 'WebsocketPath': self.session.websocket.path}

    def loginAction(self, data):
        password = data['Password']
        result = ServerResult()
        login_data = self.session.login(password)

        if login_data is None:
            result.Error = 'Not Login'
            return {'Role': 'Init', 'Token': ''}
        return login_data

    def getDataAction(self, data):
        if 'Next' in data['WhereStatement']:
            number_of_next_values = 1
            if len(data['WhereStatement'].split(' ')) > 2:
                number_of_next_values = data['WhereStatement'].split(' ')[1]
            current_data_in_client_object = self.component.getDataByName(data['DataType'])
            if current_data_in_client_object is None:
                min_id = self.dataService.getMinIdByDataType(data['DataType'])
                data['WhereStatement'] = 'Id >= ' + str(min_id) + ' AND Id < ' + str(min_id + int(number_of_next_values))
            else:
                current_data_in_client_list = [current_data_in_client_object[0]]
                counter = 0
                while counter in current_data_in_client_object is not None:
                    current_data_in_client_list.append(current_data_in_client_object[counter])
                    counter += 1
                highest_id = 0
                for value in current_data_in_client_list:
                    if value['Id'] > highest_id:
                        highest_id = value['Id']
                data['WhereStatement'] = 'Id > ' + str(highest_id) + ' AND Id <= ' + str(highest_id + int(number_of_next_values))

        data_object = self.dataService.getDataPackage(data['DataType'], data['WhereStatement'])
        self.component.data[data['DataType']] = data_object
        return {'Name': data['DataType'], 'Data': data_object}

    def saveDataAction(self, data):
        table_name = data['DataType']
        data = data['Data']
        if '0' in data:
            counter = 0
            while str(counter) in data:
                self.dataService.saveDataPackageInDataBase(table_name, data[str(counter)])
                counter += 1
        else:
            self.dataService.saveDataPackageInDataBase(table_name, data)
        return {'Name': 'SaveSucces', 'Data': 'True'}

    def routeAfterLoginAction(self, data):
        return {'ComponentName': self.configService.getScreenConfigByStartScreen(data['Role']).componentName}

    def changeRouteAction(self, data):
        component_name = data['ComponentName']
        screen_config = self.configService.getScreenConfigByComponentName(component_name)
        self.component = self.session.createNewComponent(component_name)
        if screen_config is None:
            self.serverResult.Error = 'Component not Found'
            return{'ComponentName': ''}
        for action in screen_config.outputServerActions:
            self.setActionToScreenContext(action)
        for action_object in screen_config.useActions:
            self.action = action_object
            self.executeAction2(False)

        return {'ComponentName': component_name, 'DeleteActionIds': []}

    def logoutAction(self, data):
        token = data['Token']
        self.sessionService.logout(token)

    def filterDataAction(self, data):
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

    def startNewTaskAction(self, data):
        self.__taskService.createNewTask(data['TaskName'], self.session.totalId)
        self.updateGlobalData()
        return {}


