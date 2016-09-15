from framework import Framework

class JDKFramework(Framework):
    def __init__(self, deployClass, attributes):
        super(JDKFramework,self).__init__(deployClass, attributes)
        self.variables = {"java_home":"/usr/lib/java/jdk"}

    def get_bash(self):
        returnValue = self.deployClass.getFileContent("jdkbash.sh")
        return returnValue

    def get_name(self):
        return "jdk"

    def get_dependencies(self):
        self.dependencies = {"environment": {"parallel_scp":None,"parallel_ssh":None,"hosts_lst":None,"setstate":None,"deployment_log":None}}
        return self.dependencies

