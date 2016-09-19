from framework import Framework

class ClusterFramework(Framework):
    def __init__(self, deployClass, attributes):
        super(ClusterFramework,self).__init__(deployClass, attributes)
        self.variables = {"master_name": "mymaster", "slave_name": "myslave", "slave_count": 1}

    def get_bash(self):
        return ''

    def get_name(self):
        return "cluster"

    def get_dependencies(self):
        return {}

    def set_variables(self, varDict):
        self.variables = varDict