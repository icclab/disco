from framework import Framework

class ZeppelinFramework(Framework):
    def __init__(self, deployClass, attributes):
        super(ZeppelinFramework,self).__init__(deployClass, attributes)
        self.dependencies = {"spark":{}}

    def get_bash(self):
        zeppelin_env_sh = self.deployClass.getFileContent("zeppelin-env.sh")

        returnValue = self.deployClass.getFileContent("zeppelinbash.sh")
        returnValue = returnValue.replace("$zeppelin_env_sh$", zeppelin_env_sh)

        return returnValue

    def get_name(self):
        return "zeppelin"

    def get_dependencies(self):
        return self.dependencies
