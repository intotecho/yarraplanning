# -*- coding: utf-8 -*-
# noqa: E501
"""
The Scheudle to the Yarra Heritage Register is part of the Yarra Planning Scheme:
Schedule 43.01
http://planningschemes.dpcd.vic.gov.au/schemes/vpps/43_01.pdf

After downloading the PDF and converting to tabula, this program will clean it up into a table suitable for import.

This file can be processed into a CSV table by Tabula. 
Select Tabula Stream mode rather than Lattice
https://github.com/tabulapdf/tabula
However there are a number of issues process the file, leading to
1. Records with multiline text being  split over several rows of the CSV.
   These need to be detected and merged.

The objective of this script is to correct as manu errors as possible
so that the output is ready for uploading to BigQuery or other databases.

"""

'''
input_df_columns = [
    'Heritage Place',
    'Heritage Place.1',
    'External\rPaint\rControls\rApply?',
    'External',
    'Internal\rAlteration\rControls\rApply?',
    'Internal',
    'Tree\rControls\rApply?',
    'Tree',
    'Unnamed: 10',
    'Outbuildings',
    'Unnamed: 12',
    'Included on the\rVictorian Heritage\rRegister under the\rHeritage Act 2017 ?',
    'Included on the',
    'Prohibited\ruses may be\rpermitted?',
    'Prohibited',
    'Aboriginal\rheritage\rplace?',
    'Aboriginal'
]
input_df.columns = [
    'Overlay',
    'HeritagePlace',
    'PaintControls',
    'InternalControls',
    'TreeControls',
    'FenceControls',
    'IncludedInVHR',
    'ProhibitedUsesPermited',
    'AboriginalHeritagePlace']
'''

import pandas as pd
import logging
import re
import numpy as np

logger = logging.getLogger("root")
logger.setLevel(logging.INFO)
# create console handler
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
logger.addHandler(ch)


# ------------------ CONFIGURATION -------------------------------

# Set your input file here
# e.g. "revew_of_heritage_overlay_areas_2007_rev_may_2017.csv"
input_filename = "tabula-43_01s_yarra_lattice.csv"
# Set your output file name here.
output_filename = "tabula-43_01s_yarra_cleaned.csv"

# Specify the columns we wish to read from the apps file. We want them all.
schedule_columns_in = [
    'PS', 'Heritage Place', 'External',
    'Internal', 'Tree', 'Outbuildings',
    'Included on the', 'Prohibited', 'Aboriginal'
]


# ------------------ DATA LOADING --------------------------------

# Read the input data to a Pandas Dataframe
try:
    input_df = pd.read_csv(
        input_filename,
        encoding='utf8') # ,
        #usecols=register_columns_in)
except Exception as e:
    logger.error("Input File Exception {} ".format(e))
    exit()
if 'PS' not in input_df.columns:
    raise ValueError("Missing PS column in input data")

# Rename columns to be BigQuery compatible
# You have to add a column heading for 'Overflow' manually to the input file.

print (input_df.columns)


input_df.rename(columns={
    'PS': 'Overlay',
    'Heritage Place': 'HeritagePlace',
    'External':  'PaintControls',
    'Internal': 'InternalControls',
    'Tree': 'TreeControls',
    'Outbuildings': 'FenceControls',
    'Included on the': 'IncludedInVHR',
    'Prohibited': 'Prohibited',
    'Aboriginal': 'AboriginalHeritagePlace',
}, inplace=True)
input_df = input_df.iloc[:, : 9]

input_count = len(input_df['Overlay'])

# There are some rows which are completely empty so drop them first.
#input_df.dropna(how='all', inplace=True)


''
#Convert control  symbols  if needed.
input_df['Overlay'] = input_df['Overlay'].str.replace(r'\r', " ")
input_df['HeritagePlace'] = input_df['HeritagePlace'].str.replace(r'\r', " ")
input_df['PaintControls'] = input_df['PaintControls'].str.replace(r'\r', " ")
input_df['InternalControls'] = input_df['InternalControls'].str.replace(r'\r', " ")
input_df['TreeControls'] = input_df['TreeControls'].str.replace(r'\r', " ")
input_df['IncludedInVHR'] = input_df['IncludedInVHR'].str.replace(r'\r', " ")

input_df.fillna(" ", inplace=True)
input_df['keyrow'] = (input_df['Overlay'].str.match(r'.*HO\d*.*') != 0)

input_df['FenceControls'] = input_df['FenceControls'].apply(str)
input_df = input_df[input_df['Overlay'].str.match(r'PS|map|ref') == 0]
input_df = input_df[input_df['PaintControls'].str.match(r'Controls|Apply') == 0]
input_df = input_df[input_df['FenceControls'].str.match('Clause 43\.01\-4') == 0]
input_df.reset_index(inplace=True, drop=True)
#print(input_df['FenceControls'].tolist())
print ('=== HEAD ===')
print (input_df.head(20))
#print (input_df.shape)
#print (input_df.info())
#print (input_df[3])
#print (input_df['FenceControls'].tolist())
print ('=== LOOP ===')
length = len(input_df)
pattern = re.compile(r'\r')
for i in range(0, length-1):
    #if i >= length:
    #    print ('Exiting at row {} {}'.format(i, input_df.loc[i]))
    #    break
    heritagePlace = input_df.loc[i, 'HeritagePlace'].encode('utf-8')
    includedInVHR = input_df.loc[i, 'IncludedInVHR'].encode('utf-8').strip
    # print(includedInVHR)
    isKeyRow = input_df.loc[i, 'keyrow']
    if isKeyRow == True:
        for d in range(i+1, length):
            isfollowingRowKey = input_df.loc[d, 'keyrow']
            if isfollowingRowKey == False:
                try:
                    heritagePlace = heritagePlace + u' ' + input_df.loc[d, 'HeritagePlace'].encode('utf-8')
                    includedInVHR = includedInVHR + u' ' + input_df.loc[d, 'IncludedInVHR'].encode('utf-8').replace(u"\u2019", "'")

                    print('{} {}'.format(i, includedInVHR))
                except ValueError, TypeError:
                    print ("exception: {}: {}".format(
                        input_df.loc[i, 'HeritagePlace'],
                        input_df.loc[d, 'HeritagePlace']))
            else:
                break
        input_df.loc[i, 'HeritagePlace'] = heritagePlace
        input_df.loc[i, 'IncludedInVHR'] = includedInVHR
        print(includedInVHR)
    else:
        pass


input_df['VHR'] = input_df['IncludedInVHR'].str.replace(
    r"(.*)(H\d*)(.*)",
    "\\2")
input_df['IncludedIn'] = 'No'
input_df['IncludedIn'] = input_df['IncludedInVHR'].str.replace(
    r"(\w*).*",
    "\\1")

# ---- save the results. ---- #
output_df = input_df
output_df.to_csv("{}".format(
    output_filename),
    mode='w',
    header=True,
    index=False,
    encoding='utf8')
output_count = len(output_df['Overlay'])
print('Cleaned {} lines to {} lines'.format(input_count, output_count))
exit(0)
