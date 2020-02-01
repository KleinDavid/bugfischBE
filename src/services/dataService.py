import mysql.connector
from mysql.connector import Error
from services.loggingService import LoggingService


class DataService:

    _dataBase = None
    __instance = None

    @staticmethod
    def getInstance():
        if DataService.__instance is None:
            DataService()
        return DataService.__instance

    def __init__(self):
        if DataService.__instance is not None:
            raise Exception("This class is a singleton!")
        else:
            DataService.__instance = self

        try:
            connection = mysql.connector.connect(
                host="localhost",
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
            print("Error while connecting to MySQL", e)

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
        print('SELECT * FROM `serveractions` WHERE Opening = \'1\'')
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
        properties = self.getDataPackageDescription(table_name)['Properties'].split(',')
        columns = ''
        values = ''
        for prop in properties:
            if len(columns) == 0:
                columns = columns + '`' + prop + '`'
                values = values + '\'' + data[prop] + '\''
            else:
                columns = columns + ', `' + prop + '`'
                values = values + ', \'' + data[prop] + '\''

        query = 'INSERT INTO `' + table_name.lower() + '` (' + columns + ') VALUES (' + values + ');'
        cursor = self._dataBase.cursor(dictionary=True)
        cursor.execute(query)
        self._dataBase.commit()

    def getDataPackage(self, data_type, where_statemante):
        query = 'SELECT * FROM `' + data_type.lower() + '` WHERE ' + where_statemante
        cursor = self._dataBase.cursor(dictionary=True)
        cursor.execute(query)
        res = cursor.fetchall()
        if not res:
            return None

        # **get Reference
        for ref in self.getReferences(data_type):
            for value in res:
                child_id = str(value[ref['parentField']])
                if child_id != '':
                    child = self.getDataObjectById(ref['childTable'], child_id)
                    value[ref['parentField']] = child
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
        print(query)
        cursor = self._dataBase.cursor(dictionary=True)
        cursor.execute(query)
        res = cursor.fetchall()
        return res[0]