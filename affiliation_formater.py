#!/usr/bin/env python
###!/usr/bin/env python

'''
This script was written to create a formatted list of author affiliation list
for publications with too many authors.

Required fields of the input xlsx file:
"First Name",
"Middle Name" (Only initials without spaces),
"Last Name"

Affiliation fields:
"Institute/Department/University",
"City/State",
"Post/Zip code",
"Country"

The affiliation fields can be repeated as many times as necessary. Other fields
in the xlsx table will not be considered.

Output formats:
Author names: [First Name] [Middle name initials]. [Last name]^[affiliation_number]
Affiliation list: [affiliation_number]. [Institute/Department/University], [City/State] [Post/Zip Code], [Country]
'''

# Dependencies
import pandas as pd
import numpy as np
import itertools
import argparse
import re
import os.path
import sys

parser = argparse.ArgumentParser(
    formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    description="Create a formatted list of author affiliation list for publications with too many authors")
parser.add_argument_group('Options')
parser.add_argument("-i", "--input", help="Input file in .xlsx  format (REQUIRED)", required=True)
parser.add_argument("-o", "--output", help="String text to be used as output file name (.html format)", required=False)
args = parser.parse_args()
#========================================================================
### Functions
# Check fields
def check_fields(infile, headerTwo=False):
    inheader = ['First Name', 'Middle Name', 'Last Name',
                'Institute/Department/University', 'City/State', 'Post/Zip code', 'Country']
    expected_header1 = [x.lower() for x in inheader]
    fields = [x.lower() for x in infile.columns.tolist()]
    if not set(expected_header1).issubset(set(fields)):
        print('Warning: Missing expected columns in header \n')
        print(f'Columns Missing: ', list(
            set(expected_header1) - set(fields)), '\n')
        print(f'Headers provided: ', fields, '\n')
        sys.exit(1)

    else:
        (print('pass'))


def get_fullname(row):
    ''' 
    Generate authors full name
    All first, middle and last names have to stripped to make sure there are not extra spaces added

    <First name> <Middle name initials>. <Last name>
    '''

    full_name = ""
    first = row['First Name']
    middle = row['Middle Name']
    last = row['Last Name']
    first_name = np.nan if pd.isnull(first) else first.strip()
    middle_name = np.nan if pd.isnull(middle) else middle.strip()
    last_name = np.nan if pd.isnull(last) else last.strip()

    try:
        if pd.isnull(middle_name):
            #No middle name
            full_name = first_name + " " + last_name

        else:
            #Middle name present
            full_name = first_name
            for initial in middle_name:
                full_name += " " + initial + "."
            full_name += " " + last_name
    except:
        #Only one name present
        try:
            full_name = first_name
        except:
            full_name = last_name
    return full_name


def get_affiliation(row, suffixes):
    '''
    Generate a list of affiliations

    '<Department/Institute>, <Town/city> <Post code/Zip code>, <Country>'
    '''
    affiliation_list = []

    for suffix in suffixes:
        #print(suffix)
        affiliation = ""

        inst = row['Institute/Department/University'+suffix]
        city = row['City/State' + suffix]
        postcode = row['Post/Zip Code' + suffix]
        country = row['Country' + suffix]

        if not pd.isnull(inst):
            affiliation += inst.strip()
            if not pd.isnull(city):
                affiliation += ", " + city.strip()
            if not pd.isnull(postcode):
                affiliation += " " + str(postcode).strip()
            if not pd.isnull(country):
                affiliation += ", " + country.strip()

        if len(affiliation) > 0:
            affiliation_list.append(affiliation)
    return affiliation_list

#=================================================================================
### Extracting command line parameters:
inputFile = args.input
outputFile = ''

if args.output:
    outputFile = args.output
else:
    # Output file was not given, generated by the input filename:
    try:
        filename = re.search("/+(.+)\.xls", inputFile)
        outputFile = filename.groups()[0] + ".html"
    except:
        filename = re.search("(.+)\.xls", inputFile)
        outputFile = filename.groups()[0] + ".html"

# Status update:
print(f"[Info] Input file:  {inputFile}")
print(f"[Info] Output file: {outputFile}\n")

### Reading input file:
if not os.path.isfile(inputFile):
    sys.exit(f"[Error] Input file {inputFile} does not exist.\n")
try:
    infile = pd.read_csv(inputFile, sep=';')
    cols = infile.columns.tolist()
    cols = [x.title() for x in cols]
    infile.columns = cols
except:
    sys.exit("[Error] input file could not be loaded!")

### Get maximum number of affiliations by an author (based on field counts):
suffixes = ['']
for field in infile.columns.tolist():
    try:
        match = re.search("Country(.+)", field)
        suffixes.append(match.groups()[0])
    except:
        continue
print(f"[Info] Maximum number of affiliations: {len(suffixes)}")
print(f"[Info] Number of authors in the list: {len(infile)}")

# Delete all lines where none of the name fields are filled:
infile = infile.dropna(
    how='all', subset=["First Name", "Middle Name", "Last Name"]).reindex()


### Generate formatted full-names:
infile['full_name'] = infile.apply(get_fullname, axis=1)

#### Generate a list of formatted affiliations:
infile['affiliation_total'] = infile.apply(
    get_affiliation, axis=1, args=([suffixes]))
print(" done.")

### Combining authors and affiliations together:
names_numbers = []
affiliation_list = {}
affiliation_index = 0

for row in infile.iterrows():
    numbers = []

    # checking if the given affiliation is already given
    for affiliation in row[1]["affiliation_total"]:
        try:
            numbers.append(affiliation_list[affiliation])
        except:
            affiliation_index += 1
            affiliation_list[affiliation] = affiliation_index
            numbers.append(affiliation_list[affiliation])
        names_numbers.append([row[1]['full_name'], numbers])



### Format Final Output
# Now we have to print out the affiliation list sorted for the dictionary value:
affiliation_list_sorted = sorted(affiliation_list, key=affiliation_list.get)

print("[Info] Formatting output... ")

# Now saving what we have:
html = '<!DOCTYPE html>\n<html>\n<body>\n<div></div>\n\n<div style="font-size: 16px; margin-left: 10px">'

# Create authors list with affiliation numbers
for row in names_numbers:
    author = row[0]
    affiliation = row[1]
    html += author

    if len(affiliation) > 0:
        aff_string = ",".join(str(x) for x in sorted(affiliation))
        html += '<sup>%s</sup>, \n' % aff_string
    else:
        html += ', '

html += '</div>\n\n<div></div><div></div><div style="font-size: 12px; margin-left: 20px">\n\n<ol>'
# Now looping through all the affiliations and save them:
for index, affiliation in enumerate(affiliation_list_sorted):
    html += '\t<li>%s</li>\n' % (affiliation)

html += '</ol>\n<br>\n</body>\n</html>'

# Saving html data into file:
f = open(outputFile, 'w')
#f.write(html.encode('utf8'))
f.write(html)
f.close()

print(" Done.")

####################
## Example usage:
## python affiliation_formater.py -i author_list.csv -o output.html
###################
