from lxml import etree
import random

def replace(context, content, replacedict):
    try:
        returnvalue = content[0]
        for replace_entity in replacedict:
            returnvalue = returnvalue.replace(replace_entity.attrib['string'], replace_entity.attrib['replace'])
        return str(returnvalue)
    except:
        return content[0]
