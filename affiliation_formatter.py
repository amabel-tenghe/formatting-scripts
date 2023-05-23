#!/usr/bin/env python

'''
Creates a formatted list of author affiliations for publications with too many authors

Input:
A .xlsx or .csv file 

Required fields of the input file:
"First Name",
"Middle Name" (Only initials without spaces),
"Last Name"

Optional fieds of input file - Affiliation fields:
"Institute/Department/University",
"City/State",
"Post/Zip code",
"Country"

Output formats:
Author names: [First Name] [Middle name initials].[Last name]^[affiliation_number]
Affiliation list: [affiliation_number].[Institute/Department/University],[City/State] [Post/Zip Code], [Country]
'''

# Dependencies
import pandas as pd
import numpy as np
import itertools
import argparse
import warnings 
import re
import os.path
import sys

parser = argparse.ArgumentParser(
    formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    description="Create a formatted list of author affiliation list for publications with too many authors")
parser.add_argument_group('Options')
parser.add_argument(
    "-i", "--input", help="Input file in .xlsx or .csv format (REQUIRED)", required=True)
parser.add_argument(
    "-o", "--output", help="String text to be used as output file name (.html format)", required=False, default="inputFilename.html")
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


def get_num_affi_author(indata):
    '''
    Get maximum number of affiliations by an author (based on Country field count)
    '''
    suffixes = ['']
    for field in indata.columns.tolist():
        try:
            match = re.search("Country(.+)", field)
            suffixes.append(match.groups()[0])
        except:
            continue
    print(f"[Info] Maximum number of affiliations by an author: {len(suffixes)}")
    print(f"[Info] Number of authors in the list: {len(indata)}")
    return suffixes


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


def generate_assign_aff_numbers(indata):
    ''' 
    Generate affiliation numbers and combine with authors names
    '''
    names_numbers = []
    affiliation_dict = {}
    affiliation_index = 0

    for row in indata.iterrows():
        numbers = []

        # checking if the given affiliation is already in the dictionary
        # If not, add affiliation number
        for affiliation in row[1]["affiliation_total"]:
            try:
                numbers.append(affiliation_dict[affiliation])
            except:
                affiliation_index += 1
                affiliation_dict[affiliation] = affiliation_index
                numbers.append(affiliation_dict[affiliation])
                names_numbers.append([row[1]['full_name'], numbers])

    return affiliation_dict, names_numbers

#=================================================================================

def main(args):
    """ 
    Parse input arguments and run defined functions
    """
    ### Parse command line parameters:
    inputFile = args.input
    outputFile = ''

    if args.output:
        outputFile = str(args.output) + '.html'
    elif inputFile.endswith(".csv"):
        # Output file was not given, generated by the input filename:
        try:
            filename = re.search("/+(.+)\.csv", inputFile)
            outputFile = filename.groups()[0] + ".html"
        except:
            filename = re.search("(.+)\.csv", inputFile)
            outputFile = filename.groups()[0] + ".html"


    print("\n")
    print(f"[Info] Input file:  {inputFile}")
    print(f"[Info] Output file: {outputFile}\n")

    ### Reading input file:
    if not os.path.isfile(inputFile):
        sys.exit(f"[Error] Input file {inputFile} does not exist.\n")
        
    if inputFile.endswith(".csv"):
        infile = pd.read_csv(inputFile, sep=';')
        infile= infile.astype('string')
        cols = infile.columns.tolist()
        cols = [x.title() for x in cols]
        infile.columns = cols
    else:
        print("[Error] Input file is not .csv, file could not be loaded")
        sys.exit(1)
        

    ## Delete all lines where none of the name fields are filled:
    infile = infile.dropna(
        how='all', subset=["First Name", "Middle Name", "Last Name"]).reindex()

    ## Generate formatted full-names:
    infile['full_name'] = infile.apply(get_fullname, axis=1)


    ## Get maximum number of affiliations per author 
    suffixes= get_num_affi_author(indata=infile)

    ## Generate a list of formatted affiliations:
    infile['affiliation_total'] = infile.apply(
        get_affiliation, axis=1, args=([suffixes]))

    ## Combining authors name and affiliations number:
    affiliation_info= generate_assign_aff_numbers(indata=infile)

    ## Format Final Output
    affiliation_dict_sorted = sorted(affiliation_info[0], key=affiliation_info[0].get)

    print("[Info] Formatting output... ")
    ## Now we have to print out the affiliation list sorted for the dictionary value:
    html = '<!DOCTYPE html>\n<html>\n<body>\n<div></div>\n\n<div style="font-size: 16px; margin-left: 10px">'

    # Create authors list with affiliation numbers
    names_numbers= affiliation_info[1]
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
    for index, affiliation in enumerate(affiliation_dict_sorted):
        html += '\t<li>%s</li>\n' % (affiliation)

    html += '</ol>\n<br>\n</body>\n</html>'

    # Saving html data into file:
    f = open(outputFile, 'w')
    #f.write(html.encode('utf8'))
    f.write(html)
    f.close()

    print(" Done.")


if __name__ == '__main__':
    main(args)

####################
## Example usage:
## python affiliation_formatter.py -i author_list.xlsx -o output.html
###################
