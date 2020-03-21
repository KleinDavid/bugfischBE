import string
import random


class Component:

    def __init__(self, name, component_id):
        self.actions = []
        self.active = True
        self.name = name
        self.Id = component_id
        self.data = {}

    def addAction(self, action):
        action.ComponentContext = self.name
        action.setActionId(self.Id + '_', self.actions)
        self.actions.append(action)

    def getDataByName(self, name):
        return self.data[name]
