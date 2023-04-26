#!/usr/bin/python


import glob
import csv

filename=glob.glob('*.xml')[0]

templatefile=open(filename+'.template')
inhalt=templatefile.read()
templatefile.close()

csvfile=open(filename+'.csv',encoding="ISO-8859-1")
reader = csv.DictReader(csvfile,delimiter=";")
languages=[lang for lang in reader.fieldnames if lang!='Nummer']
for row in reader:
    new_str="".join([f'<span lang="{lang}" class="multilang">{row[lang]}</span>' for lang in languages if row[lang]])
    inhalt=inhalt.replace(row['Nummer'],new_str)
csvfile.close()

newfile=open(filename[:-4]+'_new.xml','w',encoding='utf8')
newfile.write(inhalt)
newfile.close()
