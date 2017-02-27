import os
import unittest
from lxml import etree
import sys
sys.path.append("..")
from Disco import Disco


class TestDisco(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(TestDisco, self).__init__(*args, **kwargs)
        self.discoinst = Disco(None, None)
        os.chdir("/Users/puenktli/Documents/Coding/DISCO")
        self.discoinst.load_components()


    # def test_deploy(self):
    #     discoinst = Disco(None,None)
    #     os.chdir("..")
    #     self.assertEquals(discoinst.get_component_names(),['heat','hadoop'],"network names are correct")

    # def test_load_components(self):
    #     discoinst = Disco(None, None)
    #     os.chdir("..")
    #     discoinst.load_components()


    def test_inject_properties(self):
        # self.create_disco_instance()
        self.test_dependency_resolving()
        self.properties = {'heat': { 'prop1': 'value', 'prop2': 'value 2'},
                      'hadoop': { 'staticoutput': 'false'},
                      'notexistingframework': { 'fakeproperty': 'fakevalue'}
                      }
        # first, the HTTP parameters have to be injected into each component
        # second, the dependency tree has to be constructed
        # third, in a loop, the output of each component is generated after
        # inserting each dependency first
        self.discoinst.inject_requested_properties(self.properties)
        self.assertIsInstance(self.discoinst,Disco)
        output = self.discoinst.generate_output()
        print(output)
        None

    def test_dependency_resolving(self):
        # self.create_disco_instance()
        self.resolved = []
        self.discoinst.dep_resolve(self.discoinst.components['shell'],self.resolved,[])
        None

if __name__ == '__main__':
    unittest.main()
