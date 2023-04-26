import glob
import pathlib
import sys
from jinja2 import  Environment, FileSystemLoader
from lxml import etree as ET
import os

directoryOfScript = pathlib.Path(__file__).parent.resolve()
enviroment = Environment(loader=FileSystemLoader(directoryOfScript))
template = enviroment.get_template("quiz_temp.xml.jinja")

try:
    os.chdir(sys.argv[1])
except OSError as error:
    print(error)

directory = 'new_xml'
workingDirectory = pathlib.Path().resolve()
try: 
    if not os.path.exists(directory):
        path = os.path.join(workingDirectory,directory)
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
            if k[0].tag == 'defaultmark': k[0].tag = 'defaultgrade'
            if tag in ['questiontext','generalfeedback','specificfeedback','prtcorrect','prtpartiallycorrect','prtincorrect']:
                if str(k[0].text) == 'None': k[0].text = '\n\t\t\t\t<text>'
                else : k[0].text = '\n\t\t\t\t<text><![CDATA['+str(k[0].text)+']]>'
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
            if prtvar.tag == 'stackprtnodes': break
            elif prtvar.tag == 'feedbackvariables': 
                prtvar.text = '\n\t\t\t\t<text>'+(prtvar.text or '')+'</text>\n\t\t\t'
            helplist.append(checkForNone(prtvar))
        prts[i].append(helplist)
        for node in prt.iter('stackprtnode'):
            helpnode = []
            for value in node:
                if value.tag == 'nodename': value.tag = 'name'
                elif 'format' in value.tag:  continue
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
                if value.tag == 'prtname': value.tag = 'name'
                helplist[j].append(checkForNone(value))
        stackqtest[i].append(helplist)

    #stamp und version
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

