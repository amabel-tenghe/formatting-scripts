# formatting-scripts
Scripts for formatting different targets

## 1.`affiliation_formatter.py`

Creates a formatted list of author affiliations for publications with too many authors

*** Usage ***
Typing `./affiliation_formatter.py` -h will print help message

```
usage: affiliation_formatter.py [-h] -i INPUT [-o OUTPUT]

Create a formatted list of author affiliation list for publications with too many authors

options:
  -h, --help            show this help message and exit
  -i INPUT, --input INPUT
                        Input file in .csv format (REQUIRED) (default: None)
  -o OUTPUT, --output OUTPUT
                        String text to be used as output file name (.html format) (default: inputFilename.html)

```

**Input File**

The script relies on a previously compiled excel table with the author names and associated affiliations.

Required fields of the input .csv file:

* First Name
* Middle Name" (Only initials without spaces)
* Last Name

Optional fileds - Affiliation fields:
* Institute/Department/University
* City/State 
* Post/Zip code
* Country

The affiliation fields can be repeated as many times as necessary. Other fields
in the input file will be ignored.


**Output format**

Providing the name of the output file is optional, if not specified, the filename will be the same as the input file, except the extension will be html
The html file can be read by Word or other programs that deal with html (OpenOffice and LibreOffice should be fine) and saved in doc or docx format

Author names: [First Name] [Middle name initials]. [Last name]^[affiliation_number]

Affiliation list: [affiliation_number]. [Institute/Department/University], [City/State] [Post/Zip Code], [Country]
