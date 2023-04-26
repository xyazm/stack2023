#!/usr/bin/env python

# created by Michael Kallweit
# latest changes: 2023-03-13

import lxml.etree as ET
import os,sys
from termcolor import colored

import unicodedata
import re
def slugify(value, allow_unicode=False):
    """
    Taken from https://github.com/django/django/blob/master/django/utils/text.py
    Convert to ASCII if 'allow_unicode' is False. Convert spaces or repeated
    dashes to single dashes. Remove characters that aren't alphanumerics,
    underscores, or hyphens. Convert to lowercase. Also strip leading and
    trailing whitespace, dashes, and underscores.
    """
    value = str(value)
    if allow_unicode:
        value = unicodedata.normalize('NFKC', value)
    else:
        value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')  
    value = re.sub(r'[^\w\s\-\.]', '', value.lower())
    return re.sub(r'[-\s]+', '-', value).strip('-_')

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Usage: python3 split_quiz_xml.py <xml_file>')
        sys.exit(1)
    filename = sys.argv[1]
    if not os.path.isfile(filename):
        print('File not found: ' + filename)
        sys.exit(1)

folder="separate_questions"

if not os.path.exists(folder):
    os.makedirs(folder)

parser = ET.XMLParser(strip_cdata=False)
tree = ET.parse(filename,parser)
root = tree.getroot()


questions=root.findall(".//question")

for question in questions:
    if question not in root.findall(".//question[@type='category']"):
        name=question.find('name').find('text').text
        print(name)
        filename=slugify(name)
        path=os.path.join(folder,filename+'.xml')
        i=0
        while os.path.exists(path):
            i+=1
            print(colored("Error: File exists: "+path,"red"))
            path=os.path.join(folder,filename+'___'+str(i)+'.xml')
        f=open(path,'wb')
        f.write(b'<?xml version="1.0" encoding="UTF-8"?>\n<quiz>\n')
        f.write(ET.tostring(question,pretty_print=True))
        f.write(b'\n</quiz>')
        f.close()
