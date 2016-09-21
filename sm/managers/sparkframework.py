from framework import Framework
from sm.log import LOG

class SparkFramework(Framework):
    def __init__(self, deployClass, attributes):
        super(SparkFramework,self).__init__(deployClass, attributes)
        self.dependencies = {"jdk":{},"hadoop":{},"cluster":{"master_name":{},"slave_count":{},"slave_name":{}}}
        self.variables = {"slaveonmaster": "True"}

    def get_bash(self):
        # for avoiding all escaping problems, the Spark shell script has been outsourced to its own file
        returnValue = self.deployClass.getFileContent("sparkbash.sh")
        returnValue = returnValue.replace( '$slavesfile$', self.get_slavesfile())
        masterreplacement = ''
        if self.variables["slaveonmaster"]:
            masterreplacement = self.dependencies['cluster']['master_name']+"\n"
        returnValue = returnValue.replace( '$masternodeasslave$',masterreplacement)
        # returnValue = returnValue.replace( '$masternode$', self.dependencies['cluster']['master_name'])
        return returnValue

    def get_slavesfile(self):
        slavesfile = ''
        try:
            slavecount = int(self.dependencies['cluster']['slave_count'])
            slavename = self.dependencies['cluster']['slave_name']
            slavesfile = ''
            for i in xrange(1, slavecount+1):
                slavesfile += slavename+str(i)+"\n"
        except:
            LOG.error("either slave count or slave name not in dependencies")
        return slavesfile

    def get_name(self):
        return "spark"

    def get_dependencies(self):
        return self.dependencies
