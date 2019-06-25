# -*- coding: utf-8 -*-
# noqa: E501
"""
register2gnaf Reads a list of addresses in a DF and decomposes into a GNAF components
{'number_last_suffix': 'B', 
'state': 'VICTORIA', 
'postcode': '3183', 
'number_first': '35', 
'street_type': 'ROAD', 
'number_last': '77', 
'locality_name': 'MOUNT WAVERLEY', 
'building_name': 'CASA DEL GELATO', 
'street_name': 
'HIGH STREET', 
'flat_number': '1'
}

Conversion is based on the following article
https://towardsdatascience.com/addressnet-how-to-build-a-robust-street-address-parser-using-a-recurrent-neural-network-518d97b9aebd

There is a warning that makes it very slow. About one conversion every 7 seconds!
WARNING:tensorflow:Estimator's model_fn (<function model_fn at 0x7f220106f268>) includes params argument, but params are not passed to Estimator.

"""
import pandas as pd
import logging
import sys

if sys.version_info[0] < 3:
    raise Exception("Must be using Python 3. See README.md for setup")

from addressnet.predict import predict_one

logger = logging.getLogger("root")
logger.setLevel(logging.INFO)
# create console handler
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
logger.addHandler(ch)

# ------------------ CONFIGURATION -------------------------------

# Set your input file here
# e.g. "revew_of_heritage_overlay_areas_2007_rev_may_2017.csv"
input_filename = "yarra_heritage_register_C191_CLEAN.csv" # output of clean_register.py
#input_filename = "test_register.csv" # output of clean_register.py

# Set your output file name here.
output_filename = "yarra_heritage_register_C191_GNAF.csv"
#output_filename = "test_register_GNAF.csv"


#------------------ CONFIGURATION -------------------------------

# Specify the column name in your input data that contains addresses here.
input_address_column_name = "NormalAddress"

register_cols = [
    'Overlay',	'AddressName',	'Type',	'Number',	'Suburb',
    'PropertyType',	'PropertyId',	'HeritageStatus',
    'EstimatedDate',	'OriginalAddress', 'NormalAddress'
]
output_cols = [
        'number_last_suffix',
        'state',
        'postcode',
        'number_first',
        'street_type',
        'number_last',
        'locality_name',
        'building_name',
        'street_name',
        'flat_number'
]

# ------------------ DATA LOADING --------------------------------

# ---- save the results. ---- #
def save_results(df):
    df.to_csv("{}".format(
        output_filename),
        mode='w',
        header=True,
        index=False,
        encoding='utf8')

print('open files')
# Read the input data to a Pandas Dataframe
try:
    df = pd.read_csv(
        input_filename,
        encoding='utf8'
       )
except Exception as e:
    logger.error("Input File Not Found. Exception {} ".format(e))
    exit()
if 'Overlay' not in df.columns:
    raise ValueError("Missing Address column in input data")

input_count = len(df['Overlay'])

print('1')

# --- Read the output file already processed ---
try:
    df_done = pd.read_csv(
        output_filename,
        encoding='utf8'
       )
    if 'Overlay' not in df_done.columns:
        print('Output file is empty, starting from scratch')
        output_count = 0
    else:
        output_count = len(df_done['Overlay'])
except Exception as e:
    logger.error("Output File Not Found. Starting from Scratch {} ".format(e))
    output_count = 0

print('read files')

def map_address_components(address):
    #print('predicting for {}'.format(address))
    # model_dir='/home/intotecho/yarraplanning/heritage_register/pretrained/'
    return predict_one(address)

# Add columns (of type string) to the input dataframe
#df.where(df['number_first'] > 1, 10)

if 'number_first' not in df.columns:
    df['number_last_suffix'] = ""
    df['state'] = ""
    df['postcode'] = ""
    df['number_first'] = ""
    df['street_type'] = ""
    df['number_last'] = ""
    df['locality_name'] = ""
    df['building_name'] = ""
    df['street_name'] = ""
    df['flat_number'] = ""

# Pick up where we left off
if output_count == 0:
    new_df = pd.DataFrame(columns=df.columns)
else:
    new_df = df_done

check_counter=output_count
print('start')
for i in range(0, input_count):
    row = df.iloc[i].copy()
    print('{}'.format(i))
    if row['street_name'] == '' and row['street_type'] == '' and row['locality_name'] == '':
        # only call the RNN is we don't already have components of the address
        print('row', i, 'decomposing Address: ', row['NormalAddress'])
        components = map_address_components(row['NormalAddress'])
        for key in components:
            row[key] = components[key]
        new_df = new_df.append(row, ignore_index=True)

        if i % 30 == 0: # save after every Nth row
            # print(row)
            # print(new_df)
            print('Saving rows  {} to {} of {}'.format(check_counter, i, input_count))
            save_results(new_df)
            check_counter = i

print('Saving rows  {} to {} of {}'.format(output_count, i, input_count))
save_results(new_df)
print ('Finished decomposing addresses')
exit(1)
