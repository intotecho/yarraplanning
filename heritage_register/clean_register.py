# -*- coding: utf-8 -*-
"""
Python script for batch geocoding of addresses from an input file using the Google Geocoding API.

The input file: 
- Has many duplicate addresses
- May be partially encoded - i.e. some of the addresses were already geocoded by a previous iteration.

The script may be interrupted and run multiple times. It is reentrant but continues to process.
Keep running the script until there are no geocodings left to do. 
Each run will merge existing geocoding results with the input application data and write it to the output. 
Then it will try to geocode every reamining address in the applications file and write them to the output file. 
But it does not write to the output file again.

It requires an API key for paid geocoding from Google, set it in the API key section. You may also need to install pandas.

The geocoding function is based on a script by Shane Lynn, GitHub 5th November 2016. 
The rest of the script is loosely based on the same script, but modified by Chris Goodman March 2019.
- Geocode results are sorted nd stored in a CSV file
- Each address is only geocoded once. 
- New Results are merged back into the input file.
- The script can be interrupted so runs on the google cloud shell.
"""

import pandas as pd
import numpy as np
import logging
import re
logger = logging.getLogger("root")
logger.setLevel(logging.INFO) 
# create console handler
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
logger.addHandler(ch)


#------------------	FUNCTION DEFINITIONS ------------------------


#------------------ CONFIGURATION -------------------------------
 
# Set your input file here
input_filename = "revew_of_heritage_overlay_areas_2007_rev_may_2017.csv"

# Set your output file name here. It can be the same as the input file but safer to write to a new file.
output_filename = "{}_clean".format(input_filename)

# Specify the columns we wish to read from the apps file. Note that we ignore the columns of geocoded data as it is easier to join this in with the latest addresses. 
# This is also a good time to drop unwanted fields.
register_columns_in = ['Overlay', 'Address', 'Type',	'Number', 'Suburb', 'Property Type', 'Property No.', 'Heritage Status',	'Estimated Date']


#------------------ DATA LOADING --------------------------------

# Read the input data to a Pandas Dataframe
try:
    input_df = pd.read_csv(input_filename, encoding='utf8', usecols=register_columns_in)
except Exception as e:
    logger.error("Input File Not Found. Exception {} ".format(e))
    exit()
if 'Overlay' not in input_df.columns:
	raise ValueError("Missing Address column in input data")

# rename columns to be BigQuery compatible
input_df.columns = ['Overlay', 'AddressName', 'Type', 'Number', 'Suburb', 'PropertyType', 'PropertyId', 'HeritageStatus', 'EstimatedDate']
input_count = len(input_df['Overlay'])

#Convert all â€™ symbols to apostrophe if needed.
input_df['Overlay']= (input_df['Overlay'].str.replace(u'â€™', "\'"))
input_df['PropertyType']= (input_df['PropertyType'].str.replace(u'â€™', "\'"))
input_df['AddressName']= (input_df['AddressName'].str.replace(u'â€™', "\'"))

# There are some rows which are completely empty so drop them first.
input_df.dropna(how='all', inplace=True)

# Mege multiline entries to a single row.
# If Overlay on rw N is blank and Overlay on row N+2 is blank, then merge Nu,ber[n] and Number[n+2] into Number[n+1]
# Create a new column that concatenates the overlay from the line above and the line below. If this is blank, we have a split row.
#input_df['splitlines'] = input_df['Overlay'].shift(axis=0, periods=-1).str.cat(input_df['Overlay'].shift(axis=0, periods=1))


input_df['splitlines'] = input_df['Overlay'].shift(axis=0, periods=-1)
input_df = input_df.replace(np.nan, '', regex=True)
input_df['splitlines'] = input_df['splitlines'].str.cat(input_df['Overlay'].shift(axis=0, periods=1))
input_df['upper_blanklines'] = input_df['splitlines'].shift(axis=0, periods=1)
input_df['lower_blanklines'] = input_df['splitlines'].shift(axis=0, periods=-1)

def mergspliterows(df, column) :
    # Where cond is True, keep the original value. Where False, replace with corresponding value from other.
    # If splitlines is not empty or column is not empty then cond should be true and keep original value. 
    # if splitlines is empty and column is empty then transform column to the concatenation of above and below.
    
    df[column].where( ((df['splitlines'].str.len() != 0) | (df[column].str.len() != 0)), 
                         other=df[column].shift(axis=0, periods=1).str.cat(df[column].shift(axis=0, periods=-1)), 
                         inplace=True)
    return df

def deletespliterows(df) :
    # if splitlines is empty drop the row above and the row below
    #df = df.drop(df['upper_blanklines'], axis=0)
    #df = df.drop(df['lower_blanklines'], axis=0)
    df = df[df['upper_blanklines'].str.len() != 0 ]
    df = df[df['lower_blanklines'].str.len() != 0 ]
    return df



# for each split row, if the Number is also blank then combine Number from the row above concatenated with the Nu,ber from row below.
# do the same for PropertyType and Type
input_df = mergspliterows(input_df, 'Number')
input_df = mergspliterows(input_df, 'PropertyType')
input_df = mergspliterows(input_df, 'Type')

