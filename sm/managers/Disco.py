# Copyright (c) 2017. Zuercher Hochschule fuer Angewandte Wissenschaften
# All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
#
# Author: Balazs Meszaros

import os

from Component import Component
from Output import Output as FinalOutput


class Disco:
    # instance of Deployer class for deploying, retrieving and deleting clusters
    deployer = None

    # store for given parameters during construction phase
    params = None

    def __init__(self, disco_config, params):
        """
        creating a Disco class instance which will provide the regular interface to access the cluster lifecycle
        :param disco_config: data needed for Disco class
        :param params: possible further parameters (not used currently)
        """
        self.deployer = disco_config['deployer']
        self.framework_directory = disco_config['framework_directory']
        self.root_component = disco_config['root_component']
        self.root_component_state = disco_config['root_component_state']
        self.params = params
        self.components = {}
        self.output = FinalOutput()
        self.load_components()

    def get_component_names(self):
        """
        read names of available components
        :return: available component names as array
        """
        datadir = os.path.join(self.framework_directory)
        print( os.path.dirname(os.path.realpath(__file__)))
        return [name for name in os.listdir(datadir)
                if os.path.isdir(os.path.join(datadir, name))]

    def deploy(self):
        """
        A new stack will be deployed here.
        :return: return value of the deployer's deploy() function
        """
        self.deploy_string = self.generate_output()

        self.stackInfo = self.deployer.deploy(self.deploy_string)

        return self.stackInfo

    def load_components(self):
        """
        each component will be instantiated and saved within the Disco instance
        """
        component_names = self.get_component_names()
        for component in component_names:
            self.components[component] = Component(os.path.join(self.framework_directory,component), self.output)

    def inject_requested_properties(self, properties):
        """
        properties given by the end user over HTTP or default properties inserted by the framework
        properties are of type {'componentname': {'componentproperty': 'value', ... }, ...}
        :param properties: properties as dictionary of dictionary of values
        """
        for component, props in properties.iteritems():
            if component in self.components:
                self.components[component].set_requested_properties(props)

    def retrieve(self, parameter):
        """
        forward the retrieve request to the deployer instance
        :param parameter: parameter to retrieve the requested entity (probably a cluster)
        :return: return value of the deployer instance
        """
        return self.deployer.retrieve(parameter)

    def delete(self, parameter):
        """
        forward the delete request to the deployer instance
        :param parameter: parameter to delete the requested entity (probably a cluster)
        :return: return value of the deployer instance
        """
        return self.deployer.delete(parameter)

    def inject_dependency(self, component_name, dependencies):
        '''
        dependencies as {'dependency1': {'state1': {'value1': 'possible value','value2': None},
                                        ...},
                          'dependency2': {}
                          }
        :param component_name: string of the componen


        t's name to be injected into
        :param dependencies: which dependencies (formatting see above)
        :return:
        '''
        if component_name in self.components:
            self.components[component_name].add_dependencies(dependencies)

    def dep_resolve(self, component, resolved, unresolved):
        """
        recursive dependency resolving algorithm based on 2 lists, one with the already resolved dependencies and one with the dependencies to be resolved
        each component is described as a dictionary:
            { "name": <name of the component>,
              "component": <the actual component's instance>,
              "state": <the needed state of the requested component> }
        :param component: name of the component that needs all dependencies
        :param resolved: already resolved components in a list
        :param unresolved: currently unresolved components in a list
        """

        # the component to be resolved is obviously unresolved yet and needs to
        # be added to the unresolved list
        unresolved.append(component)

        # get each dependency of the new component which has to be resolved
        for comp, deps in component['component'].get_dependencies(component['state']).iteritems(): # {depname: {state: {dep1, dep2, ...},...},...}
            # e.g. comp='shell', deps={'start': {}}

            # each state of the depending components have to be handled
            for state, dep in deps.iteritems():
                # e.g. state='start', dep={}

                # check whether a component with name saved in comp exists
                if not comp in self.components:
                    raise Exception('No component %s registered' % (comp))

                # check whether current dependent component with requested
                # state is resolved already
                if not self.list_contains_comp(resolved, {'name': self.components[comp].get_name(), 'component': self.components[comp], 'state': state}):

                    # if the found dependent component is not just in the
                    # resolved list but also in the unresolved list, something
                    # is wrong: then, a circular dependency is present
                    if self.list_contains_comp(unresolved, {'name': self.components[comp].get_name(), 'component': self.components[comp], 'state': state}):
                        raise Exception('Circular reference detected: %s:%s -> %s:%s' % (component['component'].get_name(), component['state'], comp, state))

                    # if the dependent component is not within the locally
                    # instantiated components, then there is something wrong as
                    # well
                    if not comp in self.components:
                        raise Exception('No component %s registered' % (comp))

                    # else, a new component dictionary can be "created" for the
                    # next recursive call of dep_resolve
                    new_comp = self.components[comp]
                    component_to_resolve = {'name': new_comp.get_name(), 'component': new_comp, 'state': state}
                    self.dep_resolve(component_to_resolve, resolved, unresolved)
                elif len(deps) is not 0:
                    # here, the new requirements have to be inserted into existing framework instance
                    # if no new attributes are to be inserted, no call necessary as the framework will be installed anyway
                    #TODO: comment this in and write method
                    # self.add_attributes_to_comp(deps, comp, resolved)
                    pass

        # finally, the component has been found and can be switched from the
        # unresolved list to the resolved list
        resolved.append(component)
        unresolved.remove(component)


    def list_contains_comp(self, compList, compName):
        """
        list_contains_comp checks whether a component is within a given list
        this is a slightly more complicated call because the component also has
        a state
        :param compList: haystack; list containing the components, can be the resolved or unresolved list
        :param compName: dictionary of needle
        :return: True if component is within list, else False
        """
        for fw in iter(compList):
            if fw['component'].get_name()==compName['component'].get_name() and fw['state']==compName['state']:
                return True
        return False

    def resolve_dependencies(self):
        """
        initialise the component resolving (i.e. dependency handling) of the
        components
        """
        self.resolved_dependencies = []
        self.dep_resolve(
            {
                'name': self.components[self.root_component].get_name(),
                'component': self.components[self.root_component],
                'state':self.root_component_state
            },
            self.resolved_dependencies,
            [])

    def generate_output(self):
        '''
        generate the entire output within the Output (FinalOutput) class
        :return:
        '''
        for current_component in self.resolved_dependencies:
            current_component['component'].set_property('state', current_component['state'])
            current_component['component'].handle_output()
        return self.output.get_output()
