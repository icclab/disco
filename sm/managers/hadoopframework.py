from framework import Framework

class HadoopFramework(Framework):
    def __init__(self, deployClass, attributes):
        super(HadoopFramework,self).__init__(deployClass, attributes)
        self.dependencies = {}

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

        return returnValue

    def get_name(self):
        return "hadoop"

    def get_dependencies(self):
        self.dependencies = {"jdk": {}}
        return self.dependencies
