from models.ServerAction import ServerAction
from services.loggingService import LoggingService


class Dea:

    loggingService = LoggingService()

    def __init__(self):
        self.startState = -1
        self.finalStates = [-1, 9, 14]
        self.transitions = [
            Transition(-1, ' ', -1, ''),
            Transition(-1, 'any*', 0, 'type'),
            Transition(0, 'any*', 0, 'type'),

            Transition(0, '(', 1, ''),
            Transition(1, ' ', 1, ''),

            Transition(1, 'any*', 2, 'inputValueName'),
            Transition(2, 'any*', 2, 'inputValueName'),
            Transition(2, '=', 3, ''),

            Transition(3, '\'', 4, 'inputValueConst'),
            Transition(4, 'any*', 4, 'inputValueConst'),
            Transition(4, '\'', 6, 'inputValueConst'),
            Transition(6, ',', 1, ''),

            Transition(3, 'any*', 5, 'inputValueBinding'),
            Transition(5, 'any*', 5, 'inputValueBinding'),
            Transition(5, ',', 1, ''),

            Transition(3, 'new ', 7, ''),
            Transition(7, 'any*', 8, 'inputValueNew'),
            Transition(8, 'any*', 8, 'inputValueNew'),
            Transition(8, ',', 1, ''),

            Transition(1, '\'', 4, 'inputValueConst'),
            Transition(1, 'new ', 7, ''),
            Transition(1, 'any*', 5, 'inputValueBinding'),

            Transition(1, ')', 9, ''),
            Transition(6, ')', 9, ''),
            Transition(5, ')', 9, ''),
            Transition(8, ')', 9, ''),

            Transition(9, '{', 10, ''),
            Transition(10, ' ', 10, ''),
            Transition(10, 'any*', 11, 'actionPropertyName'),
            Transition(11, 'any*', 11, 'actionPropertyName'),
            Transition(11, '=', 12, ''),
            Transition(12, 'any*', 13, 'actionPropertyValue'),
            Transition(13, 'any*', 13, 'actionPropertyValue'),
            Transition(13, ';', 10, ''),
            Transition(13, '}', 14, ''),

            Transition(14, '-', 15, 'nextAction'),
            Transition(15, '>', -1, ''),

            Transition(14, ';', -1, 'newAction'),
            Transition(9, ';', -1, 'newAction'),
        ]

    def getActionsByString(self, actions_string, data_package_configs, action_configs):
        if len(actions_string) == 0:
            return []
        value_list = self.__parseString__(actions_string)
        list_of_action_value_lists = []
        action_value_list = []
        actions = []
        for value in value_list:
            if value['valueName'] == 'newAction':
                list_of_action_value_lists.append(action_value_list)
                action_value_list = []
            action_value_list.append(value)
        list_of_action_value_lists.append(action_value_list)

        for action_value_list in list_of_action_value_lists:
            action = ServerAction()
            action_input_descriptions = []

            next_action = ServerAction()
            next_action_input_descriptions = []

            next_action_state = False
            counter = 0
            for value in action_value_list:
                if not next_action_state:
                    if value['valueName'] == 'type':
                        action.Type = value['value']

                    if value['valueName'] == 'inputValueConst' or value['valueName'] == 'inputValueBinding' or value['valueName'] == 'inputValueNew' or value['valueName'] == 'inputValueName':
                        action.InputDescriptions.append({'valueName': value['valueName'], 'value': value['value']})
                        action_input_descriptions.append({'valueName': value['valueName'], 'value': value['value']})

                    if value['valueName'] == 'actionPropertyName':
                        setattr(action, value['value'], action_value_list[counter + 1]['value'])

                    if value['valueName'] == 'nextAction':
                        next_action_state = True

                else:
                    if value['valueName'] == 'type':
                        next_action.Type = value['value']

                    if value['valueName'] == 'inputValueConst' or value['valueName'] == 'inputValueName' or value['valueName'] == 'inputValueNew' or value['valueName'] == 'inputValueName':
                        next_action.InputDescriptions.append({'valueName': value['valueName'], 'value': value['value']})
                        next_action_input_descriptions.append({'valueName': value['valueName'], 'value': value['value']})

                    if value['valueName'] == 'actionPropertyName':
                        setattr(next_action, value['value'], action_value_list[counter + 1]['value'])

                    if value['valueName'] == 'nextAction':
                        self.__setInputValues__(next_action, next_action_input_descriptions, action_configs, data_package_configs)
                        action.NextActions.append(next_action)
                        next_action = ServerAction()
                        next_action_input_descriptions = []
                counter = counter + 1

            if next_action_state:
                action.NextActions.append(next_action)
            self.__setInputValues__(action, action_input_descriptions, action_configs, data_package_configs)
            self.loggingService.logObject(action)
            actions.append(action)
        return actions

    def __parseString__(self, string):
        counter = 0
        current_states = [self.startState]
        current_name_values = [{'state': self.startState, 'valueName': '', 'value': ''}]
        found_values = []
        while counter < len(string):
            transitions = self._getTransitions(current_states, counter, string)
            if len(transitions) == 0:
                return None

            for current_name_value in current_name_values:
                delete_values = []
                is_there_a_transition = False
                for transition in transitions:
                    if transition.firstKnote == current_name_value['state']:
                        if transition.name != current_name_value['valueName'] and current_name_value['valueName'] != '':
                            found_values.append(current_name_value)
                            delete_values.append(current_name_value)
                        is_there_a_transition = True
                if not is_there_a_transition:
                    delete_values.append(current_name_value)

            current_name_values = list(filter(lambda x: x not in delete_values, current_name_values))

            old_name_values = current_name_values
            current_name_values = []
            current_states = []

            transition_length = 0
            for transition in transitions:
                if transition.tansitionString == 'any*':
                    transition_string = string[counter]
                    transition_length = 1
                else:
                    transition_length = len(transition.tansitionString)
                    transition_string = transition.tansitionString

                for old_name_value in old_name_values:
                    if transition.name == old_name_value['valueName']:
                        transition_string = old_name_value['value'] + transition_string

                if transition.name != '':
                    current_name_values.append({'state': transition.targetKnote, 'valueName': transition.name, 'value': transition_string})
                current_states.append(transition.targetKnote)
            counter = counter + transition_length

        for final_state in self.finalStates:
            if final_state in current_states:
                return found_values

        return None

    def _getTransitions(self, current_states, counter, string):

        knote_transitions = list(filter(lambda x: x.firstKnote in current_states, self.transitions))
        found_transitions = []
        for transition in knote_transitions:
            if string[counter:counter + len(transition.tansitionString)] == transition.tansitionString:
                found_transitions.append(transition)
        longest_transition = 0

        for transition in found_transitions:
            if longest_transition <= len(transition.tansitionString):
                longest_transition = len(transition.tansitionString)

        for transition in found_transitions:
            if len(transition.tansitionString) != longest_transition:
                found_transitions.remove(transition)

        if len(found_transitions) == 0:
            found_transitions = list(filter(lambda x: x.tansitionString == 'any*', knote_transitions))

        return found_transitions

    def __setInputValues__(self, action, action_input_descriptions, action_configs, data_package_configs):
        list_of_expected_inputs = []

        # set default inputs in action
        for action_config in action_configs:
            if action.Type == action_config.type:
                list_of_expected_inputs = action_config.input
        for _input in list_of_expected_inputs:
            action.Input[_input] = ''

        # set input_values {type, input, name}
        input_values = []
        counter = 0
        for input_description in action_input_descriptions:
            if input_description['valueName'] == 'inputValueConst' or input_description['valueName'] == 'inputValueBinding' or input_description['valueName'] == 'inputValueNew':
                name = ''
                if action.InputDescriptions[counter - 1]['valueName'] == 'inputValueName':
                    name = action.InputDescriptions[counter - 1]['value']
                input_values.append({'type': input_description['valueName'], 'input': input_description['value'], 'name': name})
            counter = counter + 1

        # set all inputs_value names
        counter = 0
        for input_value in input_values:
            if input_value['name'] == '':
                input_value['name'] = list_of_expected_inputs[counter]
            else:
                # **check exaption
                if input_value['name'] not in list_of_expected_inputs:
                    self.loggingService.error(input_value['name'] + ' is no Input of ' + action.Type)
                    return {}
                # check exaption**

            counter = counter + 1

        # set values to action input and input bindings
        for input_value in input_values:
            if input_value['type'] == 'inputValueBinding':
                action.Bindings.append({'name': input_value['name'], 'binding': input_value['input']})
            if input_value['type'] == 'inputValueConst':
                action.Input[input_value['name']] = input_value['input'].replace('\'', '')
            if input_value['type'] == 'inputValueNew':
                action.Input[input_value['name']] = self.__getDataPackageByName__(input_value['input'], data_package_configs)

    def __getDataPackageByName__(self, name, data_package_configs):
        data_package = {}
        properties = []
        for data_package_config in data_package_configs:
            if data_package_config.name == name:
                properties = data_package_config.properties

        for _property in properties:
            if _property.find(':') != -1:
                data_package[_property.split(':')[0]] = self.getDataPackageByName(_property.split(':')[1])
            else:
                data_package[_property] = ''
        return data_package


class Transition:
    def __init__(self, first, trans, target, name):
        self.firstKnote = first
        self.tansitionString = trans
        self.targetKnote = target
        self.name = name
