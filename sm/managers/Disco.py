import os

from Component import Component
from Output import Output as FinalOutput


class Disco:
    deployer = None
    params = None

    def __init__(self, disco_config, params):
        self.deployer = disco_config['deployer']
        self.framework_directory = disco_config['framework_directory']
        self.root_component = disco_config['root_component']
        self.root_component_state = disco_config['root_component_state']
        self.params = params
        self.components = {}
        self.output = FinalOutput()
        self.load_components()

    def get_component_names(self):
        datadir = os.path.join(self.framework_directory)
        print( os.path.dirname(os.path.realpath(__file__)))
        return [name for name in os.listdir(datadir)
                if os.path.isdir(os.path.join(datadir, name))]

    def deploy(self):
        """A new stack should be deployed here.
        """
        # self.resolved = []
        # self.dep_resolve(self.components[self.root_component],self.resolved,[])

        self.deploy_string = self.generate_output()

        self.stackInfo = self.deployer.deploy(self.deploy_string)

        return self.stackInfo

    def load_components(self):
        component_names = self.get_component_names()
        for component in component_names:
            self.components[component] = Component(os.path.join(self.framework_directory,component), self.output)

    def inject_requested_properties(self, properties):
        for component, props in properties.iteritems():
            if component in self.components:
                self.components[component].set_requested_properties(props)

    def retrieve(self, parameter, output_names):
        return self.deployer.retrieve(parameter, output_names)

    def delete(self, parameter):
        return self.deployer.delete(parameter)

    def inject_dependency(self, component_name, dependencies):
        '''
        dependencies as {'dependency1': {'state1': {'value1': 'possible value','value2': None},
                                        ...},
                          'dependency2': {}
                          }
        :param component_name: string of the component's name to be injected into
        :param dependencies: which dependencies (formatting see above)
        :return:
        '''
        if component_name in self.components:
            self.components[component_name].add_dependencies(dependencies)

    def dep_resolve(self, component, resolved, unresolved):
        unresolved.append(component)
        for comp, deps in component['component'].get_dependencies(component['state']).iteritems(): # {depname: {state: {dep1, dep2, ...},...},...}
            # e.g. comp='shell', deps={'start': {}}
            for state, dep in deps.iteritems():
                # e.g. state='start', dep={}
                if not self.list_contains_comp(resolved, {'name': self.components[comp].get_name(), 'component': self.components[comp], 'state': state}):
                    if self.list_contains_comp(unresolved, {'name': self.components[comp].get_name(), 'component': self.components[comp], 'state': state}):
                        raise Exception('Circular reference detected: %s:%s -> %s:%s' % (component['component'].get_name(), component['state'], comp, state))

                    if not comp in self.components:
                        raise Exception('No component %s registered' % (comp))
                    new_comp = self.components[comp]

                    component_to_resolve = {'name': new_comp.get_name(), 'component': new_comp, 'state': state}
                    self.dep_resolve(component_to_resolve, resolved, unresolved)
                elif len(deps) is not 0:
                    # here, the new requirements have to be inserted into existing framework instance
                    # if no new attributes are to be inserted, no call necessary as the framework will be installed anyway
                    #TODO: comment this in and write method
                    # self.add_attributes_to_comp(deps, comp, resolved)
                    pass
        resolved.append(component)
        unresolved.remove(component)


    def list_contains_comp(self, compList, compName):
        for fw in iter(compList):
            if fw['component'].get_name()==compName['component'].get_name() and fw['state']==compName['state']:
                return True
        return False

    def resolve_dependencies(self):
        self.resolved_dependencies = []
        self.dep_resolve({'name': self.components[self.root_component].get_name(), 'component': self.components[self.root_component], 'state':self.root_component_state}, self.resolved_dependencies, [])

    def generate_output(self):
        '''
        generate the entire output within the Output (FinalOutput) class
        :return:
        '''
        for current_component in self.resolved_dependencies:
            current_component['component'].set_property('state', current_component['state'])
            current_component['component'].handle_output()
        return self.output.get_output()