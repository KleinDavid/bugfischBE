import string
import random

from models.ServerAction import ServerAction
from objects.component import Component
from objects.screenContext import ScreenContext
from services.dataService import DataService


class Session:
    dataService = DataService.getInstance()
    token = ''
    id = ''
    loginState = ''

    totalTime = 0
    lastRequestInSeconds = 0

    actions = []
    components = []

    def __init__(self, session_id):
        self.token = self.get_random_string(20) + str(session_id)
        self.id = session_id
        self.components = []
        self.actions = []
        self.totalTime = 0
        self.lastRequestInSeconds = 0
        self.loginState = ''

        action_decriptions = self.dataService.getServerActionDescriptions()
        for action_decription in action_decriptions:
            if action_decription['Opening'] == '1':
                action = ServerAction()
                action.Type = action_decription['Type']
                action.Name = action_decription['Type']
                self.actions.append(action)

    @staticmethod
    def get_random_string(string_length=10):
        letters = string.ascii_uppercase
        return ''.join(random.choice(letters) for i in range(string_length))

    def login(self, password):
        if self.dataService.check_passwords(password):
            return {'Token': self.token, 'Role': self.dataService.getRoleByPassword(password)}
        return None

    def checkIfActionIsAvailable(self, action):
        # self.printSessionActoins()
        for current_action in self.actions:
            if current_action.Type == action.Type and current_action.Id == action.Id:
                return True
        for current_action in self.getComponentById(action.Id.split('_')[0]).actions:
            if current_action.Id == action.Id and current_action.Type == action.Type:
                return True
        return False

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
        action.Id = self.getNewActionId()
        self.actions.append(action)

    def getActionsForResult(self):
        component_actions = []
        for component in self.components:
            if component.active is True:
                component_actions = component_actions + component.actions
        self.printSessionActoins()
        result_actions = self.actions + component_actions
        self.actions = list(filter(lambda x: x.Execute != 'Client', self.actions))
        self.lastRequestInSeconds = 0
        return result_actions

    def getComponentById(self, component_id):
        for component in self.components:
            if component.Id == component_id:
                return component
        return None

    def getNewActionId(self):
        highest_id = 0
        for action in self.actions:
            if action.Id != '':
                current_id = int(action.Id.split('-')[1])
                if current_id > highest_id:
                    highest_id = current_id
        letters = string.ascii_uppercase
        return (''.join(random.choice(letters) for i in range(6))) + '-' + str(highest_id + 1)

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
