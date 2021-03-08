from models.ServerAction import ServerAction
from services.loggingService import LoggingService


class Dea:

    loggingService = LoggingService()

    def __init__(self):
        self.startState = -1
        self.finalStates = [-1, 9, 14]
        self.GroupStack = 0
        self.singleValueNameTransitions = ['groupEnd']
        self.transitions = [
            Transition(-1, ' ', -1, ''),
            Transition(-1, '(', 0, 'groupStart'),
            # Transition(-1, '(', -1, 'groupStart'),
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

            Transition(14, '=', 15, 'outputServerAction'),
            Transition(9, '=', 15, 'outputServerAction'),
            Transition(14, '-', 15, 'nextAction'),
            Transition(9, '-', 15, 'nextAction'),
            Transition(15, '>', -1, ''),

            Transition(14, ';', -1, 'newAction'),
            Transition(9, ';', -1, 'newAction'),
            #Transition(14, ')', -1, 'groupEnd'),
            #Transition(9, ')', -1, 'groupEnd'),
            Transition(14, ' ', -1, ''),
            Transition(9, ' ', -1, ''),

            Transition(14, ')', 14, 'groupEnd'),
            Transition(9, ')', 9, 'groupEnd'),

            Transition(3, '(', 16, ''),
            Transition(1, '(', 16, ''),
            Transition(16, 'any*', 16, 'komplexCode'),
            Transition(16, '(', 17, 'komplexCode'),
            Transition(17, 'any*', 17, 'komplexCode'),
            Transition(17, ')', 18, 'komplexCode'),
            Transition(18, 'any*', 18, 'komplexCode'),
            Transition(18, ')', 19, ''),
            Transition(19, ',', 1, ''),
            Transition(19, ')', 9, ''),

            Transition(-1, '{', 20, ''),
            Transition(0, '{', 20, ''),
            Transition(20, 'any*', 20, 'condition'),
            Transition(20, '} ?', -1, ''),

            Transition(-1, '/', 21, ''),
            Transition(21, 'any*', 21, 'actionDescription'),
            Transition(21, '/', 9, ''),
            Transition(21, '/', -1, ''),
        ]
        self.parseSting = 'GetDataCondition(DataType=\'SurvayQuestion\', WhereStatement=\'Next 12 Id\', \'lala\'){Name=NextQuestions}->({GetDataConditionObject.Result} ? GetDataAction(DataType=\'SurvayQuestion\', WhereStatement=\'Next 12 Id\'){Name=NextQuestions}=>(SaveDataAction(DataType=\'Answer\', Data=([DataPackage.Data]=>[new Answer(QuestionId=Id, User=Global.Tasks.Survay.id)])){Name=SaveQuestionAction}->/GetQuestion/))->{!GetDataConditionObject.Result} ? ChangeRoute(\'SurveyWellcomeComponent\') '
        self.actionConfigs = ''
        self.dataPackageConfigs = ''

        self.data_package_configs = ''
        self.action_configs = ''
        self.parsed = False

    def getActionsByString7(self, actions_string, data_package_configs, action_configs):
        self.data_package_configs = data_package_configs
        self.action_configs = action_configs
        if not self.parsed:
            self.getActionsByString2(self.parseSting, self.data_package_configs, self.action_configs)
        self.parsed = True
        return ServerAction()

    def getActionsByString(self, actions_string, data_package_configs, action_configs):
        if actions_string is None:
            return []
        actions_string = actions_string.replace('\n', '').replace('\r', '').replace('\t', '')
        print(actions_string)
        # actions_string = self.parseSting
        self.dataPackageConfigs = data_package_configs
        self.actionConfigs = action_configs

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

            action = self.__getActionByValueList__(action_value_list)
            actions.append(action)
        return actions

    def __createServerActionByHelpingAction__(self, action):
        action_input_descriptions = []
        counter = 0
        server_action = ServerAction()
        for value in action.values:
            if value['valueName'] == 'condition':
                server_action.Condition = value['value']

            if value['valueName'] == 'type':
                server_action.Type = value['value']
                server_action.Name = value['value']
                print('####', server_action.Type)

            if value['valueName'] == 'actionDescription':
                server_action.Type = value['value']
                server_action.Name = value['value']
                print('####', server_action.Type)
                server_action.IsDescription = True
                return server_action

            if value['valueName'] == 'komplexCode' or value['valueName'] == 'inputValueConst' or \
                    value['valueName'] == 'inputValueBinding' or value['valueName'] == 'inputValueNew' or \
                    value['valueName'] == 'inputValueName':
                action_input_descriptions.append({'valueName': value['valueName'], 'value': value['value']})

            if value['valueName'] == 'actionPropertyName':
                setattr(server_action, value['value'], action.values[counter + 1]['value'])
            counter += 1

        for output_action in action.outputActions:
            server_action.OutputServerActions.append(self.__createServerActionByHelpingAction__(output_action))
        for next_action in action.nextActions:
            server_action.NextActions.append(self.__createServerActionByHelpingAction__(next_action))

        self.__setInputValues__(server_action, action_input_descriptions)
        self.__setActionExecute__(server_action)
        self.__setActionContext__(server_action)
        return server_action

    def __getActionByValueList__(self, value_list):
        group_list = self.__getGroupList__(value_list, 0)
        action = self.__createServerActionByHelpingAction__(self.__getHelpingActionByGroupList__(group_list))
        return action

    def __getHelpingActionByGroupList__(self, group_list):
        action = ActionHelpingObject()
        next_action = ActionHelpingObject()
        out_action = ActionHelpingObject()
        state = 'first'
        counter = 0
        while counter < len(group_list):
            if isinstance(group_list[counter], list):
                if state == 'next':
                    action.nextActions.append(self.__getHelpingActionByGroupList__(group_list[counter]))
                    state = ''
                if state == 'out':
                    action.outputActions.append(self.__getHelpingActionByGroupList__(group_list[counter]))
                    state = ''
            else:
                if group_list[counter]['valueName'] == 'outputServerAction' or \
                        group_list[counter]['valueName'] == 'nextAction':
                    if state == 'next':
                        action.nextActions.append(next_action)
                    if state == 'out':
                        action.outputActions.append(out_action)

                if group_list[counter]['valueName'] == 'outputServerAction':
                    out_action = ActionHelpingObject()
                    state = 'out'
                if group_list[counter]['valueName'] == 'nextAction':
                    next_action = ActionHelpingObject()
                    state = 'next'

                if state == 'next':
                    next_action.values.append(group_list[counter])
                if state == 'out':
                    out_action.values.append(group_list[counter])
                if state == 'first':
                    action.values.append(group_list[counter])
            counter += 1
        if state == 'next':
            action.nextActions.append(next_action)
        if state == 'out':
            action.outputActions.append(out_action)
        return action

    def __getGroupList__(self, value_list, counter):
        group_list = []
        start_with_group_start = False
        if value_list[counter]['valueName'] == 'groupStart':
            counter += 1
            start_with_group_start = True
        while counter < len(value_list):
            group_list.append(value_list[counter])
            if value_list[counter]['valueName'] == 'groupStart':
                next_group_list = self.__getGroupList__(value_list, counter)
                group_list.append(next_group_list)
                counter += self.countGroupList(next_group_list)
            elif value_list[counter]['valueName'] == 'groupEnd':
                if start_with_group_start:
                    return group_list
                else:
                    self.loggingService.log('ActionParseError Klammer zu viel geschlossen')
                    return None
            counter += 1
        if start_with_group_start:
            self.loggingService.log('ActionParseError Klammer nicht geschlossen')
        else:
            return group_list
        return None

    def countGroupList(self, _list):
        counter = 0
        for i in _list:
            if isinstance(i, list):
                counter += self.countGroupList(i)
            else:
                counter += 1
        return counter

    def __parseString__(self, string):
        counter = 0
        current_states = [self.startState]
        current_name_values = [{'state': self.startState, 'valueName': '', 'value': ''}]
        found_values = []
        while counter < len(string):
            transitions = self._getTransitions(current_states, counter, string)

            if len(transitions) == 0:
                self.loggingService.log('parseActionError [' + string + '] at position ' + str(counter) + ' \'' + string[counter] + '\'')
                return None

            for current_name_value in current_name_values:
                delete_values = []
                is_there_a_transition = False
                for transition in transitions:

                    if transition.firstKnote == current_name_value['state']:
                        if (transition.name != current_name_value['valueName'] or transition.name in self.singleValueNameTransitions) \
                                and current_name_value['valueName'] != '':
                            found_values.append(current_name_value)
                            #self.loggingService.logObject(transition)
                            #print(current_name_value, current_name_values)
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
                    if transition.name == old_name_value['valueName'] and old_name_value['valueName'] not in self.singleValueNameTransitions:
                        transition_string = old_name_value['value'] + transition_string

                if transition.name != '':
                    current_name_values.append({'state': transition.targetKnote, 'valueName': transition.name, 'value': transition_string})
                current_states.append(transition.targetKnote)
            counter = counter + transition_length

        #if len(current_name_values) > 0:
            #found_values.append(current_name_values[0])
        for final_state in self.finalStates:
            if final_state in current_states:
                return found_values

        self.loggingService.log(
            'parseActionError [' + string + '] at not valid')
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

    def __setInputValues__(self, action, action_input_descriptions):
        list_of_expected_inputs = []
        # set default inputs in action
        for action_config in self.actionConfigs:
            if action.Type == action_config.type:
                list_of_expected_inputs = action_config.input
        for _input in list_of_expected_inputs:
            action.Input[_input] = ''

        # set input_values {type, input, name}
        input_values = []
        counter = 0
        for input_description in action_input_descriptions:
            if input_description['valueName'] == 'komplexCode' or input_description['valueName'] == 'inputValueConst' or input_description['valueName'] == 'inputValueBinding' or input_description['valueName'] == 'inputValueNew':
                name = ''
                if action_input_descriptions[counter - 1]['valueName'] == 'inputValueName':
                    name = action_input_descriptions[counter - 1]['value']
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
                action.Input[input_value['name']] = self.__getDataPackageByName__(input_value['input'], self.dataPackageConfigs)
            if input_value['type'] == 'komplexCode':
                action.KomplexCode.append({'name': input_value['name'], 'code': input_value['input']})

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

    @staticmethod
    def __setActionContext__(action):
        if action.Execute == 'Client':
            action.Context = ''
        else:
            if action.Context == '':
                action.Context = 'Component'

    def __setActionExecute__(self, action):
        for action_config in self.actionConfigs:
            if action_config.type == action.Type:
                action.Execute = action_config.execute
                action.Opening = action_config.opening


class Transition:
    def __init__(self, first, trans, target, name):
        self.firstKnote = first
        self.tansitionString = trans
        self.targetKnote = target
        self.name = name


class ActionHelpingObject:
    def __init__(self):
        self.values = []
        self.nextActions = []
        self.outputActions = []
