from framework import Framework

class HadoopFramework(Framework):
    def __init__(self, deployClass, attributes):
        super(HadoopFramework,self).__init__(deployClass, attributes)
        self.dependencies = {}

    def get_bash(self):
        return self.deployClass.getFileContent("hadoopbash.sh")

    def get_name(self):
        return "hadoop"

    def get_dependencies(self):
        self.dependencies = {"jdk": {}}
        return self.dependencies
