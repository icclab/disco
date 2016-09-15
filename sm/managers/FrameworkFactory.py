from jdkframework import JDKFramework
from environmentframework import EnvironmentFramework
from clusterframework import ClusterFramework
from shellframework import ShellFramework
from hadoopframework import HadoopFramework
from sparkframework import SparkFramework

class FrameworkFactory:
    @staticmethod
    def get_framework(frameworkName, deployClass, attributes ):
        framework = None
        if frameworkName=="jdk":
            framework = JDKFramework(deployClass, attributes)
        elif frameworkName=="environment":
            framework = EnvironmentFramework(deployClass, attributes)
        elif frameworkName=="cluster":
            framework = ClusterFramework(deployClass, attributes)
        elif frameworkName=="shell":
            framework = ShellFramework(deployClass, attributes)
        elif frameworkName=="hadoop":
            framework = HadoopFramework(deployClass, attributes)
        elif frameworkName=="spark":
            framework = SparkFramework(deployClass, attributes)
        return framework
