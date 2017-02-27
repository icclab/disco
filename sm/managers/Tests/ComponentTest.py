# import unittest
# from Component import Component
# from Output import Output
from lxml import etree

class TestFramework:
    # def __init__(self, *args, **kwargs):
    #     super(TestFramework, self).__init__(*args, **kwargs)
    #     os.chdir("..")

    # def get_test_component(self,fwname="shell",output=Output()):
    #
    #     fwinst = Component(os.path.join(os.getcwd(),"data",fwname),output)
    #     return fwinst
    #
    # def test_creation(self):
    #     # get_files() and register_functions() are implicitly tested as well
    #     os.chdir("..")
    #     fwinst = self.get_test_component()
    #     self.assertNotEquals(fwinst,None)
    #     self.assertDictEqual(fwinst.get_dependencies_from_xml(),{'hadoop': {'foobar':None,'property':None},'heat':{'fw2baz':None,'fw2foobar':None}})
    #     self.assertDictContainsSubset({'included':'false'},fwinst.get_all_properties())
    #     self.assertIsInstance(fwinst.xml,etree._Element)
    #     None
    #
    # def test_dependencies(self):
    #     fwinst = self.get_test_component('shell',Output().add_property({'hadoop': {'property': 'value'}}))
    #     self.assertDictContainsSubset({'hadoop':{'property':None,'foobar':None}}, fwinst.get_dependencies_from_xml())
    #     # following function implicitly is testing set_dependendy_value() as well
    #     fwinst.set_dependency_values()
    #     deps = fwinst.get_dependencies_from_xml()
    #     self.assertDictContainsSubset({'hadoop':{'property':'value','foobar':None}}, fwinst.get_dependencies_from_xml())
    #     # following function implicitly is testing add_dependency() as well
    #     fwinst.add_dependencies({'fake':{'prop':'val'}})
    #     self.assertDictContainsSubset({'fake':{'prop':'val'}},fwinst.get_dependencies_from_xml())
    #
    # def test_properties(self):
    #     fwinst = self.get_test_component()
    #     fwinst.set_requested_properties({'property': 'other value'})
    #     props = fwinst.get_all_properties()
    #     self.assertDictContainsSubset({'property': 'other value'},props)
    #     self.assertEqual('other value',fwinst.get_property_value('property'))
    #
    # def test_output(self):
    #     fwinst = self.get_test_component('hadoop')
    #     rettext = fwinst.get_output()
    #     print(rettext[0])

    def xml_standalone(self):
        # ns = etree.FunctionNamespace("test.xsl")
        # ns.prefix = "test"
        # ns['replace'] =
        xslt_root = etree.XML('''\
     <xsl:stylesheet version="1.0"
         xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

         <xsl:template name="recursive-template">
           <xsl:param name="var" select="5"/>
           <xsl:choose>
             <xsl:when test="$var > 0">
               <!--<xsl:value-of select="$var"/>-->
               <xsl:value-of select="/root/slavetemplate" />
               <xsl:value-of select="$var" />

               <xsl:call-template name="recursive-template">
                 <xsl:with-param name="var" select="$var - 1"/>
               </xsl:call-template>
             </xsl:when>
             <xsl:otherwise/>
           </xsl:choose>
        </xsl:template>

         <xsl:template match="/output">
             <foo><xsl:call-template name="recursive-template" /></foo>
         </xsl:template>
     </xsl:stylesheet>''')
        transform = etree.XSLT(xslt_root)

        root = etree.XML('<root><slavetemplate>myslave</slavetemplate><output /></root>')
        result = transform(root)
        print(etree.tostring(result, pretty_print = True))

        # self.assertEqual(True,True)


    def test_dependency(self):
        # output = Output()
        # fwinst = Component(os.path.join(os.getcwd(),"..","data","test1"),output)
        # print(output.get_output())
        # self.assertEqual(True, True)
        pass


if __name__ == '__main__':
    # unittest.main()
    testfw = TestFramework
    testfw.xml_standalone()
