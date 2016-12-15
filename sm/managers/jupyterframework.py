from framework import Framework

class JupyterFramework(Framework):
    def __init__(self, deployClass, attributes):
        super(JupyterFramework,self).__init__(deployClass, attributes)
        self.dependencies = {"cluster": {"master_name": {}}}

    def get_bash(self):
        jupyter_notebook_config_py = self.deployClass.getFileContent("jupyter_notebook_config.py")
        returnValue = self.deployClass.getFileContent("jupyterbash.sh")
        returnValue = returnValue.replace("$jupyter_notebook_config.py$", jupyter_notebook_config_py)

        return returnValue

    def get_name(self):
        return "jupyter"

    def get_dependencies(self):
        return self.dependencies
