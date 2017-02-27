import unittest
import sys
sys.path.append("..")
from Component import Component
from Output import Output
from Disco import Disco
from Deployer import Deployer
import os
from lxml import etree

class MyTestCase(unittest.TestCase):
    # def test_something(self):
    #     output = Output()
    #     output.add_property({"test2": {"foobar": "value"}})
    #     fwinst = Component(os.path.join(os.getcwd(),"..","data","test1"),output)
    #     fwinst.handle_output()
    #     curoutput = output.get_output()
    #     print(curoutput)
    #     print(etree.tostring(fwinst.xml))
    #
    #     self.assertEqual(True, False)

    def test_component_output(self):
        output = Output()
        # output.add_property({"test2": {"foobar": "value"}})
        fwinst = Component(os.path.join(os.getcwd(),"..","data","heat"),output)
        fwinst.set_requested_properties({
            'slavecount':'3',
            'state':'start',
            'masterimage':'d6c4e3fe-cac9-4e37-9ada-45085296673f',
            'slaveimage':'d6c4e3fe-cac9-4e37-9ada-45085296673f',
            'masterflavor':'2',
            'slaveflavor':'2',
            'mastername':'masternode-5a0014ab-b56c-11e6-8fca-34363b7e7806',
            'slavename':'slavenode-5a0014ab-b56c-11e6-8fca-34363b7e7806-',
            'externalnetworkname':'public',
            'networkname': 'network_-5a0014ab-b56c-11e6-8fca-34363b7e7806'
        })
        fwinst.handle_output()
        curoutput = output.get_output()
        print(curoutput)
        # print(etree.tostring(fwinst.xml))

        pass

    def test_component_shell(self):
        output = Output()
        output.append_output("blabla\n<shell>some output\nfoobar\n</shell>blablabla")
        fwinst = Component(os.path.join(os.getcwd(),"..","data","shell"),output)
        fwinst.handle_output()
        curoutput = output.get_output()
        print(curoutput)


        framework_directory = os.path.join(os.path.dirname(__file__),"..","data")
        disco_config = {"framework_directory": framework_directory, "root_component": "heat", "root_component_state": "end","deployer":Deployer()}

        discoinst = Disco(disco_config, None)

        discoinst.resolve_dependencies()

        discoinst.inject_requested_properties({'heat':{
            'slavecount':'3',
            'state':'start',
            'masterimage':'d6c4e3fe-cac9-4e37-9ada-45085296673f',
            'slaveimage':'d6c4e3fe-cac9-4e37-9ada-45085296673f',
            'masterflavor':'2',
            'slaveflavor':'2',
            'mastername':'masternode-5a0014ab-b56c-11e6-8fca-34363b7e7806',
            'slavename':'slavenode-5a0014ab-b56c-11e6-8fca-34363b7e7806-',
            'externalnetworkname':'public',
            'networkname': 'network_-5a0014ab-b56c-11e6-8fca-34363b7e7806'
        }})

        current_output = discoinst.generate_output()
        print(current_output)

if __name__ == '__main__':
    unittest.main()
