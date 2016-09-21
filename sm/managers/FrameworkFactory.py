from sm.log import LOG
from jdkframework import JDKFramework
from environmentframework import EnvironmentFramework
from clusterframework import ClusterFramework
from shellframework import ShellFramework
from hadoopframework import HadoopFramework
from sparkframework import SparkFramework
from zeppelinframework import ZeppelinFramework

class FrameworkFactory:
    @staticmethod
    def get_framework(frameworkName, deployClass, attributes ):
        framework = None
        if frameworkName=="jdk":
            LOG.debug("creating JDKFramework instance")
            framework = JDKFramework(deployClass, attributes)
        elif frameworkName=="environment":
            LOG.debug("creating EnvironmentFramework instance")
            framework = EnvironmentFramework(deployClass, attributes)
        elif frameworkName=="cluster":
            LOG.debug("creating ClusterFramework instance")
            framework = ClusterFramework(deployClass, attributes)
        elif frameworkName=="shell":
            LOG.debug("creating ShellFramework instance")
            framework = ShellFramework(deployClass, attributes)
        elif frameworkName=="hadoop":
            LOG.debug("creating HadoopFramework instance")
            framework = HadoopFramework(deployClass, attributes)
        elif frameworkName=="spark":
            LOG.debug("creating SparkFramework instance")
            framework = SparkFramework(deployClass, attributes)
        elif frameworkName=="zeppelin":
            LOG.debug("creating ZeppelinFramework instance")
            framework = ZeppelinFramework(deployClass, attributes)
        return framework
