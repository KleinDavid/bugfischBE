import re
from services.loggingService import LoggingService
from xml.dom import minidom
import re
from models.ServerAction import ServerAction


class Nfa:
    loggingService = LoggingService()
    transitions = []
    startEvents = []
    states = []
    endConditions = []

    def __init__(self):
        path = '../config/ActionDescriptionLaguage.bpmn'
        with open(path, 'r') as myfile:
            data = myfile.read()
            dom_tree = minidom.parseString(data)
            for sequenceFlow in dom_tree.getElementsByTagName('bpmn:sequenceFlow'):
                source = sequenceFlow.getAttribute('sourceRef')
                tartet = sequenceFlow.getAttribute('targetRef')
                name_list = sequenceFlow.getAttribute('name').split(' ')
                regex = name_list[0]
                stack = ''
                if len(name_list) > 1:
                    stack = name_list[1]
                name = sequenceFlow.getElementsByTagName('bpmn:documentation')
                if len(name) > 0:
                    name = name[0].firstChild.nodeValue
                else:
                    name = ''
                transition = Transition(source, regex, tartet, name, stack)
                self.transitions.append(transition)
            start_events = dom_tree.getElementsByTagName('bpmn:startEvent')
            for start_event in start_events:
                start_event_id = start_event.getAttribute('id')
                self.startEvents.append(start_event_id)
            end_conditions = dom_tree.getElementsByTagName('bpmn:intermediateThrowEvent')
            print(end_conditions)
            for end_condition in end_conditions:
                end_condition_child = end_condition.getElementsByTagName('bpmn:escalationEventDefinition')
                if len(end_condition_child) > 0:
                    self.endConditions.append(end_condition.getAttribute('id'))
                    print('###########', end_condition.getAttribute('id'))
            self.parseActionDescription('meineAction()')

    def parseActionDescription(self, action_string):
        path = '../config/test.action'
        with open(path, 'r') as action_file:
            action_string = action_file.read().replace("\r", "").replace("\n", "").replace("\t", "").replace("    ", "")
            action_parser = ActionParser(self.transitions, self.startEvents, self.endConditions)
            action_parser.parseActionString(action_string)

        #action_string = 'GetDataCondition(DataType=\'SurvayQuestion\', WhereStatement=\'next 12 Id\', \'lala\', myBinding=david.klein){Name=NextQuestions}->zweiteAction(input=\'meininput\')'
        #


class TreeNode:
    def __init__(self):
        self.name = ''
        self.value = ''
        self.condition = ''
        self.target_id = ''
        self.stack = ''
        self.children = []


class ActionParser:
    loggingService = LoggingService()

    def __init__(self, transitions, start_conditions, end_conditions):
        self.transitions = transitions
        self.startConditions = start_conditions
        self.endConditions = end_conditions

    def parseActionString(self, action_string):
        for start_condition in self.startConditions:
            for tree in self.parseActionDescription(start_condition, action_string):
                tree = self.clearTree(tree)
                if not tree:
                    self.loggingService.error('can\'t parse action')
                self.checkStack(tree)

                self.printTree(tree, 0)
                self.getServerActionByTree(ServerAction(), tree)

    def parseActionDescription(self, start_condition, line):
        tree_nodes = []
        # print(start_condition, line)
        transitions = self.getTransitionByCondition(start_condition)
        for transition in transitions:
            # print(transition.regEx)
            p = re.compile(transition.regEx)
            matches = [x for x in p.finditer(line) if x.start() == 0]
            for match in matches:
                tree_node = TreeNode()
                tree_node.name = transition.name
                tree_node.value = match.group()
                tree_node.stack = transition.stack
                tree_node.target_id = transition.targetKnote
                tree_node.children = self.parseActionDescription(tree_node.target_id, line[match.end():])
                tree_nodes.append(tree_node)

            for m in matches:
                print(m.start(), m.group(), m.end())
        return tree_nodes

    def clearTree(self, tree):
        remaining_children = []
        for child in tree.children:
            child = self.clearTree(child)
            if child:
                remaining_children.append(child)
        if len(remaining_children) > 0:
            tree.children = remaining_children
            return tree
        elif tree.target_id in self.endConditions:
            return tree
        else:
            return None

    def checkStack(self, tree):
        print(self.initStack(tree, []))

    def initStack(self, tree, stack):
        if len([x for x in stack if x['name'] == tree.name and x['name'] is not '']) == 0:
            stack.append({'name': tree.name, 'count': 0})
        node = [x for x in stack if x['name'] == tree.name][0]
        if tree.stack is '+':
            node['count'] += 1
        if tree.stack is '-':
            node['count'] -= 1
        if node['count'] < 0:
            self.loggingService.error('Action Parse Error: to stack -1 ' + tree.name)
            return None

        print(node)
        if len(tree.children) > 0:
            stack = self.initStack(tree.children[0], stack)
        return stack

    def getTransitionByCondition(self, condition):
        return [x for x in self.transitions if x.firstKnote == condition]

    def getServerActionByTree(self, server_action, tree):
        if tree.name is 'actionName':
            server_action.Name = tree.value

        return server_action

    def printTree(self, tree, deep):
        counter = 0
        string = ''
        while counter < deep:
            string += ' '
            counter += 1
        print(string + tree.value + ' ' + tree.name + ' ' + str(len(tree.children)))
        for x in tree.children:
            self.printTree(x, deep + 1)


class Transition:
    def __init__(self, first, reg_ex, target, name, stack):
        self.firstKnote = first
        self.regEx = reg_ex
        self.targetKnote = target
        self.name = name
        self.stack = stack


class ActionHelpingObject:
    def __init__(self):
        self.values = []
        self.nextActions = []
        self.outputActions = []
