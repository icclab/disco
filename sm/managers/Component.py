import os
from lxml import etree
from xml.etree.ElementTree import ParseError as ParseError
# inspect is needed to determine the functions in dynamically included Python files
import inspect
# import sm.log as log
import logging
import sys
dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append("%s/data" %dir_path)
# sys.path.append("/home/ubuntu/DISCO/sm/managers/data")
from sm.managers.data.DiscoConfiguration import DiscoConfiguration

class FileResolver(etree.Resolver):
    '''
    thisclass is needed by the lxml parser
    '''
    def resolve(self, url, pubid, context):
        return self.resolve_filename(url, context)

class XMLNotConformingException(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)

class Component():
    '''
    Component is an element which can be installed within the created template.
    '''
    def __init__(self, fwpath, output):
        '''
        each component needs to connect to the "outer" world, i.e. it needs to know which framework/part it should install and where to put the output to
        :param fwpath: name of the framework to be installed
        :param output: handle to the instance of the Output class
        :return: None
        '''
        self.logger = logging.getLogger(__name__)
        self.path = fwpath
        self.output = output
        self.fwname = self.path[self.path.rindex("/")+1:]
        xmlfilename = os.path.join(self.path, self.fwname+".xml")
        if os.path.isfile(xmlfilename):
            xmlfilehandle = open(xmlfilename, "r")
            self.xmlfile = xmlfilehandle.read()
            xmlfilehandle.close()
            try:
                self.xml = etree.XML(self.xmlfile)
            except ParseError as e:
                self.logger.error(str(e.message))
                pass
            self.register_functions()
        else:
            raise XMLNotConformingException('there is no XML file '+xmlfilename+' for component '+self.fwname)

    def set_requested_properties(self, properties):
        '''
        set the requested properties to the values given in a dictionary; usually, the end user will issue a request with desired variables
        :param properties: dictionary with properties
        :return: self
        '''
        for property, value in properties.iteritems():
            self.set_property(property, value)
        return self

    def set_property(self, property_name, property_value):
        '''
        set a new value to an already existing property
        :param property_name: name of the property
        :param property_value: value it should be assigned
        :return: self
        '''
        self.output.add_property({self.fwname: {property_name: property_value}})

        property = self.xml.xpath("/discocomponent/properties/property[@name='"+property_name+"']")
        if len(property)>0:
            property[0].attrib['value'] = property_value
        else:
            new_property = etree.Element("property")
            new_property.attrib['name'] = property_name
            new_property.attrib['value'] = property_value
            self.xml.xpath("/discocomponent/properties")[0].insert(0,new_property)
        return self

    def get_property_value(self, property_name):
        '''
        access the value of an existing property
        :param property_name: name of the requested property
        :return: value of the property or None if not existing
        '''
        try:
            property = self.xml.xpath("/discocomponent/properties/property[@name='"+property_name+"']")[0]
            return property.attrib['value']
        except:
            return None

    def get_all_properties(self):
        '''
        access every existing property as a dictionary
        :return: dictionary with each property and its value
        '''
        properties = self.xml.xpath("/discocomponent/properties/property")
        property_dictionary = {}
        for property in properties:
            try:
                property_dictionary[property.attrib['name']] = property.attrib['value']
            except:
                #this happens if a property with no attribute value is found
                pass
        return property_dictionary

    def set_dependency_values(self):
        '''
        load values of each dependency into local dictionary and XML structure
        :return: self
        '''
        # current_state = ""
        # try:
        #     self.xml.xpath("/discocomponent/properties/property[@name='state']")[0].attrib['value']
        # except:
        #     pass
        deps = self.xml.xpath("/discocomponent/dependencies/*")
        for component in deps:
            current_variables = component.xpath("variable")
            for property in current_variables:
                value = self.output.get_value_for_component(component.attrib['name'], property.attrib['name'])
                self.set_dependency_value(component.attrib['name'], property.attrib['name'], value)
        return self

    def set_dependency_value(self, component_name, dependency_name, dependency_value):
        '''
        set the value of a particular dependency
        :param component_name: name of the dependant component
        :param dependency_name: name of the dependency within the component
        :param dependency_value: value of the dependency
        :return: self on success, False in case of error
        '''
        try:
            #TODO: the state has to be introduced here
            dependencies = self.xml.xpath("/discocomponent/dependencies/dependency[@name='"+component_name+"']/variable[@name='"+dependency_name+"']")
            for dependency in dependencies:
                dependency.text = dependency_value
            return self
        except:
            # this can only happen for an injected dependency
            return False

    def get_dependencies(self, state):
        '''
        compile all dependencies including their values into a dictionary and return it:
            {'dependencyname':
                {'state':
                    { 'variable': 'value', ... },
                ...},
            ...}
        :return: dependencies including their values or None (if exception occurred)
        '''
        dependencies = {}
        try:
            # for dep in self.xml.xpath("/discocomponent/dependencies[]/dependency"):
            #     dependencies[dep.attrib['name']] = {dep.attrib['state']: {}}
            #     for var in dep.xpath("variable"):
            #         dependencies[dep.attrib['name']][dep.attrib['state']][var.attrib['name']] = var.text
            for dep in self.xml.xpath("/discocomponent/dependencies[not(@state) or @state='%s']/dependency" % state):
                #todo: thisl
                if 'state' not in dep.attrib:
                    dep.attrib['state'] = 'default'
                dependencies[dep.attrib['name']] = {dep.attrib['state']: {}}
                for var in dep.xpath("variable"):
                    dependencies[dep.attrib['name']][dep.attrib['state']][var.attrib['name']] = var.text
        except:
            return None
        return dependencies

    def add_dependencies(self, new_dependencies):
        '''
        add a tree of dependencies defined in the given dictionary
        parameter is of the type {'state1': {'dependency1': {'dep1state1': {'value1': 'possible value','value2': None}, ...},
                                                ... },
                                  'state2': {}
                                  }
        if state is set to string(default), it means that no state will be set
        :param new_dependencies: dictionary of dependencies
        :return: self
        '''
        for comp_state, dependencies in new_dependencies.iteritems():
            dependencies_element = None
            if comp_state=="default":
                if len(self.xml.xpath("/discocomponent/dependencies[not(@state)]"))==0:
                    new_dep_element = etree.Element("dependencies")
                    dependencies_element = new_dep_element
                    self.xml.xpath("/discocomponent")[0].insert(0, new_dep_element)
                else:
                    dependencies_element = self.xml.xpath("/discocomponent/dependencies[not(@state)]")[0]
            elif len(self.xml.xpath("/discocomponent/dependencies[@state='"+comp_state+"']"))==0:
                new_dep_element = etree.Element("dependencies")
                new_dep_element.attrib['state'] = comp_state
                dependencies_element = new_dep_element
                self.xml.xpath("/discocomponent")[0].insert(0, new_dep_element)
            else:
                dependencies_element = self.xml.xpath("/discocomponent/dependencies[@state='"+comp_state+"']")[0]

            for dep, dep_states in dependencies.iteritems():
                for dep_state, dep_values in dep_states.iteritems():
                    new_dependency_element = None
                    if dep_state=='default':
                        if len(dependencies_element.xpath("dependency[@name='"+dep+"'][not(@state)]"))==0:
                            new_dependency_element = etree.Element("dependency")
                            new_dependency_element.attrib['name'] = dep
                            dependencies_element.insert(0, new_dependency_element)
                        else:
                            new_dependency_element = dependencies_element.xpath("dependency[@name='"+dep+"'][not(@state)]")
                    elif len(dependencies_element.xpath("dependency[@name='"+dep+"'][@state='"+dep_state+"']"))==0:
                        new_dependency_element = etree.Element("dependency")
                        new_dependency_element.attrib['name'] = dep
                        new_dependency_element.attrib['state'] = dep_state
                        dependencies_element.insert(0, new_dependency_element)
                    else:
                        new_dependency_element = dependencies_element.xpath("dependency[@name='"+dep+"'][@state='"+dep_state+"']")

            # here, new dependency has been added up to the state level
            #TODO: if variables are to be added, this would come here

        #
        # for dep_name,dep_val in new_dependencies.iteritems():
        #     for state, dependency_value in dep_val.iteritems():
        #         dependency = None
        #         if state is not 'default':
        #             dependency = self.xml.xpath("/discocomponent/dependencies/dependency[@name='"+dep_name+"'][@state='"+state+"']")
        #         else:
        #             dependency = self.xml.xpath("/discocomponent/dependencies/dependency[@name='"+dep_name+"'][not(@state)]")
        #         if 0 is len(dependency):
        #             self.add_dependency(dep_name, state, dep_val)
        return self

    def add_dependency(self, dep_name, dep_state, dep_val):
        """
        add a new dependency to the component; this is how dependency injection is handled, mainly for the shell script
        value is something of the type {'value1': 'possible value','value2': None}
        :param: dep_name as a string - new dependency's name
        :param: dep_val as a dictionary - required values from that dependency
        :return: self
        """
        #TODO: handle the case that the dependency is already present!!!
        dependency_to_extend = None
        if dep_state is not 'default':
            dependency_to_extend = self.xml.xpath("/discocomponent/dependencies/dependency[@name='"+dep_name+"'][@state='"+dep_state+"']")
        else:
            dependency_to_extend = self.xml.xpath("/discocomponent/dependencies/dependency[@name='"+dep_name+"'][not(@state)]")
        element = None
        if len(dependency_to_extend)==0:
            element = etree.Element('dependency')
            element.attrib['name'] = dep_name
            self.xml.xpath("/discocomponent/dependencies")[0].insert(0,element)
        else:
            element = dependency_to_extend[0]
        for prop_name,prop_val in dep_val.iteritems():
            sub = etree.Element('variable')
            sub.attrib['name'] = prop_name
            sub.text = prop_val
            element.insert(0,sub)
        return self

    def get_files(self):
        '''
        get each file with Python code from the XML as a list
        :return: list with each filename
        '''
        files = self.xml.xpath("/discocomponent/functions/file")
        paths = []
        for file in files:
            file_path = file.attrib['path']
            paths.insert(0,file_path)
        return paths

    def register_functions(self):
        '''
        register Python functions within lxml so that they can be referenced within the XSLT code
        :return: self
        '''
        python_files = self.get_files()
        # each registered file has to be evaluated
        for cur_file in python_files:
            path = ""
            try:

                path = "%s/%s" % (DiscoConfiguration.component_directory, self.fwname)
                # only add path if not present yet - possible if multiple
                # source files for the same component are iterated
                if path not in sys.path:
                    sys.path.append(path)
                module_name = cur_file[0:-3]
                cur_mod = __import__(module_name)
                new_functions = inspect.getmembers(cur_mod, inspect.isfunction)
                ns = etree.FunctionNamespace(self.fwname+".xsl")
                ns.prefix = self.fwname
                for cur_function in new_functions:
                    name = str(cur_function[0])
                    ns[name] = cur_function[1]
            except Exception as e:
                print(e.message)
                print("in path "+path)
                pass
        return self

    def update_dependency_dictionary(self):
        properties = self.get_all_properties()
        self.output.add_property({self.get_name():properties})
        pass

    def get_output(self):
        self.set_dependency_values()

        global_output = self.xml.xpath("/discocomponent/globaloutput")

        if len(global_output) is 0:
            # if no /discocomponent/globaloutput has been provided, create it before filling
            element = etree.Element("globaloutput")
            element.text = self.output.get_output()
            self.xml.xpath("/discocomponent")[0].insert(0,element)
        else:
            global_output[0].text = self.output.get_output()

        static_output = self.get_property_value('staticoutput')
        if static_output is not None:
            if static_output.lower()=='true':
                cur_output = self.xml.xpath("/discocomponent/output/text()")
                self.update_dependency_dictionary()
                try:
                    return ''.join(str(elem) for elem in cur_output)
                except:
                    return cur_output
            else:
                self.xml = self.create_xslt_output()
                strings = self.xml.xpath("/discocomponent/output/text()")
                self.update_dependency_dictionary()
                return ''.join(str(elem) for elem in strings) #resultstring


        raise XMLNotConformingException('there is no property staticoutput set in the XML file of'+self.fwname)

    def handle_output(self):
        '''
        this is a proxy function
        :return:
        '''
        # the output has to be fetched at the beginning because the output type might get changed by XSLT within get_output()
        output_string = self.get_output()
        if self.get_output_type()=='append':
            self.output.append_output(output_string)
        else:
            self.output.set_output(output_string)
        return self

    def get_name(self):
        return self.fwname

    def create_xslt_output(self):
        '''

        :return: the newly generated XML document by XSLT
        '''
        parser = etree.XMLParser()
        self.add = parser.resolvers.add(FileResolver())

        xslt_file_handle = open(os.path.join(self.path,self.fwname+".xsl"))
        xslt_file_content = xslt_file_handle.read()
        xslt_file_handle.close()
        xslt_tree = ''
        try:
            xslt_tree = etree.XML(xslt_file_content)
        except ParseError as e:
            self.logger.error(e.message)
            pass
        transform = etree.XSLT(xslt_tree)

        oldstring = etree.tostring(self.xml, pretty_print=True)
        # print(etree.tostring(self.xml))
        # print("xslt: "+etree.tostring(xslt_tree))
        result = transform(self.xml)
        newstring = etree.tostring(result, pretty_print=True)
        result_string = etree.tostring(result)
        result_strings = result.xpath("/discocomponent/output/text()")
        return result #''.join(str(elem) for elem in result_strings)

    def get_output_type(self):
        '''
        value of property "outputtype" which defines whether to append the output to the existing output or to replace the current output entirely
        :return: {'replace','append'}
        '''
        try:
            output_type = self.xml.xpath("/discocomponent/properties/property[@name='outputtype']")[0]
            return output_type.attrib['value']
        except:
            return "append"

