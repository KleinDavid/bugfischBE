import string
import random


class ServerAction:

    def __init__(self):
        self.Name = ''
        self.Type = ''
        self.Input = {}
        self.Token = ''
        self.Id = ''
        self.Execute = ''
        self.ComponentId = ''
        self.InClient = False
        self.InputValues = []
        self.NextActions = []
        self.Context = ''

        # {name, binding}
        self.Bindings = []

    def setBindings(self, data):
        for binding in self.Bindings:
            value = data
            for key in binding['binding'].split('.'):
                value = value[key]
            self.Input[binding['name']] = value

    def setActionId(self, pre_id, actions):
        highest_id = 0
        for action in actions:
            if action.Id != '':
                current_id = int(action.Id.split('-')[len(action.Id.split('-')) - 1])
                if current_id > highest_id:
                    highest_id = current_id
        letters = string.ascii_uppercase
        self.Id = pre_id + (''.join(random.choice(letters) for i in range(6))) + '-' + str(highest_id + 1)