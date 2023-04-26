#!/usr/bin/env python

# created by Michael Kallweit
# latest changes: 2023-03-13

import sys,os
import bs4
import re
import lxml.etree as ET
from lxml.etree import CDATA
import easygui

orig_prettify = bs4.BeautifulSoup.prettify
r = re.compile(r'^(\s*)', re.MULTILINE)
def prettify(self, encoding=None, formatter="minimal", indent_width=4):
    return r.sub(r'\1' * indent_width, orig_prettify(self, encoding, formatter))
bs4.BeautifulSoup.prettify = prettify

def prettify_html(html):
    soup = bs4.BeautifulSoup(html, 'html.parser')
    return soup.prettify()


if __name__ == '__main__':
    new_xml_files=[]
    xml_files = easygui.fileopenbox("Select xml file","prettify","*.xml",multiple=True)
    if not xml_files:
        sys.exit(1)

    folder="prettified"
    if not os.path.exists(folder):
        os.makedirs(folder)

    for xml_file in xml_files:
        if not os.path.isfile(xml_file):
            easygui.msgbox('File not found: ' + xml_file)
            sys.exit(1)


        parser = ET.XMLParser(strip_cdata=False)
        tree = ET.parse(xml_file, parser)

        for elem in tree.iter():
            if elem.text == None:
                elem.text = ''

        ET.indent(tree, space="    ")

        for element in tree.findall(".//*[@format='html']/text"):
            if b"<![CDATA[" in ET.tostring(element):
                element.text = CDATA('\n'+prettify_html(element.text).strip()+'\n')

        path,filename=os.path.split(xml_file)
        new_xml_file=os.path.join(path,folder,filename)
        tree.write(new_xml_file,pretty_print=True,encoding="utf-8")
        new_xml_files.append(new_xml_file)

    easygui.msgbox('File(s) prettified:\n\n ' + "\n\n".join(new_xml_files))
