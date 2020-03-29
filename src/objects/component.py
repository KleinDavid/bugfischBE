import string
import random


class Component:

    def __init__(self, name, component_id):
        self.actions = []
        self.active = True
        self.name = name
        self.Id = component_id
        self.data = {}

    def addAction(self, new_action):
        for action in self.actions:
            if action.Id == new_action.Id:
                action.Input = new_action.Input
                action.InClient = False
                return
            elif action.Name == new_action.Name:
                self.actions.remove(action)
        new_action.ComponentContext = self.name
        new_action.setActionId(self.Id + '_', self.actions)
        self.actions.append(new_action)

    def getDataByName(self, name):
        if name not in self.data:
            return None
        return self.data[name]
