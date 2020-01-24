import random
import string

from services.dataService import DataService


class ScreenContext:
    ServerActions = []
    ClientActions = []
    ActualServerActoinsInClient = []
    Data = []
    Component = []
    lastResultInSections = 0

    dataService = DataService.getInstance()

    def __init__(self):
        self.Component = self.dataService.getScreenByStartScreen('Init')['ComponentName']

    def componentChange(self, component_name):
        delete_action_ids = []
        if component_name == self.Component:
            return
        for action in self.ServerActions:
            if action.ComponentContext != component_name and action.ComponentContext != 'no':
                delete_action_ids.append(action.Id)
                self.ServerActions.remove(action)
        self.Component = component_name
        return delete_action_ids

    def addAction(self, action):
        action.ComponentContext = self.Component
        if action.Execute == 'Client':
            self.ClientActions.append(action)
        else:
            action.Id = self.getActionId()
            self.ServerActions.append(action)

    def getActionsForResult(self):
        return_actions = self.ServerActions + self.ClientActions
        self.ClientActions = []
        for action in self.ServerActions:
            self.ActualServerActoinsInClient.append(action.Id)
        self.lastResultInSections = 0
        return return_actions

    def getActionId(self):
        highest_id = 0
        for action in self.ServerActions:
            current_id = int(action.Id.split('-')[1])
            if current_id > highest_id:
                highest_id = current_id
        letters = string.ascii_uppercase
        return (''.join(random.choice(letters) for i in range(6))) + '-' + str(highest_id + 1)
