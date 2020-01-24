import string
import random

from objects.screenContext import ScreenContext
from services.dataService import DataService


class Session:
    dataService = DataService.getInstance()
    token = ''
    id = ''
    loginState = ''
    totalTime = 0
    lastRequestInSeconds = 0
    screeContext = {}
    alwaysAvailableActions = []

    def __init__(self, session_id):
        self.screeContext = ScreenContext()
        self.token = self.get_random_string(20) + str(session_id)
        self.id = session_id

        action_decriptions = self.dataService.getServerActionDescriptions()
        for action_decription in action_decriptions:
            if action_decription['Opening'] == 1:
                self.alwaysAvailableActions.append(action_decription['Type'])

    @staticmethod
    def get_random_string(string_length=10):
        letters = string.ascii_uppercase
        return ''.join(random.choice(letters) for i in range(string_length))

    def login(self, password):
        if self.dataService.check_passwords(password):
            return {'Token': self.token, 'Role': self.dataService.getRoleByPassword(password)}
        return None

    def checkIfActionIsAvailable(self, action):
        for always_available_action in self.alwaysAvailableActions:
            if always_available_action == action.Type:
                return True
        for current_action in self.screeContext.ServerActions:
            if current_action.Id == action.Id and current_action.Type == action.Type:
                return True
        return False
