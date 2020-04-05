from objects.task import Task
from services.dataService import DataService


class TaskService:
    __dataService__ = DataService.getInstance()
    __instance = None

    @staticmethod
    def getInstance():
        if TaskService.__instance is None:
            TaskService()
        return TaskService.__instance

    def __init__(self):
        if TaskService.__instance is not None:
            raise Exception("This class is a singleton!")
        else:
            TaskService.__instance = self

        self.currentTasks = []

    def getCurrentTasksBySessionTotalId(self, session_total_id):
        obj = {}
        for i in list(filter(lambda x: x.sessionTotalId == session_total_id, self.currentTasks)):
            props = {}
            for attr, value in i.__dict__.items():
                props[attr] = value
            obj[i.name] = props
        return obj

    def createNewTask(self, task_name, session_total_id):
        task = Task()
        task.name = task_name
        task.state = 'working'
        task.sessionTotalId = session_total_id
        task.id = self.__dataService__.saveNewTask(task)
        self.currentTasks.append(task)
