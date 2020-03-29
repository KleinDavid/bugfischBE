import string
import random

from services.loggingService import LoggingService


class ServerAction:

    __loggingService = LoggingService()

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
        self.OutputServerActions = []
        self.Context = ''

        # {name, binding}
        self.Bindings = []

        # {name, code}
        self.KomplexCode = []

    def setBindings(self, data, data_package_configs):
        for binding in self.Bindings:
            self.Input[binding['name']] = self.getValueByBinding(binding, data)

        for komplex_code_statement in self.KomplexCode:
            code = komplex_code_statement['code']
            source_list_binding = code.split(']=>')[0].replace('[', '')
            data_package_type = code.split('new ')[1].split('(')[0]
            assigned_values = []
            for assingment in code.split('(')[1].split(')')[0].split(','):
                assigned_values.append({'source': assingment.split('=')[1], 'target': assingment.split('=')[0]})

            data_package_multi = data
            for key in source_list_binding.split('.'):
                data_package_multi = data_package_multi[key]

            new_object_list = {}
            counter = 0
            while counter in data_package_multi:
                data_package_config = list(filter(lambda x: x.name == data_package_type, data_package_configs))[0]
                new_object = {}
                for propertie in data_package_config.properties:
                    new_object[propertie] = ''
                for assigned_value in assigned_values:
                    target = assigned_value['target'].replace(' ', '')
                    if assigned_value['source'] in data_package_multi[counter]:
                        new_object[target] = data_package_multi[counter][assigned_value['source']]
                    else:
                        new_object[target] = self.getValueByBindingString(assigned_value['source'], data)
                new_object_list[counter] = new_object
                counter += 1
            self.Input[komplex_code_statement['name']] = new_object_list

    def getValueByBinding(self, binding, data):
        value = data
        for key in binding['binding'].split('.'):
            value = value[key]
        return value

    def getValueByBindingString(self, binding, data):
        value = data
        for key in binding.split('.'):
            if key in value:
                value = value[key]
            else:
                print(value[key])
        return value

    def setActionId(self, pre_id, actions):
        highest_id = 0
        for action in actions:
            if action.Id != '':
                current_id = int(action.Id.split('-')[len(action.Id.split('-')) - 1])
                if current_id > highest_id:
                    highest_id = current_id
        letters = string.ascii_uppercase
        self.Id = pre_id + (''.join(random.choice(letters) for i in range(6))) + '-' + str(highest_id + 1)