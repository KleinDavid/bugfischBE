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
    sessionService = SessionService.getInstance()
    component = {}
    configService = ConfigService.getInstance()
    __taskService = TaskService.getInstance()

    def __init__(self, action, session):
        self.dataService = DataService.getInstance()
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

    def executeAction(self, action, from_client):
        if not action.checkCondition(self.actionOutputData):
            self.loggingService.log('Condition == False: ' + str(action.Type))
            return

        if action.IsDescription:
            action = self.configService.getActionDescriptionConfigByName(action.Name)

        self.loggingService.log('execute Action ' + str(action.Type) + ' | Input: ' + str(action.Input))
        action_config = self.configService.getActionConfigByType(action.Type)
        self.actionOutputData[action_config.outputData] = self.runAction(action)

        # config
        for client_action in action_config.outputClientActions:
            client_action.setBindings(self.actionOutputData, self.configService.dataPackageConfigs)
            self.setActionToScreenContext(client_action)

        for action_object in action_config.outputServerActions:
            action_object.setBindings(self.actionOutputData, self.configService.dataPackageConfigs)
            self.setActionToScreenContext(action_object)

        for action_object in action_config.useActions:
            action_object.setBindings(self.actionOutputData, self.configService.dataPackageConfigs)
            self.executeAction(action_object, False)

        # action specific
        for action_object in action.OutputServerActions:
            action_object.setBindings(self.actionOutputData, self.configService.dataPackageConfigs)
            self.setActionToScreenContext(action_object)

        for action_object in action.NextActions:
            action_object.setBindings(self.actionOutputData, self.configService.dataPackageConfigs)
            self.executeAction(action_object, False)

        if from_client:
            self.serverResult.Actions = self.session.getActionsForResult()
            self.serverResult.ActionIds = self.session.getCurrentActionIds()
            self.loggingService.logServerResult(self.serverResult)
            self.dataService.connection.close()

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
            "StartNewTaskAction": self.startNewTaskAction,
            "GetDataCondition": self.getDataCondition,
            "SaveDataCondition": self.saveDataCondition,
            "SetDataAction": self.setDataAction
        }
        func = switcher.get(action.Type, lambda: "Invalid month")
        return func(action.Input)

    # Main Action
    def initializeSessionAction(self, data):
        token = data['Token']
        if token == '':
            # self.session = self.sessionService.getSessionByToken(self.sessionService.generate_session_and_token())
            screen = self.configService.getScreenConfigByStartScreen('Init')
            return {'Token': self.session.token, 'ComponentName': screen.componentName, 'WebsocketPath': ''}
        else:
            self.session = self.sessionService.getSessionByToken(token)
            self.session.setNoActionInClient()
            return {'Token': self.session.token, 'ComponentName': self.session.getCurrentComponent().name, 'WebsocketPath': ''}

    def loginAction(self, data):
        password = data['Password']
        result = ServerResult()
        login_data = self.session.login(password)

        if login_data is None:
            result.Error = 'Not Login'
            return {'Role': 'Init', 'Token': ''}
        return login_data

    def getDataAction(self, data):
        where_statement = self.parseWherStatement(data['WhereStatement'], data['DataType'])
        data_object = self.dataService.getDataPackage(data['DataType'], where_statement)
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
            self.executeAction(action_object, False)

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
                    data_value = data_value[_property]
                    if str(data_value) == str(condition):
                        return_data_package[counter] = data_package[value_id]
                        counter = counter + 1
        return {'Name': data['DataType'], 'Data': return_data_package}

    def startNewTaskAction(self, data):
        self.__taskService.createNewTask(data['TaskName'], self.session.totalId)
        self.updateGlobalData()
        return {}

    def getDataCondition(self, data):
        where_statement = self.parseWherStatement(data['WhereStatement'], data['DataType'])
        data_object = self.dataService.getDataPackage(data['DataType'], where_statement)
        if data_object is None:
            return {'WhereStatement': data['WhereStatement'], 'DataType': data['DataType'], 'Result': False}
        res = 0 in data_object
        return {'WhereStatement': data['WhereStatement'], 'DataType': data['DataType'], 'Result': res}

    def saveDataCondition(self, data):
        table_name = data['DataType']
        condition = data['Condition']
        failed_list_field = data['FailedListField']
        data = data['Data']
        failted_list = []

        if_decition = condition.split('?')[0].replace(' ', '')
        if_statement = condition.split('?')[1].split(':')[0].replace(' ', '')
        # else_statement = condition.split(':')[1].replace(' ', '')
        res = True

        if '0' in data:
            counter = 0
            while str(counter) in data:
                if self.getValueByCondition(if_decition, data[str(counter)]):
                    res = self.getValueByCondition(if_statement, data[str(counter)]) and res
                    if not self.getValueByCondition(if_statement, data[str(counter)]):
                        failted_list.append(data[str(counter)][failed_list_field])
                counter += 1
        return {'Data': data, 'DataType': table_name, 'Result': res, 'FailtedList': failted_list}

    def setDataAction(self, data):
        return {'Data': data['Data'], 'Name': data['Name']}

    def parseWherStatement(self, where_statement, data_type):
        new_where_statement = where_statement
        if 'Marit' in new_where_statement:
            number_of_next_values = 1
            if len(new_where_statement.split(' ')) > 2:
                number_of_next_values = new_where_statement.split(' ')[1]
            current_data_in_client_object = self.component.getDataByName(data_type)
            if current_data_in_client_object is None:
                min_id = self.dataService.getMinIdByDataType(data_type)
                new_where_statement = 'Id >= ' + str(min_id) + ' AND Id < ' + str(min_id + int(number_of_next_values))
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
                new_where_statement = 'Id > ' + str(highest_id) + ' AND Id <= ' + str(highest_id + int(number_of_next_values))
        return new_where_statement

    def getValueByCondition(self, string, data):
        if '==' in string:
            value_list = string.split('==')
            return self.getLenOfValueByString(value_list[0], data) == value_list[1]
        if '>' in string:
            value_list = string.split('>')
            return self.getLenOfValueByString(value_list[0], data) > int(value_list[1])
        if '<' in string:
            value_list = string.split('<')
            return self.getLenOfValueByString(value_list[0], data) < int(value_list[1])
        if '<=' in string:
            value_list = string.split('<=')
            return self.getLenOfValueByString(value_list[0], data) <= int(value_list[1])
        if '>=' in string:
            value_list = string.split('>=')
            return self.getLenOfValueByString(value_list[0], data) >= int(value_list[1])

    @staticmethod
    def getLenOfValueByString(string, data):
        if 'len(' in string:
            string = string.replace('len(', '').replace(')', '')
            return len(data[string])
        else:
            return data[string]
