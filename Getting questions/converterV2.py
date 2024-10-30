#!/usr/bin/env python

import os
import sys
import pyzipper
import lxml.etree as ET
from termcolor import colored
import unicodedata
import re
import glob
import pathlib
from jinja2 import Environment, FileSystemLoader
import shutil


def extract_mbz(mbz_file, extract_to):
    if not os.path.isfile(mbz_file):
        print(f"File not found: {mbz_file}")
        sys.exit(1)

    # Umbenennen der MBZ-Datei in ZIP
    zip_file = mbz_file.replace('.mbz', '.zip')
    shutil.copy(mbz_file, zip_file)

    # Erstellen des Verzeichnisses zum Extrahieren
    os.makedirs(extract_to, exist_ok=True)

    try:
        # Extrahieren der ZIP-Datei
       with pyzipper.AESZipFile(mbz_file, 'r') as zip_ref:
        zip_ref.extractall(extract_to)
        print("Extraction successful.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        sys.exit(1)

    # Rückgabe des Verzeichnispfades, in das extrahiert wurde
    return extract_to

def slugify(value, allow_unicode=False):
    value = str(value)
    if allow_unicode:
        value = unicodedata.normalize('NFKC', value)
    else:
        value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')  
    value = re.sub(r'[^\w\s\-\.]', '', value.lower())
    return re.sub(r'[-\s]+', '-', value).strip('-_')

def split_xml():
    filename = "question.xml" 
    folder = "separate_questions"
    
    if not os.path.exists(folder):
        os.makedirs(folder)

    parser = ET.XMLParser(strip_cdata=False)
    tree = ET.parse(filename, parser)
    root = tree.getroot()

    questions = root.findall(".//question")

    for question in questions:
        if question not in root.findall(".//question[@type='category']"):
            name = question.find('name').find('text').text
            print(name)
            filename = slugify(name)
            path = os.path.join(folder, filename + '.xml')
            i = 0
            while os.path.exists(path):
                i += 1
                print(colored("Error: File exists: " + path, "red"))
                path = os.path.join(folder, filename + '___' + str(i) + '.xml')
            with open(path, 'wb') as f:
                f.write(b'<?xml version="1.0" encoding="UTF-8"?>\n<quiz>\n')
                f.write(ET.tostring(question, pretty_print=True))
                f.write(b'\n</quiz>')

def convert2xml():
    directoryOfScript = pathlib.Path(__file__).parent.resolve()
    environment = Environment(loader=FileSystemLoader(directoryOfScript))
    template = environment.get_template("quiz_temp.xml.jinja")

    try:
        os.chdir(sys.argv[1])
    except OSError as error:
        print(error)

    directory = 'convertedMoodleXml'
    workingDirectory = pathlib.Path().resolve()
    try: 
        if not os.path.exists(directory):
            path = os.path.join(workingDirectory, directory)
            os.mkdir(path)
    except OSError as error: 
        print(error)

    filename = glob.glob('*.xml')

    def checkForNone(checkvar):
        if checkvar.text == '$@NULL@$': 
            checkvar.text = ''
        return checkvar

    for file in filename:
        tree = ET.parse(file)
        root = tree.getroot()  
        questionId= "<!-- question: "+ str(root[0].get('id')) +" -->"

        # regular information about question
        liste = ['name','questiontext','generalfeedback','defaultmark','penalty','hidden','idnumber','stackversion','questionvariables','specificfeedback','questionnote','questionsimplify','assumepositive','assumereal','prtcorrect','prtpartiallycorrect','prtincorrect','multiplicationsign','sqrtsign','complexno','inversetrig','logicsymbol','matrixparens','variantsselectionseed']

        infos = []
        for tag in liste:
            k = [elem for elem in root.iter(tag)]
            if len(k) > 0:
                if k[0].tag == 'defaultmark': 
                    k[0].tag = 'defaultgrade'
                if tag in ['questiontext','generalfeedback','specificfeedback','prtcorrect','prtpartiallycorrect','prtincorrect']:
                    if str(k[0].text) == 'None': 
                        k[0].text = '\n\t\t\t\t<text>'
                    else: 
                        k[0].text = '\n\t\t\t\t<text><![CDATA['+str(k[0].text)+']]>'
                    k[0].text += '</text>\n\t\t'
                if tag in ['questionnote','stackversion','questionvariables','name']:
                    k[0].text = '\n\t\t\t\t<text>'+(k[0].text or '')+'</text>\n\t\t'
                infos.append(checkForNone(k[0]))

        # the inputs
        inputs = [checkForNone(elem) for elem in root.iter('stackinput')]

        # the prts
        prts = []
        format = ['moodle_auto_format','html']
        for i, prt in enumerate(root.iter('stackprt')):
            prts.append([])
            helplist = []
            for prtvar in prt:
                if prtvar.tag == 'stackprtnodes': 
                    break
                elif prtvar.tag == 'feedbackvariables': 
                    prtvar.text = '\n\t\t\t\t<text>'+(prtvar.text or '')+'</text>\n\t\t\t'
                helplist.append(checkForNone(prtvar))
            prts[i].append(helplist)
            for node in prt.iter('stackprtnode'):
                helpnode = []
                for value in node:
                    if value.tag == 'nodename': 
                        value.tag = 'name'
                    elif 'format' in value.tag:  
                        continue
                    elif 'feedback' in value.tag: 
                        value.text = '\n\t\t\t\t\t<text>'+(value.text or '')+'</text>\n\t\t\t\t'
                    helpnode.append(checkForNone(value))
                prts[i].append(helpnode)

        # deployedseed
        seeds = root.iter('seed')

        # qtest
        stackqtest = []
        for i, qtest in enumerate(root.iter('stackqtest')):
            stackqtest.append([])
            stackqtest[i].append(qtest[0])
            stackqtest[i].append(qtest.iter('stackqtestinput'))
            helplist = []
            for j, expect in enumerate(qtest.iter('stackqtestexpected')):
                helplist.append([])
                for value in expect:
                    if value.tag == 'prtname': 
                        value.tag = 'name'
                    helplist[j].append(checkForNone(value))
            stackqtest[i].append(helplist)

        # stamp und version
        tags = []
        tags.append(root[0].find('stamp'))
        tags.append(root[0].find('version'))

        content = template.render(info_template=infos, questionid=questionId, input_template=inputs, deployedseed=seeds, prt_template = prts, qtests = stackqtest, tag = tags)   
        try:
            with open("new_xml/new_"+file, mode="w", encoding="utf-8") as newfile:
                newfile.write(content)
        except FileNotFoundError:
            print("The 'new_xml_data' directory does not exist")
        finally:
            newfile.close() 

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Usage: python3 script.py <mbz_file>')
        sys.exit(1)

    mbz_file = sys.argv[1]
    
    # Step 1: Extract question.xml from mbz
    extract_dir = extract_mbz(mbz_file, 'extracted_mbz')
    os.chdir(extract_dir)

    # Step 2: Split question.xml into separate files
    split_xml()

    # Step 3: Process the separate XML files 
    os.chdir("separate_questions")  # Korrigierte Schreibweise
    convert2xml()