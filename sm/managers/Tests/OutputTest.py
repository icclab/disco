import unittest
import os
from Output import Output

class TestOutput(unittest.TestCase):
    # def __init__(self, *args, **kwargs):
    #     super(TestOutput, self).__init__(*args, **kwargs)

    def test_output_handling(self):
        output = Output()
        teststring = "test this output"
        output.set_output(teststring)
        output.append_output(teststring)
        self.assertEqual(output.get_output(), 2*teststring)

    def test_property_handling(self):
        output = Output()
        propertyDict = {'fw1': {'prop1': 'val1', 'prop2': 'not val2'}, 'fw2': {'propfw2': 'something'}}
        output.add_property(propertyDict)
        self.assertEqual(output.get_properties(),propertyDict)
        updateDict = {'fw1': {'prop2': 'val2', 'prop3': None}, 'fw3': {'propfw3': 'foo'}}
        output.add_property(updateDict)
        propertyDict['fw1'].update(updateDict['fw1'])
        propertyDict['fw3'] = updateDict['fw3']

        # print(propertyDict)
        self.assertEqual(output.get_properties(),propertyDict)

if __name__ == '__main__':
    unittest.main()
