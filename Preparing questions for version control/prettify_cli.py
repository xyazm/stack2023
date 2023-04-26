#!/usr/bin/env python

# created by Michael Kallweit
# latest changes: 2023-03-13

import sys,os
import bs4
import re
import lxml.etree as ET
from lxml.etree import CDATA

orig_prettify = bs4.BeautifulSoup.prettify
r = re.compile(r'^(\s*)', re.MULTILINE)
def prettify(self, encoding=None, formatter="minimal", indent_width=4):
    return r.sub(r'\1' * indent_width, orig_prettify(self, encoding, formatter))
bs4.BeautifulSoup.prettify = prettify

def prettify_html(html):
    soup = bs4.BeautifulSoup(html, 'html.parser')
    return soup.prettify()


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Usage: python3 prettify_cli.py <xml_file>')
        sys.exit(1)
    xml_file = sys.argv[1]
    if not os.path.isfile(xml_file):
        print('File not found: ' + xml_file)
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
    new_xml_file=os.path.join(path,'pretty_'+filename)
    tree.write(new_xml_file,pretty_print=True,encoding="utf-8")

    print('File prettified: ' + new_xml_file)
