from framework import Framework

class SparkFramework(Framework):
    def __init__(self, deployClass, attributes):
        super(SparkFramework,self).__init__(deployClass, attributes)

    def get_bash(self):
        # for avoiding all escaping problems, the Spark shell script has been outsourced to its own file
        return self.deployClass.getFileContent("sparkbash.sh")

    def get_name(self):
        return "spark"

    def get_dependencies(self):
        return {"jdk":{},"hadoop":{}}

