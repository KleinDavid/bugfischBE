import string
import random


class Component:
    name = ''
    active = True
    Id = ''
    actions = []
    data = {}

    def __init__(self, name, component_id):
        self.actions = []
        self.active = True
        self.name = name
        self.Id = component_id
        self.data = {}

    def addAction(self, action):
        print('add Actoin to', self.name, action.Type)
        action.ComponentContext = self.name
        action.Id = self.getActionId()
        self.actions.append(action)

    def getActionId(self):
        highest_id = 0
        for action in self.actions:
            current_id = action.Id.split('_')[1]
            current_id = int(current_id.split('-')[1])
            if current_id > highest_id:
                highest_id = current_id
        letters = string.ascii_uppercase
        return self.Id + '_' + (''.join(random.choice(letters) for i in range(6))) + '-' + str(highest_id + 1)

    def getDataByName(self, name):
        return self.data[name]
