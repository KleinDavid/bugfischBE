import mysql.connector
from mysql.connector import Error
from objects.configObjects.actionConfig import ActionConfig
from objects.configObjects.dataPackageConfig import DataPackageConfig
from objects.configObjects.dea import Dea
from objects.configObjects.screenConfig import ScreenConfig
from services.loggingService import LoggingService


class ConfigService:

    __instance = None
    __loggingService = LoggingService()

    @staticmethod
    def getInstance():
        if ConfigService.__instance is None:
            ConfigService()
        return ConfigService.__instance

    def __init__(self):
        if ConfigService.__instance is not None:
            raise Exception("This class is a singleton!")
        else:
            ConfigService.__instance = self

        self.actionConfigs = []
        self.screenConfigs = []
        self.referenceConfigs = []
        self.dataPackageConfigs = []
        self.dea = Dea()

    def initConfig(self):
        connection = mysql.connector.connect(
            # database="jschelp",
            # user="jschelp",
            # passwd="HU&43jdJK)82HU&43jdJK)82",
            # use_pure=True)
            host="localhost",
            database="jugend.config",
            user="root",
            passwd="HU&43jdJK)82")
        if connection.is_connected():
            config_data_base = connection
            db_info = connection.get_server_info()
            self.__loggingService.log("Connected to MySQL Server version " + db_info)
            cursor = connection.cursor()
            cursor.execute("select database();")
            record = cursor.fetchone()
            # self.__loggingService.log("You're connected to database: " + record)

            cursor = config_data_base.cursor(dictionary=True)
            cursor.execute("SELECT * FROM datapackages")
            result = cursor.fetchall()
            self.initDataPackageConfigs(result)

            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM serveractions")
            result = cursor.fetchall()
            self.initActionConfigs(result)

            cursor = config_data_base.cursor(dictionary=True)
            cursor.execute("SELECT * FROM screenconfig")
            result = cursor.fetchall()
            self.initScreenConfigs(result)

    def initActionConfigs(self, data):
        for action_decription in data:
            action_config = ActionConfig()
            action_config.type = action_decription['Type']
            action_config.execute = action_decription['Execute']
            action_config.outputData = action_decription['OutputData']
            action_config.opening = action_decription['Opening']
            action_config.input = action_decription['Input'].replace(' ', '').split(',')
            self.actionConfigs.append(action_config)

        counter = 0
        for action_config in self.actionConfigs:
            action_config.outputClientActions = self.dea.getActionsByString(data[counter]['OutputClientAction'], self.dataPackageConfigs, self.actionConfigs)
            action_config.outputServerActions = self.dea.getActionsByString(data[counter]['OutputServerAction'], self.dataPackageConfigs, self.actionConfigs)
            action_config.useActions = self.dea.getActionsByString(data[counter]['UseAction'], self.dataPackageConfigs, self.actionConfigs)

    def initScreenConfigs(self, data):
        for screen_decription in data:
            screen_config = ScreenConfig()
            screen_config.outputServerActions = self.dea.getActionsByString(screen_decription['OutputServerActions'], self.dataPackageConfigs, self.actionConfigs)
            screen_config.useAction = self.dea.getActionsByString(screen_decription['UseAction'], self.dataPackageConfigs, self.actionConfigs)
            screen_config.componentName = screen_decription['ComponentName']
            screen_config.startScreen = screen_decription['StartScreen']
            for ua in screen_config.useAction:
                self.__loggingService.logObject(ua)

    def initReferenceConfigs(self, data):
        for reference_decription in data:
            print('')

    def initDataPackageConfigs(self, data):
        for data_package_decription in data:
            data_package_config = DataPackageConfig()
            data_package_config.name = data_package_decription['Name']
            data_package_config.properties = data_package_decription['Properties'].replace(' ', '').split(',')
            self.dataPackageConfigs.append(data_package_config)

    def getActionsByArrayString(self, array_str):
        counter = 0
