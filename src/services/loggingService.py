from datetime import datetime


class LoggingService:

    @staticmethod
    def log(message):
        now = datetime.now()
        dt_string = '[' + now.strftime("%d/%b/%Y %H:%M:%S") + ']'
        massage_string = dt_string + ' "' + message + '"'
        print(massage_string)
        file = open("log.log", "a")
        file.write(massage_string + "\n")
        file.close()

    def error(self, message):
        self.log(Bcolors.WARNING + message)

    def logServerResult(self, server_result):
        string = 'Send ServerResult | Actions = ['
        for server_action in server_result.Actions:
            action_string = '{\'Type\': \'' + str(server_action.Type) + '\', \'Input\': \'' + str(server_action.Input) + '\'}'
            string = string + action_string

        string = string + '] | ClientActions = ['

        string = string + ']'
        self.log(string)


class Bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'