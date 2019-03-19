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

#Convert all â€™ symbols to apostrophe
input_df['Overlay']= (input_df['Overlay'].str.replace(u'â€™', "\'"))
input_df['PropertyType']= (input_df['PropertyType'].str.replace(u'â€™', "\'"))
input_df['AddressName']= (input_df['AddressName'].str.replace(u'â€™', "\'"))

# Remove blank lines - WARNING - Only do this after merged multiline entries
input_df['Overlay'].replace('', np.nan, inplace=True)
input_df.dropna(subset=['Overlay'], inplace=True)

#selection = input_df.loc[(input_df['Overlay'].str.len() > 6)] 
#output_df = selection


#output_df = input_df.apply(shiftAddress, axis=0)
#output_df = input_df[['Suburb']].apply(lambda x: x if row['Overlay'].str.len() <= 5 else row['Number'], axis=0)


#input_df['Overlay'].where(input_df['Overlay'].str.len() <= 5, other=input_df['Overlay'].str[0:len(re.match(r'HO[\d]*', input_df['Overlay']).group(0))-1], inplace=True)

# shift (copy) three columns to the right when the Overlay string is too long.
input_df['Number'].where(input_df['Overlay'].str.len() <= 5, other=input_df['Type'], inplace=True)
input_df['Type'].where(input_df['Overlay'].str.len() <= 5, other=input_df['AddressName'], inplace=True)
input_df['AddressName'].where(input_df['Overlay'].str.len() <= 5, other=input_df['Overlay'], inplace=True)
#input_df['Overlay'].where(input_df['Overlay'].str.len() <= 5, other=input_df['Overlay'].str[0:len(re.match(r'HO[\d]*', input_df['Overlay']).group(0))-1], inplace=True)



# Add a dummy column to simplfy the code. Its the length of the name of the overlay H01 or HO12 or HO123
#pattern = re.compile("HO[\d]*")
#input_df['NotHOlen'] = input_df['Overlay'].str[input_df['HOlen'].str.len()-1:]
#input_df['NotHOlen'] = input_df['Overlay'].str[input_df['HOlen'].str.len()-1:]

#input_df['HOlen'] = input_df['Overlay'].str.extract(r'(HO[\d]*)', expand=False)

input_df['HOlen'] = input_df['Overlay'].str.split(pat=r'(HO[\d]*)', n=1, expand=False)
test_df = input_df['Overlay'].str.split(pat=r'(HO[\d]*)', n=1, expand=True)
#input_df['AddressName'] = test_df[2]
input_df['AddressName'].where(input_df['Overlay'].str.len() <= 5, other=test_df[], inplace=True)
input_df['Overlay'] = test_df[1]

#input_df['Overlay'].where(len(input_df['HOlen'].tolist()) < 1, other=input_df['HOlen'][1], inplace=True)
#input_df['Overlay'].where(input_df['Overlay'].str.len() <= 5, other=input_df['HOlen'][1], inplace=True)

# Find rows where the Overlay and AddressName are merged  
#mask = (input_df['Overlay'].str.len() > 5)
#lines_to_fix  = input_df.loc[mask].apply



output_df = input_df

# output the results.
output_df.to_csv("{}".format(output_filename), mode='w', header=True, index=False, encoding='utf8')

output_count = len(output_df['Overlay'])

print('Cleaned {} lines to {} lines'.format(input_count, output_count))
exit()

'''
def shiftAddress(x):
    print(x['Suburb'])
    if  x['Overlay'].str.len() > 5:
        x['Suburb'] = x['Number'] 
        x['Number'] = x['Type'] 
        x['Type'] = x['AddressName'] 
        x['AddressName'] = x['AddressName'].str.slice(0, 5) 

df.apply({
          'AddressName':shiftAddressName,
          'Type':shiftPropertType, 
          'Number':shiftAddressName, 
          'Suburb': shiftSuburb
          }, axis=0)
'''
