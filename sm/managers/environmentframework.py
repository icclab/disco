from framework import Framework

class EnvironmentFramework(Framework):
    def __init__(self, deployClass, attributes):
        super(EnvironmentFramework,self).__init__(deployClass, attributes)

    def get_bash(self):
        return ''

    def get_name(self):
        return "environment"

    def get_dependencies(self):
        return {"cluster": {"username","master_user_dir","slave_user_dir"}}

