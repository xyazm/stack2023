#!/usr/bin/python

import glob
#import xml.etree.ElementTree as ET
from lxml import etree as ET
from bs4 import BeautifulSoup
import csv
from bs4.formatter import HTMLFormatter


class UnsortedAttributes(HTMLFormatter):
    def attributes(self, tag):
        for k, v in tag.attrs.items():
            if k == 'm':
                continue
            yield k, v

filename=glob.glob('*.xml')[0]
tree = ET.parse(filename)
root = tree.getroot()
texte=root.findall('.//*[@format="html"]/text')

languages=set()
groups=[]
for text in texte:
    if text.text:
        soup = BeautifulSoup(text.text,'html.parser')
        spans = soup.findAll("span",{"class":"multilang"})
        group=[]
        for span in spans:
            languages.add(span['lang'])
            group.append(span)
            try:
                nexttag_name=span.find_next_sibling().name
            except:
                nexttag_name=""
            if nexttag_name!='span':
                groups.append(group)
                group=[]
        if group:
            groups.append(group)

infile=open(filename)
inhalt=infile.read()
infile.close()
csvfile=open(filename+'.csv','w',newline='',encoding='utf8')
fieldnames=['Nummer']+list(languages)
writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
writer.writeheader()
number=0
for group in groups:
    number+=1
    zeile={el['lang']:el.text for el in group}
    zeile['Nummer']='###'+str(number)+'###'
    writer.writerow(zeile)
    el=group[0]
    str_el=el.encode(formatter=UnsortedAttributes()).decode('utf-8')
    inhalt=inhalt.replace(str_el,zeile['Nummer'])
    for el in group[1:]:
        str_el=el.encode(formatter=UnsortedAttributes()).decode('utf-8')
        inhalt=inhalt.replace(str_el,'')
csvfile.close()

templatefile=open(filename+'.template','w',encoding='utf8')
templatefile.write(inhalt)
templatefile.close()
