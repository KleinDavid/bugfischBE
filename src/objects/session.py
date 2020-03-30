import string
import random

from objects.component import Component
from objects.websocket.consumerWebsocket import CostumerWebsocket
from services.configService import ConfigService
from services.dataService import DataService
from services.loggingService import LoggingService


class Session:
    __dataService__ = DataService.getInstance()
    __loggingService__ = LoggingService()
    __configService__ = ConfigService.getInstance()

    def __init__(self, session_id):
        self.totalId = None
        self.token = self.get_random_string(20) + str(session_id)
        self.id = session_id
        self.components = []
        self.actions = []
        self.totalTime = 0
        self.lastRequestInSeconds = 0
        self.loginState = ''
        self.websocket = CostumerWebsocket()
        self.actions = self.actions + self.__configService__.getAllOpeningActions()

    @staticmethod
    def get_random_string(string_length=10):
        letters = string.ascii_uppercase
        return ''.join(random.choice(letters) for i in range(string_length))

    def login(self, password):
        if self.__dataService__.check_passwords(password):
            return {'Token': self.token, 'Role': self.__dataService__.getRoleByPassword(password)}
        return None

    def getActionByOutputAction(self, output_action):
        for current_action in self.actions:
            if current_action.Type == output_action.Type and current_action.Id == output_action.Id:
                current_action.InClient = False
                return current_action
        if '_' in output_action.Id:
            for current_action in self.getComponentById(output_action.Id.split('_')[0]).actions:
                if current_action.Id == output_action.Id and current_action.Type == output_action.Type:
                    current_action.InClient = False
                    return current_action
        return None

    def createNewComponent(self, name):
        for component in self.components:
            component.active = False
        for component in self.components:
            if component.name == name:
                component.active = True
                component.actions = []
                return component
        component = Component(name, self.getNewComponentId())
        self.components.append(component)
        return component

    def setNewAction(self, action):
        if action.Context == 'Component':
            component = self.getComponentById(action.ComponentId)
            component.addAction(action)
            return
        action.setActionId('', self.actions)
        self.actions.append(action)

    def getActionsForResult(self):
        component_actions = []
        for component in self.components:
            if component.active is True:
                component_actions = component_actions + component.actions
        # self.printSessionActoins()
        result_actions = self.actions + component_actions
        result_actions = list(filter(lambda x: not x.InClient, result_actions))
        self.actions = list(filter(lambda x: x.Execute != 'Client', self.actions))
        for action in self.actions:
            action.InClient = True
        for action in component_actions:
            action.InClient = True
        self.lastRequestInSeconds = 0
        return result_actions

    def getCurrentActionIds(self):
        action_ids = []
        for component in list(filter(lambda x: x.active, self.components)):
            for action in component.actions:
                action_ids.append(action.Id)
        for action in self.actions:
            action_ids.append(action.Id)
        return action_ids

    def setNoActionInClient(self):
        for component in self.components:
            for action in component.actions:
                action.InClient = False
        for action in self.actions:
            action.InClient = False

    def getComponentById(self, component_id):
        for component in self.components:
            if component.Id == component_id:
                return component
        return None

    def getNewComponentId(self):
        highest_id = 0
        for component in self.components:
            if component.Id != '':
                current_id = int(component.Id.split('-')[1])
                if current_id > highest_id:
                    highest_id = current_id
        letters = string.ascii_uppercase
        return (''.join(random.choice(letters) for i in range(6))) + '-' + str(highest_id + 1)

    def getCurrentComponent(self):
        current_components_list = list(filter(lambda x: x.active is True, self.components))
        if len(current_components_list) > 0:
            return current_components_list[0]
        return None

    def printSessionActoins(self):
        print('Session:')
        for action in self.actions:
            print('    ', action.Type)
        for component in self.components:
            print (component.name, component.Id)
            for action in component.actions:
                print('    ', action.Type)
