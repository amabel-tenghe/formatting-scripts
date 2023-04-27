# formatting-scripts
Scripts for formatting different targets

## 1.`affiliation_formatter.py`

Creates a formatted list of author affiliations for publications with too many authors

*** Usage ***
Typing ./affiliation_formatter.py -h will print help message

```
usage: affiliation_formatter.py [-h] -i INPUT [-o OUTPUT]

Create a formatted list of author affiliation list for publications with too many authors

options:
  -h, --help            show this help message and exit
  -i INPUT, --input INPUT
                        Input file in .xlsx or .csv format (REQUIRED) (default: None)
  -o OUTPUT, --output OUTPUT
                        String text to be used as output file name (.html format) (default: None)

```

**Input File**

Required fields of the input .xlsx or .csv file:

* First Name
* Middle Name" (Only initials without spaces)
* Last Name

Optional fileds - Affiliation fields:
* Institute/Department/University
* City/State 
* Post/Zip code
* Country

The affiliation fields can be repeated as many times as necessary. Other fields
in the input file will not be considered.


**Output formats**

Author names: [First Name] [Middle name initials]. [Last name]^[affiliation_number]

Affiliation list: [affiliation_number]. [Institute/Department/University], [City/State] [Post/Zip Code], [Country]
