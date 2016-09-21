from sm.log import LOG
from framework import Framework

class HadoopFramework(Framework):
    def __init__(self, deployClass, attributes):
        super(HadoopFramework,self).__init__(deployClass, attributes)
        self.dependencies = {"jdk": {},"cluster":{"master_name":{},"slave_count":{},"slave_name":{}}}
        self.variables = {"slaveonmaster": "True"}

    def get_bash(self):
        returnValue = self.deployClass.getFileContent("hadoopbash.sh")
        yarn_site_xml = self.deployClass.getFileContent("yarn-site.xml")
        core_site_xml = self.deployClass.getFileContent("core-site.xml")
        mapred_site_xml = self.deployClass.getFileContent("mapred-site.xml")
        hdfs_site_xml = self.deployClass.getFileContent("hdfs-site.xml")
        hadoop_env_sh = self.deployClass.getFileContent("hadoop-env.sh")

        replaceDict = {
            "$yarn-site.xml$": yarn_site_xml,
            "$core-site.xml$": core_site_xml,
            "$mapred-site.xml$": mapred_site_xml,
            "$hdfs-site.xml$": hdfs_site_xml,
            "$hadoop-env.sh$": hadoop_env_sh,
        }
        for key, value in replaceDict.iteritems():
            returnValue = returnValue.replace(key, value)
        returnValue = returnValue.replace( '$slavesfile$', self.get_slavesfile())
        masterreplacement = ''
        if self.variables["slaveonmaster"]:
            masterreplacement = self.dependencies['cluster']['master_name']+"\n"
        returnValue = returnValue.replace( '$masternodeasslave$',masterreplacement)
        returnValue = returnValue.replace( '$masternode$', self.dependencies['cluster']['master_name'])
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
        return "hadoop"

    def get_dependencies(self):
        return self.dependencies
