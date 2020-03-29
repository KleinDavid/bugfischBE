from __future__ import annotations
import mysql.connector
from datetime import datetime
from mysql.connector import Error
from services.configService import ConfigService
from services.loggingService import LoggingService


class DataService(object):
    _dataBase = None
    __instance = None
    __loggingService = LoggingService()
    __configService = ConfigService.getInstance()

    @staticmethod
    def getInstance() -> DataService:
        if DataService.__instance is None:
            DataService()
        return DataService.__instance

    def __init__(self):
        if DataService.__instance is not None:
            raise Exception("This class is a singleton!")
        else:
            DataService.__instance = self

        self.getDataBaseConnection()

    def getDataBaseConnection(self):
        try:
            connection = mysql.connector.connect(
                host="localhost",
                #database="jschelp",
                #user="jschelp",
                #passwd="HU&43jdJK)82HU&43jdJK)82",
                #use_pure=True)
                database="jugend",
                user="root",
                passwd="HU&43jdJK)82")
            if connection.is_connected():
                db_info = connection.get_server_info()
                print("Connected to MySQL Server version ", db_info)
                cursor = connection.cursor()
                cursor.execute("select database();")
                record = cursor.fetchone()
                print("You're connected to database: ", record)
                self._dataBase = connection

        except Error as e:
            print("Error while connecting to MySQLuuu: ", e)

    def checkDataBaseConnection(self):
        if self._dataBase.is_connected():
            return True
        else:
            self._dataBase.close()
            self.getDataBaseConnection()
            return False

    def check_passwords(self, password):
        cursor = self._dataBase.cursor(dictionary=True)
        cursor.execute("SELECT * FROM passwörter")
        myresult = cursor.fetchall()

        for x in myresult:
            if str(x["passwort"]) == str(password):
                return True

        return False

    def getRoleByPassword(self, password):
        cursor = self._dataBase.cursor(dictionary=True)
        cursor.execute("SELECT * FROM passwörter")
        myresult = cursor.fetchall()

        for x in myresult:
            if str(x["passwort"]) == str(password):
                return x["rolle"]
        return False

    def saveQuestion(self, question):
        cursor = self._dataBase.cursor(dictionary=True)
        sql = "INSERT INTO `questions` (`ID`, `question`) VALUES (%s, %s)"
        val = ("NULL", question)
        cursor.execute(sql, val)
        self._dataBase.commit()
        LoggingService.log('safe Question: \'' + question + '\'')
        return True

    def getRouteData(self, component):
        cursor = self._dataBase.cursor(dictionary=True)
        cursor.execute("SELECT * FROM screenconfig WHERE ComponentName = \'" + component + "\'")
        res = cursor.fetchall()

        if res is not None and res[0] is not None:
            return res[0]

        return None

    def getActionByName(self, action_name):

        cursor = self._dataBase.cursor(dictionary=True)
        cursor.execute("SELECT * FROM serveractions WHERE Type = \'" + action_name + "\'")
        res = cursor.fetchall()
        if not res:
            return None
        return res[0]

    def getServerActionDescription(self, action_type):
        cursor = self._dataBase.cursor(dictionary=True)
        query = 'SELECT * FROM `serveractions` WHERE Type = \'' + action_type + '\''
        cursor.execute(query)
        res = cursor.fetchall()
        if not res:
            return None
        return res[0]

    def getServerActionDescriptions(self):
        cursor = self._dataBase.cursor(dictionary=True)
        cursor.execute('SELECT * FROM `serveractions` WHERE Opening = \'1\'');
        res = cursor.fetchall()
        if not res:
            return None
        return res

    def getDataPackageDescription(self, package_name):
        cursor = self._dataBase.cursor(dictionary=True)
        cursor.execute('SELECT * FROM `datapackages` WHERE Name = \'' + package_name + '\'')
        res = cursor.fetchall()
        if not res:
            return None
        res[0]['Properties'] = res[0]['Properties'].replace(' ', '')
        self._dataBase.commit()
        return res[0]

    def mapDataBaseResultToObject(self, table, select_by, select_value, result_object):
        query = 'SELECT * FROM `' + table + '` WHERE ' + select_by + ' = \'' + select_value + '\''
        cursor = self._dataBase.cursor(dictionary=True)
        cursor.execute(query)
        res = cursor.fetchall()
        if not res:
            return None
        res = res[0]
        for attr in result_object.__dict__.items():
            try:
                setattr(result_object, attr[0], res[attr[0]])
            except:
                ''
        # pprint(vars(result_object))

    def getDataPackageByName(self, name):
        data_package = {}
        package_description = self.getDataPackageDescription(name)
        if package_description is None:
            return data_package
        for propertie in package_description['Properties'].split(','):
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
                values = values + '\'' + str(data[prop]) + '\''
            else:
                columns = columns + ', `' + prop + '`'
                values = values + ', \'' + data[prop] + '\''

        query = 'INSERT INTO `' + table_name.lower() + '` (' + columns + ') VALUES (' + values + ');'
        cursor = self._dataBase.cursor(dictionary=True)
        cursor.execute(query)
        self._dataBase.commit()

    def getMinIdByDataType(self, data_type):
        query = 'SELECT MIN(Id) FROM ' + data_type.lower()
        cursor = self._dataBase.cursor(dictionary=True)
        cursor.execute(query)
        res = cursor.fetchall()
        if not res:
            return None
        return res[0]['MIN(Id)']

    def getDataPackage(self, data_type, where_statemante):
        query = 'SELECT * FROM ' + data_type.lower() + ' WHERE ' + where_statemante
        cursor = self._dataBase.cursor(dictionary=True)
        cursor.execute(query)
        res = cursor.fetchall()
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

        cursor = self._dataBase.cursor(dictionary=True)
        cursor.execute(query)
        res = cursor.fetchall()
        if not res:
            return None
        return res[0]

    def getDataObjectsByFieldValue(self, table_name, value_name, value):
        query = 'SELECT * FROM `' + table_name.lower() + '` WHERE ' + value_name + ' = \'' + value + '\''
        cursor = self._dataBase.cursor(dictionary=True)
        cursor.execute(query)
        res = cursor.fetchall()
        return res

    def saveNewSession(self, session):
        query = 'SELECT MAX(ID) FROM `sessions`'
        cursor = self._dataBase.cursor(dictionary=True)
        cursor.execute(query)
        res = cursor.fetchall()
        max_id = res[0]['MAX(ID)']
        if not max_id:
            max_id = 0
        now = datetime.now().strftime("%d/%b/%Y %H:%M:%S")
        query = 'INSERT INTO `sessions` (`ID`, `Token`, `Date`) VALUES (' + str(int(max_id) + 1) + ', \'' + session.token + '\', \'' + now + '\');'
        cursor = self._dataBase.cursor(dictionary=True)
        cursor.execute(query)
        self._dataBase.commit()
        return str(int(max_id) + 1)

    def saveNewTask(self, task):
        query = 'SELECT MAX(ID) FROM `tasks`'
        cursor = self._dataBase.cursor(dictionary=True)
        cursor.execute(query)
        res = cursor.fetchall()
        max_id = res[0]['MAX(ID)']
        if not max_id:
            max_id = 0
        now = datetime.now().strftime("%d/%b/%Y %H:%M:%S")
        query = 'INSERT INTO `tasks` (`ID`, `name`, `sessionTotalId`, `State`) VALUES (' + str(
            int(max_id) + 1) + ', \'' + task.name + '\', \'' + task.sessionTotalId + '\', \'' + task.state + '\');'
        cursor = self._dataBase.cursor(dictionary=True)
        cursor.execute(query)
        self._dataBase.commit()
        return str(int(max_id) + 1)

