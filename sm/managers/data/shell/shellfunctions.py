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

#TODO: make this method more generic: multiple shell tags should be handled just like shell tags at the very beginning of the string
def indentshell(context,allcontent):
    '''
    indentshell indents each line between <shell>...</shell> tags by 12 spaces
    attention: this function only works if:
        1. the shell tag is present once or not at all in allcontent
        2. <shell> must not be at the first position
    :param context:
    :param allcontent: all output up to this time
    :return:
    '''
    try:
        allcontent = str(allcontent)
        left = allcontent.split("<shell>")
        right = left[1].split("</shell>")
        master_bash = right[0]
        master_bash_lines = master_bash.splitlines(True)
        masterbash = ""
        for line in master_bash_lines:
            masterbash += ' '*12+line
        if len(right)==1:
            return str(left[0]+masterbash)
        return str(left[0]+masterbash+right[1])
    except:
        return allcontent
