class ServerAction:

    def __init__(self):
        self.Name = ''
        self.Type = ''
        self.Input = {}
        self.Token = ''
        self.Id = ''
        self.Execute = ''
        self.ComponentId = ''
        self.InClient = False
        self.InputValues = []
        self.NextActions = []

        # {name, binding}
        self.Bindings = []

    def setBindings(self, data):
        for binding in self.Bindings:
            value = data
            for key in binding['binding'].split('.'):
                value = value[key]
            self.Input[binding['name']] = value
