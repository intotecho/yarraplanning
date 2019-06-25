# -*- coding: utf-8 -*-
# noqa: E501
"""
merge OriginalAddress from CLEAN into GNAF

Conversion is based on the following article
https://towardsdatascience.com/addressnet-how-to-build-a-robust-street-address-parser-using-a-recurrent-neural-network-518d97b9aebd


"""
import pandas as pd
import logging
import column_defs as cd


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
gnaf_filename = "yarra_heritage_register_C191_GNAF.csv"
output_filename = "yarra_heritage_register_C191_GNAF2.csv"
#output_filename = "test_register_GNAF.csv"


#------------------ CONFIGURATION -------------------------------

# Specify the column name in your input data that contains addresses here.
input_address_column_name = "NormalAddress"

register_cols = [
    'Overlay',	'AddressName',	'Type',	'Number',	'Suburb',
    'PropertyType',	'PropertyId',	'HeritageStatus',
    'EstimatedDate', 'OriginalAddress', 'NormalAddress'
]

# ------------------ DATA LOADING --------------------------------

# ---- save the results. ---- #


def save_results(df, filename=output_filename):
    df.to_csv("{}".format(
        filename),
        mode='w',
        header=True,
        index=False,
        encoding='utf8')


register_columns = cd.register_columns_gnaf
register_dtypes = cd.register_dtypes_gnaf

print('open files')
# Read the input data to a Pandas Dataframe
try:
    df = pd.read_csv(
        input_filename,
        usecols=['NormalAddress', 'OriginalAddress'],
        encoding='utf8'
       )
except Exception as e:
    logger.error("Input File Not Found. Exception {} ".format(e))
    exit()
if 'OriginalAddress' not in df.columns:
    raise ValueError("Missing OriginalAddress column in input data")

#input_count = len(df['OriginalAddress'])

print('2')

# --- Read the output file already processed ---
try:
    df_done = pd.read_csv(
        gnaf_filename,
        #dtype=register_dtypes,
        #usecols=register_columns,
        #low_memory=False,
        encoding='utf8'
       )

    if 'Overlay' not in df_done.columns:
        print('Output file is empty, starting from scratch')
        exit(-1)
except Exception as e:
    logger.error("Output File Not Found. Starting from Scratch {} ".format(e))
    exit(-1)

print(df_done.head())
print(df_done.columns)
print(df.columns)
print(df.shape)
#print(df.head())
#print(df['NormalAddress'])
del df_done['OriginalAddress']

df = df.drop_duplicates()
df_done = df_done.drop_duplicates()

result = pd.merge(df_done,
                  df,
                  how='left',
                  on='NormalAddress',
                  copy=True)
print('result')

result = result.drop_duplicates()

save_results(result)

delta = result[result['NormalAddress'] != result['OriginalAddress']]
summary = delta[['NormalAddress', 'OriginalAddress']].copy()
save_results(summary, 'changed_addresses.csv')

print(summary)
print(df.shape, df_done.shape, result.shape, summary.shape)
exit(1)
