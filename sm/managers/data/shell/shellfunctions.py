from lxml import etree

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
