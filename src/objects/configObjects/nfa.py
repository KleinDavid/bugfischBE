import re
from services.loggingService import LoggingService
from xml.dom import minidom
import re


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
                regex = sequenceFlow.getAttribute('name')
                name = sequenceFlow.getElementsByTagName('bpmn:documentation')
                if len(name) > 0:
                    name = name[0].firstChild.nodeValue
                else:
                    name = ''
                transition = Transition(source, regex, tartet, name)
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
        action_string = 'action1(uu=hallo.hallo1, mango=\'Frucht\'){}->apfel(){name=husten}'
        actionParser = ActionParser(self.transitions, self.startEvents, self.endConditions, action_string)


class TreeNode:
    def __init__(self):
        self.name = ''
        self.value = ''
        self.condition = ''
        self.target_id = ''
        self.children = []


class ActionParser:
    loggingService = LoggingService()

    def __init__(self, transitions, start_conditions, end_conditions, action_string):
        self.transitions = transitions
        self.startConditions = start_conditions
        self.actionString = action_string
        self.endConditions = end_conditions
        for start_condition in self.startConditions:
            for x in self.parseActionDescription(start_condition, self.actionString):
                x = self.clearTree(x)
                self.printTree(x, 0)

    def parseActionDescription(self, start_condition, line):
        tree_nodes = []
        print(start_condition, line)
        transitions = self.getTransitionByCondition(start_condition)
        for transition in transitions:
            print(transition.regEx)
            p = re.compile(transition.regEx)
            matches = [x for x in p.finditer(line) if x.start() == 0]
            for match in matches:
                tree_node = TreeNode()
                tree_node.name = transition.name
                tree_node.value = match.group()
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


    def getTransitionByCondition(self, condition):
        return [x for x in self.transitions if x.firstKnote == condition]

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
    def __init__(self, first, reg_ex, target, name):
        self.firstKnote = first
        self.regEx = reg_ex
        self.targetKnote = target
        self.name = name
