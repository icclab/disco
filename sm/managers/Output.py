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

class Output():
    '''
    Output handles all the output aggregation and variable forwarding amongst components
    '''
    def __init__(self):
        self.final_output = ""
        self.property_dict = {}

    def append_output(self, new_output):
        '''
        append a string to the current output
        :param new_output: string to be added to the output
        :return: the entire output
        '''
        if isinstance(new_output, basestring):
            self.final_output = self.final_output + new_output
        return self.get_output()

    def get_output(self):
        '''
        get the current output
        :return: output up to this point
        '''
        return self.final_output

    def set_output(self, new_output):
        '''
        set the entire output to a new value. keep in mind: with great power comes great responsibility!
        :param new_output: the entire new output
        :return: the new output
        '''
        if isinstance(new_output, basestring):
            self.final_output = new_output
        else:
            self.final_output = ""
        return self.final_output

    def add_property(self, property):
        '''
        add a new property to the list - these are the dependencies that components depend on; the local dictionary will be updated. Only the own properties should be updated!
        :param property: dictionary with properties; always of the form
                { 'componentname': {
                    'property1': 'value',
                    'property2': 'value',
                    ...
                    }
                }
        :return: self
        '''
        for component, value in property.iteritems():
            if component not in self.property_dict:
                self.property_dict[component] = value
            else:
                self.property_dict[component].update(value)
        return self

    def get_properties(self):
        '''
        access all saved properties
        :return: list of properties as a dictionary
        '''
        return self.property_dict

    def get_value_for_component(self, component_name, property_name):
        '''
        get a specific property's value
        :param component_name: name of the providing component
        :param property_name: name of the requested property
        :return: the actual property if existing, else None
        '''
        try:
            return self.property_dict[component_name][property_name]
        except:
            return None
