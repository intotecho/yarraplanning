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
2. Some fields get shifted into the wrong column.

3. Sometimes tabula completely threw some fileds away. 
   So some manual editing of the tabula-43_01s_yarra_lattice_auto.csv file was done 
   to create the input file tabula-43_01s_yarra_lattice.csv
   The changes made can be seen by diffing the two files in the repo.
    
The objective of this script is to correct as many errors as possible
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
exported_columns = [
    'Overlay',
    'HeritagePlace',
    'PaintControls','InternalControls','TreeControls','FenceControls','IncludedInVHR','Included', 'VHR', 'Prohibited','AboriginalHeritagePlace', 'Status', 'Expiry']

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

# Set your input file here - this is the output of tabula.
# e.g. "tabula-43_01s_yarra_lattice.csv"
input_filename = "tabula-43_01s_yarra_lattice.csv"
# Set your output file name here.
output_filename = "heritage_schedule_cleaned.csv"

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
input_df = input_df.iloc[:, : 13] # will need to drop 4 more after processing
input_df['Included'] = '' # Fill with Yes or No from IncludedInVHR
input_df['VHR'] = '' # Fill with the H reference from IncludedInVHR. 
# WARNING. Does not support multiple H references numbers for HO350.

input_count = len(input_df['Overlay'])

print ('=== SHIFT BLANK CELLS ===')
'''
Tabula has inserted some rows with nan. So the content is shifted to the right.
This function will remocve the nan and shift the rest of the row to the left.
All the real content has type string, not float.
NOTE: This is a very slow function...
'''
def shiftLeftWhenColumnEmpty(s):
    firstColumn = 2
    #count = 0
    for c in range(firstColumn, len(s)-1):
        if type(s[c]) == float: #np.nan:
            s[c:] = s[c:].shift(-1)
            #count = count + 1
    #if count > 0:
    #    print('\nShifted: ', count)
    return s

input_df = input_df.apply(shiftLeftWhenColumnEmpty, axis=1)

print ('=== REMOVE TITLE ROWS ===')
'''
The following indicate title rows from the PDF that can be deleted from the data

PS,Heritage Place,External,Internal,Tree,Outbuildings,Included on the,Prohibited,Aboriginal,,,,
map,,Paint,Alteration,Controls,or fences,Victorian Heritage,uses may be,heritage,,,,
ref,,Controls,Controls,Apply?,which are not,Register under the,permitted?,place?,,,,
,,Apply?,Apply?,exempt under,Heritage Act 2017 ?,,,,,,,
,,,Clause 43.01-4,,,,,,,,,
'''
input_df['isTitleRow'] = \
                            (input_df['Overlay'] == 'PS')   |  \
                            (input_df['Overlay'] == 'PS Heritage Place')   |  \
                            (input_df['Overlay'] == 'map')  |  \
                            (input_df['Overlay'] == 'ref')  |  \
                            (input_df['PaintControls'] == 'Apply?') | \
                            (input_df['PaintControls'] == 'Clause 43.01-4') | \
                            (input_df['InternalControls'] == 'Clause 43.01-4')


print ('=== INTERMEDIATE ===')
input_df.to_csv("{}".format(
    "intermediate.csv"),
    mode='w',
    header=True,
    index=False,
    encoding='utf8')

input_df = input_df.drop(input_df[input_df.isTitleRow == True].index)
input_df.reset_index(inplace=True, drop=True)

# There are some rows which are completely empty so drop them.
# input_df.dropna(how='all', inplace=True)

input_df['Overlay'] = input_df['Overlay'].str.replace(r'\r', " ")
input_df['HeritagePlace'] = input_df['HeritagePlace'].str.replace(r'\r', " ")
input_df['PaintControls'] = input_df['PaintControls'].str.replace(r'\r', " ")
input_df['InternalControls'] = input_df['InternalControls'].str.replace(r'\r', " ")
input_df['TreeControls'] = input_df['TreeControls'].str.replace(r'\r', " ")
input_df['IncludedInVHR'] = input_df['IncludedInVHR'].str.replace(r'\r', " ")
input_df.fillna(" ", inplace=True)
input_df['keyrow'] = (input_df['Overlay'].str.match(r'.*HO\d*.*') != 0)

