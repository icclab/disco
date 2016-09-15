class Framework(object):
    def __init__(self, deployClass, attributes):
        self.dependencies = {}
        self.deployClass = deployClass
        self.attributes = attributes # of type {"attribname": "optionalvalue",...}
        self.variables = {}

    # return the dependencies; this is a dictionary with key framework names containing dictionaries with the variable names of the respective frameworks as values
    def get_dependencies(self):
        return self.dependencies

    # with this method, a certain framework's dependency's values will be filled
    def set_dependency_value(self, dependency_value):
        self.dependencies.update(dependency_value)

    #TODO: currently, new item is only inserted if it doesn't exist in the attributes list yet. A problem will arise as soon as the element exists already, but with a different value! This problem is not solved yet in the specification!!!
    def add_required_attributes(self, new_attribute_dict):
        for attr, val in new_attribute_dict.iteritems():
            if attr not in self.attributes.keys():
                self.attributes.update({attr: val})



    # variables is a dictionary which only contains the variable names without the framework name; this method should only be used from within the framework
    def set_variable(self, variable_dict):
        self.variables.update(variable_dict)

    # the return value includes the framework name as it is always called from other frameworks for filling their own dependency list
    def get_variables(self):
        return {self.get_name(): self.variables }

    def get_name(self):
        pass
