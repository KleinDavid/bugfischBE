from __future__ import annotations
import mysql.connector
from models.ServerAction import ServerAction
from objects.configObjects.actionConfig import ActionConfig
from objects.configObjects.actionDescriptionConfig import ActionDescriptionConfig
from objects.configObjects.dataPackageConfig import DataPackageConfig
from objects.configObjects.dea import Dea
from objects.configObjects.referenceConfig import ReferenceConfig
from objects.configObjects.screenConfig import ScreenConfig
from services.loggingService import LoggingService

import copy


class ConfigService:

    __instance = None
    __loggingService = LoggingService()

    @staticmethod
    def getInstance() -> ConfigService:
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
        self.actionDescriptionConfigs = []
        self.dea = Dea()
        self.__initConfig__()

    def __initConfig__(self):
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

            self.actionConfigs = []
            self.screenConfigs = []
            self.referenceConfigs = []
            self.dataPackageConfigs = []
            self.actionDescriptionConfigs = []

            cursor = config_data_base.cursor(dictionary=True)
            cursor.execute("SELECT * FROM datapackages")
            result = cursor.fetchall()
            self.__initDataPackageConfigs__(result)

            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM serveractions")
            result = cursor.fetchall()
            self.__initActionConfigs__(result)

            cursor = config_data_base.cursor(dictionary=True)
            cursor.execute("SELECT * FROM `actiondescriptions`")
            result = cursor.fetchall()
            self.__initActionDescriptions__(result)

            cursor = config_data_base.cursor(dictionary=True)
            cursor.execute("SELECT * FROM screenconfig")
            result = cursor.fetchall()
            self.__initScreenConfigs__(result)

            cursor = config_data_base.cursor(dictionary=True)
            cursor.execute("SELECT * FROM `references`")
            result = cursor.fetchall()
            self.__initReferenceConfigs__(result)

    def __initActionConfigs__(self, data):
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
            action_config.outputClientActions = self.dea.getActionsByString(data[counter]['OutputClientActions'], self.dataPackageConfigs, self.actionConfigs)
            action_config.outputServerActions = self.dea.getActionsByString(data[counter]['OutputServerActions'], self.dataPackageConfigs, self.actionConfigs)
            action_config.useActions = self.dea.getActionsByString(data[counter]['UseActions'], self.dataPackageConfigs, self.actionConfigs)
            counter = counter + 1

    def __initScreenConfigs__(self, data):
        for screen_decription in data:
            screen_config = ScreenConfig()
            screen_config.outputServerActions = self.dea.getActionsByString(screen_decription['OutputServerActions'], self.dataPackageConfigs, self.actionConfigs)
            screen_config.useActions = self.dea.getActionsByString(screen_decription['UseActions'], self.dataPackageConfigs, self.actionConfigs)
            screen_config.componentName = screen_decription['ComponentName']
            screen_config.startScreen = screen_decription['StartScreen']
            self.screenConfigs.append(screen_config)

    def __initActionDescriptions__(self, data):
        for action_description in data:
            action_decription_config = ActionDescriptionConfig()
            action_decription_config.action = self.dea.getActionsByString(action_description['Description'], self.dataPackageConfigs, self.actionConfigs)[0]
            action_decription_config.name = action_description['Name']
            action_decription_config.id = action_description['ID']
            self.actionDescriptionConfigs.append(action_decription_config)

    def __initReferenceConfigs__(self, data):
        for reference_decription in data:

            reference = ReferenceConfig()
            reference.ID = reference_decription['ID']
            reference.Type = reference_decription['Type']
            reference.ChildField = reference_decription['ChildField']
            reference.ChildFieldNames = reference_decription['ChildFieldNames'].replace(' ', '').split(',')
            reference.ChildTable = reference_decription['ChildTable']
            reference.ParentField = reference_decription['ParentField']
            reference.ParentFieldName = reference_decription['ParentFieldName']
            reference.ParentTable = reference_decription['ParentTable']
            self.referenceConfigs.append(reference)

    def __initDataPackageConfigs__(self, data):
        for data_package_decription in data:
            data_package_config = DataPackageConfig()
            data_package_config.name = data_package_decription['Name']
            data_package_config.properties = data_package_decription['Properties'].replace(' ', '').split(',')
            self.dataPackageConfigs.append(data_package_config)

    def getScreenConfigByComponentName(self, name) -> ScreenConfig:
        return copy.deepcopy(list(filter(lambda x: x.componentName == name, self.screenConfigs))[0])

    def getScreenConfigByStartScreen(self, start_screen) -> ScreenConfig:
        return copy.deepcopy(list(filter(lambda x: x.startScreen == start_screen, self.screenConfigs))[0])

    def getActionConfigByType(self, _type):
        return copy.deepcopy(list(filter(lambda x: x.type == _type, self.actionConfigs))[0])

    def getAllOpeningActions(self):
        action_descriptions = list(filter(lambda x: x.opening == '1', self.actionConfigs))
        actions = []
        for action_description in action_descriptions:
            action = ServerAction()
            action.Type = action_description.type
            action.Name = action_description.type
            actions.append(action)
        return actions

    def getReferenceConfigListByParentTable(self, parent_table):
        return list(filter(lambda x: x.ParentTable == parent_table, self.referenceConfigs))

    def getDatPackageConfigByName(self, name) -> DataPackageConfig:
        return list(filter(lambda x: x.name == name, self.dataPackageConfigs))[0]

