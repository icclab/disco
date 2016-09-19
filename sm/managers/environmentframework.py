from framework import Framework

class EnvironmentFramework(Framework):
    def __init__(self, deployClass, attributes):
        super(EnvironmentFramework,self).__init__(deployClass, attributes)
        self.dependencies = {"cluster": {"username": None,"master_user_dir": None,"slave_user_dir": None}}

    def get_bash(self):
        return ''

    def get_name(self):
        return "environment"

    def get_dependencies(self):
        return self.dependencies
