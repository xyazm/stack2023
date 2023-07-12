This is a collection of useful tools for working with XML files of moodle questions, especially of the question type STACK. The work was presented at the International Meeting of the STACK Community 2023, Tallinn, Estonia, 24 - 26 April 2023. See also: https://zenodo.org/record/8032232

## Getting questions
### Splitting an exported xml file
Tool: `split_exported_xml.py`.

It takes an moodle xml file with many questions (export from question bank) and outputs a separate xml file for every question in the folder `separate_questions`.

Usage: `python split_exported_xml.py XMLFILE`

### Extract from course backup
Tool: `convert_mbz.py`.

It extracts the `quesions.xml` from a moodle backup file and converts this to the Moodle XML-format for
questions (like an export from moodle question bank)

Usage: `python convert_mbz.py MBZFILE`

## Preparing questions for version control
Tool: `prettfy_cli.py` (cli) and `pretty_gui.py` (with gui). 

The scripts format a Moodle XML file and HTML snippets (CDATA) inside in a more visually appealing manner without sacrificing Moodle compatibility.
Specifically, the HTML tags are then line-by-line, making it easier for version control systems like GIT to manage changes.
This makes it easy to see in a diff which changes in HTML (for example translations) have been made.

Usage: `python prettfy_cli.py XMLFILE`

## Helping with doing translation work
Tools: `xml2csv.py` and `csv2xml.py`.

`xml2csv` opens all (moodle) xml files in the current directory and extracts the translations (`<span class="multilang">`) to csv files. The different strings are in rows, their translations in columns.
You can make modifications to this translation via some spreadsheet application.
Use `csv2xml` to bring back the modifications to new moodle xml files (with "_new" added to the filenames).

Usage: `python xml2csv.py`

Usage: `python csv2xml.py`


### Automatic translations

Tool: `xml2csv_with_autotranslate.py`

Instead of `xml2csv.py` you can use this script which adds a automatic translation provided by libretranslate.

Usage: `python xml2csv_with_autotranslate.py`
