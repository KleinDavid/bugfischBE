from models.ServerAction import ServerAction
from services.dataService import DataService
from services.loggingService import LoggingService


class ActionParser:
    actionResultData = {}
    logginService = LoggingService()
    dataService = DataService.getInstance()

    def __init__(self, action_result_data):
        self.actionResultData = action_result_data

    def getActionsByArray(self, actions):
        new_actions = []
        for action_string in actions:
            if len(action_string) > 0 and action_string is not '#':
                new_actions.append(self.getActionByString(action_string))
        return new_actions

    def getActionByString(self, action_string):
        action = ServerAction()
        action.Name = self.getActionNameByString(action_string)
        action.Type = self.getActionTypeByString(action_string)
        action.Input = self.getActionInputByString(action_string)
        action.Execute = self.dataService.getServerActionDescription(action.Type)['Execute']
        action.Context = self.getActionContextByString(action_string, action.Execute)
        return action

    @staticmethod
    def getActionTypeByString(action_string):
        return action_string.split('(')[0].replace(' ', '')

    def getActionNameByString(self, action_string):
        if '{' in action_string:
            values = action_string.split('{')[1].replace('}', '')
            for value in values.split(';'):
                if value.split('=')[0] == 'Name':
                    return value.split('=')[1]
        return self.getActionTypeByString(action_string)

    def getActionInputByString(self, action_string):
        list_of_inputs_string = action_string.split('(')[1].split(')')[0].split(';')
        action_description = self.dataService.getActionByName(self.getActionTypeByString(action_string))
        list_of_expected_inputs = action_description['Input'].replace(' ', '').split(',')
        counter = 0
        input_objects = []
        for input_string in list_of_inputs_string:
            input_object = {}
            if '=' not in input_string:
                input_object['name'] = list_of_expected_inputs[counter]
                input_object['input'] = self.getInputValueByString(input_string)
            else:
                input_object['name'] = input_string.split('=')[0].replace(' ', '')

                # **test for exaption
                if input_object['name'] not in list_of_expected_inputs:
                    self.loggingService.error(input_object['name'] + ' is no Input of ' + self.getActionTypeByString(action_string))
                    return {}
                # test for exaption**

                input_object['input'] = self.getInputValueByString(input_string.split('=')[1])
            input_objects.append(input_object)

        # **test for exaption
        for expected_input in list_of_expected_inputs:
            found_value = False
            for input_object in input_objects:
                if expected_input == input_object['name']:
                    found_value = True
                    break
                else:
                    found_value = False
            if not found_value:
                self.loggingService.error('Expected Input \'' + expected_input + '\' is not set in Action \'' + self.getActionTypeByString(action_string)) + '\''
                return {}
        # test for exaption**

        return_inputs_object = {}
        for input_object in input_objects:
            return_inputs_object[input_object['name']] = input_object['input']
        return return_inputs_object

    @staticmethod
    def getActionContextByString(action_string, execute):
        if execute == 'Client':
            return ''
        if '{' in action_string:
            action_string = action_string.split('{')[1].replace('}', '')
            for value in action_string.split(';'):
                if value.split('=')[0] == 'Context':
                    return value.split('=')[1]
        return 'Component'

    def getInputValueByString(self, input_value_string):
        if '\'' in input_value_string:
            return input_value_string.split('\'')[1]
        if 'new ' in input_value_string:
            return self.dataService.getDataPackageByName(input_value_string.split(' ')[1].replace(' ', ''))

        return self.getValueFromActionResultDataByString(input_value_string.replace(' ', ''))

    def getValueFromActionResultDataByString(self, string):
        result = self.actionResultData
        for key in string.split('.'):
            result = result[key]
        return result
