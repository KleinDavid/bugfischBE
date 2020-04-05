import mysql.connector
from datetime import datetime
from mysql.connector import Error
from services.configService import ConfigService
from services.loggingService import LoggingService
import json
import time
from random import randrange


class DataService(object):
    __instance = None
    __loggingService = LoggingService()
    __configService = ConfigService.getInstance()
    runningInsert = False

    @staticmethod
    def getInstance():
        # if DataService.__instance is None:
        #    DataService()
        # return DataService.__instance
        return DataService()

    def __init__(self):
        # if DataService.__instance is not None:
        #    raise Exception("This class is a singleton!")
        # else:
        #    DataService.__instance = self

        self.configJsonData = ''
        with open('config.json') as json_file:
            self.configJsonData = json.load(json_file)

        self.connection = None
        self.__connection = None
        self.connectWithInfo()

    def connectWithInfo(self):
        self.connect()
        try:
            if self.connection.is_connected():
                db_info = self.connection.get_server_info()
                print("Connected to MySQL Server version ", db_info)
                cursor = self.connection.cursor()
                cursor.execute("select database();")
                record = cursor.fetchone()
                print("You're connected to database: ", record)
        except Error as e:
            print("Error while connecting to MySQL: ", e)

    def connect(self):
        self.connection = mysql.connector.connect(
            host=self.configJsonData["database"]["host"],
            database=self.configJsonData["database"]["database"],
            user=self.configJsonData["database"]["user"],
            passwd=self.configJsonData["database"]["password"],
            use_pure=True)

    def check_passwords(self, password):
        query = "SELECT * FROM passwörter WHERE passwort = \'" + password + "\'"
        res = self.runQueryWithMultiResult(query)
        if len(res) > 0:
            return True
        return False

    def getRoleByPassword(self, password):
        res = self.runQueryWithMultiResult("SELECT * FROM passwörter WHERE passwort = \'" + password + "\'")
        if len(res) > 0:
            return res[0]["rolle"]
        return False

    def mapDataBaseResultToObject(self, table, select_by, select_value, result_object):
        query = 'SELECT * FROM `' + table + '` WHERE ' + select_by + ' = \'' + select_value + '\''
        res = self.runQueryWithSingleResult()
        if not res:
            return None
        for attr in result_object.__dict__.items():
            try:
                setattr(result_object, attr[0], res[attr[0]])
            except Error as e:
                print(e)
        # pprint(vars(result_object))

    def getDataPackageByName(self, name):
        data_package = {}
        for propertie in self.__configService.getDatPackageConfigByName(name).properties:
            if propertie.find(':') != -1:
                data_package[propertie.split(':')[0]] = self.getDataPackageByName(propertie.split(':')[1])
            else:
                data_package[propertie] = ''
        return data_package

    def saveDataPackageInDataBase(self, table_name, data):
        properties = self.__configService.getDatPackageConfigByName(table_name).properties
        columns = ''
        values = ''
        for prop in properties:
            if len(columns) == 0:
                columns = columns + '`' + prop + '`'
                values = values + '\'' + str(data[prop]).replace('\'', '\\' + '\'') + '\''
            else:
                columns = columns + ', `' + prop + '`'
                values = values + ', \'' + data[prop].replace('\'', '\\' + '\'') + '\''

        query = 'INSERT INTO `' + table_name.lower() + '` (' + columns + ') VALUES (' + values + ');'
        self.runQueryWithoutResult(query)

    def getMinIdByDataType(self, data_type):
        query = 'SELECT MIN(Id) FROM ' + data_type.lower()
        res = self.runQueryWithSingleResult(query)
        if not res:
            return None
        return res['MIN(Id)']

    def getDataPackage(self, data_type, where_statemante):
        query = 'SELECT * FROM ' + data_type.lower() + ' WHERE ' + where_statemante
        res = self.runQueryWithMultiResult(query)
        if not res:
            return None

        # **get Reference
        for ref in self.__configService.getReferenceConfigListByParentTable(data_type.lower()):
            for value in res:
                child_id = str(value[ref.ParentField])
                if child_id != '':
                    if ref.Type == '1:1':
                        child = self.getOneDataObjectByFieldValue(ref.ChildTable, ref.ChildField, child_id)
                        child_object = {}
                        for field_name in ref.ChildFieldNames:
                            child_object[field_name] = child[field_name]
                        value[ref.ParentFieldName] = child_object
                    if ref.Type == '1:n':
                        childs = self.getDataObjectsByFieldValue(ref.ChildTable, ref.ChildField, child_id)

                        childs_object = {}
                        counter = 0
                        for val in childs:
                            child_object = {}
                            for field_name in ref.ChildFieldNames:
                                child_object[field_name] = val[field_name]
                            childs_object[counter] = child_object
                            counter = counter + 1
                        value[ref.ParentFieldName] = childs_object
        # get Reference**

        res_object = {}
        counter = 0
        for value in res:
            res_object[counter] = value
            counter = counter + 1
        return res_object

    def getScreenByStartScreen(self, start_screen):
        query = 'SELECT * FROM `' + 'screenconfig' + '` WHERE StartScreen = \'' + start_screen + '\''
        cursor = self._dataBase.cursor(dictionary=True)
        cursor.execute(query)
        res = cursor.fetchall()
        return res[0]

    def getReferences(self, data_package_name):
        query = 'SELECT * FROM `' + 'references' + '` WHERE parentTable = \'' + data_package_name.lower() + '\''
        cursor = self._dataBase.cursor(dictionary=True)
        cursor.execute(query)
        res = cursor.fetchall()
        return res

    def getDataObjectById(self, table_name, data_id):
        query = 'SELECT * FROM `' + table_name.lower() + '` WHERE ID = \'' + data_id + '\''
        cursor = self._dataBase.cursor(dictionary=True)
        cursor.execute(query)
        res = cursor.fetchall()
        return res[0]

    def getOneDataObjectByFieldValue(self, table_name, value_name, value):
        query = 'SELECT * FROM `' + table_name.lower() + '` WHERE ' + value_name + ' = \'' + value + '\''
        return self.runQueryWithSingleResult(query)

    def getDataObjectsByFieldValue(self, table_name, value_name, value):
        query = 'SELECT * FROM `' + table_name.lower() + '` WHERE ' + value_name + ' = \'' + value + '\''
        res = self.runQueryWithMultiResult(query)
        return res

    def saveNewSession(self, session):
        query = 'SELECT MAX(ID) FROM `sessions`'
        res = self.runQueryWithSingleResult(query)

        max_id = res['MAX(ID)']
        if not max_id:
            max_id = 0
        now = datetime.now().strftime("%d/%b/%Y %H:%M:%S")
        query = 'INSERT INTO `sessions` (`ID`, `Token`, `Date`) VALUES (' + str(int(max_id) + 1) + ', \'' + session.token + '\', \'' + now + '\');'
        self.runQueryWithoutResult(query)
        return str(int(max_id) + 1)

    def saveNewTask(self, task):
        query = 'SELECT MAX(ID) FROM `tasks`'
        res = self.runQueryWithSingleResult(query)
        max_id = res['MAX(ID)']
        if not max_id:
            max_id = 0
        query = 'INSERT INTO `tasks` (`ID`, `name`, `sessionTotalId`, `State`) VALUES (' + str(
            int(max_id) + 1) + ', \'' + task.name + '\', \'' + task.sessionTotalId + '\', \'' + task.state + '\');'
        self.runQueryWithoutResult(query)
        return str(int(max_id) + 1)

    def runQueryWithSingleResult(self, query):
        if not self.runningInsert:
            self.runningInsert = True
            res = self.getCurser(query).fetchall()[0]
            self.runningInsert = False
            return res
        else:
            sleep_time = randrange(100) / 10
            time.sleep(sleep_time)
            return self.runQueryWithSingleResult(query)

    def runQueryWithMultiResult(self, query):
        if not self.runningInsert:
            self.runningInsert = True
            res = self.getCurser(query).fetchall()
            self.runningInsert = False
            return res
        else:
            sleep_time = randrange(100) / 10
            time.sleep(sleep_time)
            return self.runQueryWithMultiResult(query)

    def runQueryWithoutResult(self, query):
        if not self.runningInsert:
            self.runningInsert = True
            self.getCurser(query)
            self.connection.commit()
            self.runningInsert = False
        else:
            sleep_time = randrange(100) / 10
            time.sleep(sleep_time)
            self.runQueryWithoutResult(query)

    def getCurser(self, query):
        try:
            if self.connection.is_connected():
                cursor = self.connection.cursor(dictionary=True)
                cursor.execute(query)
            else:
                sleep_time = randrange(100) / 10
                time.sleep(sleep_time)
                self.connect()
                return self.getCurser(query)
        except Error as e:
            sleep_time = randrange(100) / 10
            time.sleep(sleep_time)
            self.connect()
            return self.getCurser(query)
        return cursor
