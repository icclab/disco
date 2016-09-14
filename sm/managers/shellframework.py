from framework import Framework

class ShellFramework(Framework):
    def __init__(self, deployClass, attributes):
        super(ShellFramework,self).__init__(deployClass, attributes)
        self.dependencies = {}

    def get_bash(self):
        return ''

    def get_name(self):
        return "shell"

    def set_dependencies(self, dependencies):
        self.dependencies = dependencies

    def get_dependencies(self):
        return self.dependencies

