from framework import Framework

class ZeppelinFramework(Framework):
    def __init__(self, deployClass, attributes):
        super(ZeppelinFramework,self).__init__(deployClass, attributes)
        self.dependencies = {"spark":{}}

    def get_bash(self):
        return self.deployClass.getFileContent("zeppelinbash.sh")

    def get_name(self):
        return "zeppelin"

    def get_dependencies(self):
        return self.dependencies