#print ('=== HEAD ===')
#print (input_df.head(20))
#print (input_df.shape)
#print (input_df.info())
#print (input_df[3])
#print (input_df['FenceControls'].tolist())



print ('=== LOOP ===')
'''
Slow loop...
For each keyrow, merge content from subsequent rows
'''
length = len(input_df)

for i in range(0, length-1):
    overlay = input_df.loc[i, 'Overlay']
    heritagePlace = input_df.loc[i, 'HeritagePlace']
    includedInVHR = input_df.loc[i, 'IncludedInVHR']
    paint = input_df.loc[i, 'PaintControls']
    internal = input_df.loc[i, 'InternalControls']
    isKeyRow = input_df.loc[i, 'keyrow']
    if isKeyRow == True:
        for d in range(i+1, length):
            isfollowingRowKey = input_df.loc[d, 'keyrow']
            if isfollowingRowKey == False:
                try:
                    nextoverlay = input_df.loc[d, 'Overlay']  
                    nextheritagePlace = input_df.loc[d, 'HeritagePlace']  
                    nextVHR = input_df.loc[d, 'TreeControls'] + input_df.loc[d, 'IncludedInVHR'] # Tablula puts the H number into the wrong column E.g. HO67, HO292 
                    nextPaint = input_df.loc[d, 'PaintControls'] 
                    nextInternal = input_df.loc[d, 'InternalControls'] 

                    overlay = overlay  + ' ' + nextoverlay
                    heritagePlace = heritagePlace  + ' ' + nextheritagePlace
                    includedInVHR = includedInVHR  + ' ' + nextVHR 
                    paint = paint  + ' ' + nextPaint 
                    internal = internal + ' ' + nextInternal 
                except TypeError :
                    print ("exception: {}: {}".format(
                        input_df.   loc[i, 'HeritagePlace'],
                        input_df.loc[d, 'HeritagePlace']))
            else:
                break
        
        input_df.loc[i, 'Overlay'] = overlay.strip()
        input_df.loc[i, 'HeritagePlace'] = heritagePlace.strip()
        input_df.loc[i, 'PaintControls'] = paint.strip()
        input_df.loc[i, 'InternalControls'] = internal.strip()
        input_df.loc[i, 'IncludedInVHR'] = includedInVHR.strip()

    else:
        pass

input_df['HeritagePlace'] = input_df['HeritagePlace'].str.replace(r'\n', " ")


# === DROP Non-Key  ROWS ====
# input_df[input_df['keyrow'] ==True]
input_df = input_df.drop(input_df[input_df.keyrow == False].index)
input_df.drop('keyrow', 1, inplace=True)

input_df['Included'] = input_df['IncludedInVHR'].str.extract(r'(\w*).*')
input_df['VHR'] = input_df['IncludedInVHR'].str.extract(r'\w* Ref No *(H\d*)')

regex = re.compile(
    r'^(HO\d{1,4})(.*(Interim).*(\d\d\/\d\d\/\d\d\d\d))?'
)
overlay_df = input_df['Overlay'].str.extract(regex, expand=True)
print (overlay_df.head(20))
input_df['Status'] = overlay_df[2]
input_df['Expiry'] = overlay_df[3]
input_df['Overlay'] = overlay_df[0]



# === save the results. === #
output_df = input_df
output_df.to_csv("{}".format(
    output_filename),
    mode='w',
    header=True,
    index=False,
    columns=exported_columns,
    encoding='utf8')
output_count = len(output_df['Overlay'])
print('Cleaned {} lines to {} lines'.format(input_count, output_count))
exit(0)