input_df = deletespliterows(input_df) 

# Remove temporary columns
input_df.drop(['splitlines'], axis=1, inplace = True)
input_df.drop(['upper_blanklines'], axis=1,  inplace = True)
input_df.drop(['lower_blanklines'], axis=1,  inplace = True)


# shift (copy) three columns to the right when the Overlay string is too long.
input_df['Number'].where(input_df['Overlay'].str.len() <= 5, other=input_df['Type'], inplace=True)
input_df['Type'].where(input_df['Overlay'].str.len() <= 5, other=input_df['AddressName'], inplace=True)
input_df['AddressName'].where(input_df['Overlay'].str.len() <= 5, other=input_df['Overlay'], inplace=True)

# Create a new DF with the first column split into two strings ['HO123' 'Bendigo Street 4']
overlay_df = input_df['Overlay'].str.split(pat=r'(HO[\d]*)', n=1, expand=True)
# have  look at this DF.
overlay_df.to_csv("{}".format("splits.csv"), mode='w', header=True, index=False, encoding='utf8')
#print(overlay_df.size)

#Copy the split strings toback  the first two columns.
input_df['AddressName'].where(input_df['Overlay'].str.len() <= 5, other=overlay_df[2], inplace=True)
input_df['Overlay'] = overlay_df[1]


# Remove blank lines - WARNING - Only do this after merged multiline entries
input_df['Overlay'].replace('', np.nan, inplace=True)
input_df.dropna(subset=['Overlay'], how='all', inplace=True)
# Remove rows for which all of the below columns contain blank values.
# Note that AddressName is not included in this list. So the code will still delete lines that only contain an Overlay and AddressName
# These lines are like 'HO309, - Barkly Gardens Precinct, Richmond,,,,,,; i.e. they describe the precinct name only, not a place. So can be dropped.
input_df = input_df[ 
                     (input_df['Type'].str.len() != 0) |
                     (input_df['Number'].str.len() != 0) |
                     (input_df['Suburb'].str.len() != 0) |
                     (input_df['PropertyType'].str.len() != 0) |
                     (input_df['PropertyId'].str.len() != 0) |
                     (input_df['HeritageStatus'].str.len() != 0) |
                     (input_df['EstimatedDate'].str.len() != 0)
                     ]


# shift (copy) three columns to the right when the PropertyID contains the heritage status of Contributory This fixesd 27 rows.
input_df['EstimatedDate'].where((input_df['PropertyId'].str.contains('Contributory|Individually') == False), other=input_df['HeritageStatus'], inplace=True)
input_df['HeritageStatus'].where((input_df['PropertyId'].str.contains('Contributory|Individually') == False), other=input_df['PropertyId'], inplace=True)
input_df['PropertyId'].where((input_df['PropertyId'].str.contains('Contributory|Individually') == False), other=input_df['PropertyType'], inplace=True)


# shift (copy) four columns to the right when the PropertyType contains the heritage status of Contributory This fixesd 259 rows.
input_df['EstimatedDate'].where((input_df['PropertyType'].str.contains('Contributory|Individually') == False), other=input_df['PropertyId'], inplace=True)
input_df['HeritageStatus'].where((input_df['PropertyType'].str.contains('Contributory|Individually') == False), other=input_df['PropertyType'], inplace=True)
input_df['PropertyId'].where((input_df['PropertyType'].str.contains('Contributory|Individually') == False), other=input_df['Suburb'], inplace=True)
input_df['Suburb'].where((input_df['PropertyType'].str.contains('Contributory|Individually') == False), other=input_df['Number'], inplace=True)
input_df['PropertyType'].where((input_df['PropertyType'].str.contains('Contributory|Individually') == False), other='blank', inplace=True)
# Next line wont work because PropertyId  is now changed. 
#input_df['PropertyType'].where((input_df['PropertyId'].str.contains('Contributory|Individually') == False), other='nope', inplace=True)

# shift (copy) X columns to the right when the Suburb contains the heritage status This only partially fixes 94 rows.
# Need to investigate why these lines don't contain a property id anymore. It was in the Number column when parsed by Tabula.
input_df['EstimatedDate'].where((input_df['Suburb'].str.contains('Contributory|Individually') == False), other=input_df['PropertyType'], inplace=True)
input_df['HeritageStatus'].where((input_df['Suburb'].str.contains('Contributory|Individually') == False), other=input_df['Suburb'], inplace=True)
input_df['PropertyId'].where((input_df['Suburb'].str.contains('Contributory|Individually') == False), other=input_df['Number'], inplace=True)
input_df['PropertyType'].where((input_df['Suburb'].str.contains('Contributory|Individually') == False), other='', inplace=True)
input_df['Suburb'].where((input_df['Suburb'].str.contains('Contributory|Individually') == False), other=input_df['Type'], inplace=True)


#### ---- save the results. ---- ####

output_df = input_df

output_df.to_csv("{}".format(output_filename), mode='w', header=True, index=False, encoding='utf8')
output_count = len(output_df['Overlay'])
print('Cleaned {} lines to {} lines'.format(input_count, output_count))
exit(0)

