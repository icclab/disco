from framework import Framework

class ClusterFramework(Framework):
    def __init__(self, deployClass, attributes):
        super(ClusterFramework,self).__init__(deployClass, attributes)

    def get_bash(self):
        return ''

    def get_name(self):
        return "cluster"

    def get_dependencies(self):
        return {}

