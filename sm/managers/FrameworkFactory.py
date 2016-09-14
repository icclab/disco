from jdkframework import JDKFramework
from environmentframework import EnvironmentFramework
from clusterframework import ClusterFramework

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
        return framework
    # pass