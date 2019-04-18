# -*- coding: utf-8 -*-
# noqa: E501
"""
The Yarra Heritage Register is recorded in the document  PDF file
Review Of Heritage Overlay Areas 2007 Appendix 8 Revised May 2017.pdf
This reference doc in the planning scheme is ammended from time to time
but only when there is a planning scheme amendment.

The link moves, and was last seen at:
https://www.yarracity.vic.gov.au/the-area/planning-for-yarras-future/yarra-planning-scheme-and-amendments/incorporated-documents
https://www.yarracity.vic.gov.au/-/media/files/planning-scheme-amendments/amendment-c231/am-c231--september--appendix-8.pdf?la=en&hash=F7D784016EBAF0750310399CCCDCE29D30A5B1C2

This file can be processed into a CSV table by Tabula.
https://github.com/tabulapdf/tabula
However there are a number of issues process the file, leading to
1. Records with multiline text being  split over several rows of the CSV.
   These need to be detected and merged.
2. Records where multiple fields and merged into one field
   so all the remaining fields are shifted.
3. Headings and blank rows.

The objective of this script is to correct as manu errors as possible
so that the output is ready for uploading to BigQuery or other databases.

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


# ------------------ CONFIGURATION -------------------------------

# Set your input file here
# e.g. "revew_of_heritage_overlay_areas_2007_rev_may_2017.csv"
input_filename = "tabula_yarra_heritage_database_c191_Jan2019.csv"
# Set your output file name here.
output_filename = "yarra_heritage_register_C191_auto.csv"

# Specify the columns we wish to read from the apps file. We want them all.
register_columns_in = [
    'Overlay', 'Address', 'Type',	'Number', 'Suburb',
    'Property Type', 'Property No.', 'Heritage Status',
    'Estimated Date', 'Overflow']

suburbs = [
    'Abbotsford',
    'Alphington',
    'Burney',
    'Burnley',
    'Collingwood',
    'Cremorne',
    'Fairfield',
    'Fitzroy',
    'Fitzroy North',
    'Fitzroy-Collingwood',
    'Clifton Hill',
    'Carlon North',
    'Princes Hill',
    'Richmond',
    'Yarra Bend',
    '(west) Clifton Hill'
    ]


# Reference DataFrame of Street Types and their Abreviations.
streetTypde_df = pd.DataFrame({
    'street_types': [
        'Avenue',
        'Boulevard',
        'Court',
        'Crescent',
        'Crofts',
        'Drive',
        'Esplanade',
        'Grove',
        'Highway',
        'Lane',
        'Parade',
        'Place',
        'Road',
        'Street',
        'Terrace',
        'Vaucluse',
        'Way'],
    'street_abbr': [
        'Ave',
        'Bvd',
        'Ct',
        'Cres',  # Sometimes Prefixed with 'The' in Applications
        'Crofts',
        'Drive',
        'Esplanade',  # Sometimes Prefixed with 'The' in Applications
        'Gr',
        'Hwy',
        'Lane',  # Once abbreviated to 'Ln' in Buckhurst,  usually 'Lane'
        'Pde',
        'Pl',
        'Rd',
        'St',
        'Tce',
        'Vaucluse',  # Sometimes Prefixed with 'The' in Applications
        'Way']
    })


'''
StreetTypeinRegister	Abbr	Comments
Crescent	Cres	Prefix with 'The'
Esplanade	Esplanade	Prefix with 'The'
Vaucluse	Vaucluse	Prefix with 'The'
Lane	Lane	Ln used once for Buckhurst Ln
'''


''' Need to fix this
Abinger
Street
null
Richmond
Malt House (Former)
194930
Individually Significant
1880-1890
Jan-24 Abinger St Richmond
'''


# ------------------ DATA LOADING --------------------------------

# Read the input data to a Pandas Dataframe
try:
    input_df = pd.read_csv(
        input_filename,
        encoding='utf8',
        usecols=register_columns_in)
except Exception as e:
    logger.error("Input File Not Found. Exception {} ".format(e))
    exit()
if 'Overlay' not in input_df.columns:
    raise ValueError("Missing Address column in input data")

# Rename columns to be BigQuery compatible
# You have to add a column heading for 'Overflow' manually to the input file.
input_df.columns = [
    'Overlay', 'AddressName', 'Type', 'Number', 'Suburb',   'PropertyType',
    'PropertyId', 'HeritageStatus', 'EstimatedDate', 'Overflow']

input_count = len(input_df['Overlay'])

'''
#Convert all â€™ symbols to apostrophe if needed.
input_df['Overlay']= (input_df['Overlay'].str.replace(u'â€™', "\'"))
input_df['PropertyType']= (input_df['PropertyType'].str.replace(u'â€™', "\'"))
input_df['AddressName']= (input_df['AddressName'].str.replace(u'â€™', "\'"))
'''
# There are some rows which are completely empty so drop them first.
input_df.dropna(how='all', inplace=True)

'''
# Mege multiline entries to a single row.
# If Overlay on row N-1 is blank and Overlay on row N+2 is also blank,
# then row N contains a record that needs to merge in some fields from the row
# above and below. First step is to create a splitlines column that is only
# empty when both the row above and below have no Overlay.
# Create a new column that concatenates the overlay from the line above
# and the line below. If this is blank, we have a split row.
# upper_blanklines are rows above a splitline, lower_blanklines are rows below.
# both upper and lower can be deleted once their data has been merged.
'''
input_df['splitlines'] = input_df['Overlay'].shift(axis=0, periods=-1)
input_df = input_df.replace(np.nan, '', regex=True)
input_df['splitlines'] = \
    input_df['splitlines'].str.cat(input_df['Overlay'].shift(
        axis=0,
        periods=1))

input_df['upper_blanklines'] = input_df['splitlines'].shift(axis=0, periods=1)
input_df['lower_blanklines'] = input_df['splitlines'].shift(axis=0, periods=-1)


def mergspliterows(df, column):
    '''
    '''
    df[column].where(
        ((df['splitlines'].str.len() != 0) | (df[column].str.len() != 0)),
        other=df[column].shift(axis=0, periods=1).str.cat(df[column].shift(
            axis=0,
            periods=-1)),
        inplace=True)
    return df


def deletespliterows(df):
    '''
    # if splitlines is empty drop the row above and the row below
    #df = df.drop(df['upper_blanklines'], axis=0)
    #df = df.drop(df['lower_blanklines'], axis=0)
    '''
    df = df[df['upper_blanklines'].str.len() != 0]
    df = df[df['lower_blanklines'].str.len() != 0]
    return df


# for each split row, if the Number is also blank then combine Number
# from the row above concatenated with the Nu,ber from row below.
# do the same for PropertyType and Type
input_df = mergspliterows(input_df, 'Number')
input_df = mergspliterows(input_df, 'PropertyType')
input_df = mergspliterows(input_df, 'Type')

input_df = deletespliterows(input_df)

# Remove temporary columns
input_df.drop(['splitlines'], axis=1, inplace=True)
input_df.drop(['upper_blanklines'], axis=1,  inplace=True)
input_df.drop(['lower_blanklines'], axis=1,  inplace=True)

# Remove blank lines - WARNING - Only do this after merged multiline entries
input_df['Overlay'].replace('', np.nan, inplace=True)
input_df.dropna(subset=['Overlay'], how='all', inplace=True)
# Remove rows for which all of the below columns contain blank values.
# Note that AddressName is not included in this list.
# Still delete lines that only contain an Overlay and AddressName
# These lines are like 'HO309, - Barkly Gardens Precinct, Richmond,,,,,,;
# i.e. they describe the precinct name only, not a place. So can be dropped.
input_df = input_df[
                     (input_df['Type'].str.len() != 0) |
                     (input_df['Number'].str.len() != 0) |
                     (input_df['Suburb'].str.len() != 0) |
                     (input_df['PropertyType'].str.len() != 0) |
                     (input_df['PropertyId'].str.len() != 0) |
                     (input_df['HeritageStatus'].str.len() != 0) |
                     (input_df['EstimatedDate'].str.len() != 0)
                     ]


def copycol(df, from_field, to_field, cond):
    df[to_field].where(cond, other=df[from_field], inplace=True)
    df[from_field].where(cond, other='', inplace=True)
    return df


# --  When the PropertyID contains a HeritageStatus.
input_df['keycolumn'] = input_df['PropertyId'].copy()
condition = (
    input_df['keycolumn'].
    str.contains('Contributory|Individually|Register', case=False) == 0)
copycol(input_df, 'HeritageStatus', 'EstimatedDate', condition)
copycol(input_df, 'PropertyId', 'HeritageStatus', condition)
copycol(input_df, 'PropertyType', 'PropertyId', condition)

# --  When the PropertyType contains a HeritageStatus.
input_df['keycolumn'] = input_df['PropertyType'].copy()
condition = (
    input_df['keycolumn'].
    str.contains('Contributory|Individually|Register', case=False) == 0)
copycol(input_df, 'PropertyId', 'EstimatedDate', condition)
copycol(input_df, 'PropertyType', 'HeritageStatus', condition)
copycol(input_df, 'Suburb', 'PropertyId', condition)
copycol(input_df, 'Number', 'PropertyType', condition)


'''
A little diagnostic to see which step caused a change to the matching row
logger.debug('2 - {}'.format(input_df.loc[input_df['Test'] == 'MATCH']))
'''

# --  When the Suburb contains a HeritageStatus.
input_df['keycolumn'] = input_df['Suburb'].copy()
condition = (
    input_df['keycolumn'].
    str.contains('Contributory|Individually|Register', case=False) == 0)

copycol(input_df, 'PropertyType', 'EstimatedDate', condition)
copycol(input_df, 'Suburb', 'HeritageStatus', condition)
copycol(input_df, 'Number', 'PropertyId', condition)
copycol(input_df, 'Type', 'PropertyType', condition)
copycol(input_df, 'AddressName', 'Suburb', condition)


# --  When Number contains a Suburb
input_df['keycolumn'] = input_df['Number'].copy()
condition = (
    input_df['keycolumn'].
    str.contains('|'.join(suburbs), regex=False) == 0)
copycol(input_df, 'Number', 'Suburb', condition)
copycol(input_df, 'Type', 'Number', condition)


# --  When EstimateDate contains a HeritageStatus. (Shifted other way)
input_df['keycolumn'] = input_df['EstimatedDate'].copy()
condition = (
    input_df['keycolumn'].
    str.contains('Contributory|Individually|Register', case=False) == 0)
copycol(input_df, 'HeritageStatus', 'PropertyId', condition)
copycol(input_df, 'EstimatedDate', 'HeritageStatus', condition)
copycol(input_df, 'Overflow', 'EstimatedDate', condition)

# --  When AddressName contains a StreetType it's OK
input_df['keycolumn'] = input_df['AddressName'].copy()
street_types = streetTypde_df['street_types']
condition = (
    input_df['keycolumn'].
    str.contains('|'.join(street_types), regex=False) == 0)
copycol(input_df, 'Number', 'Suburb', condition)
copycol(input_df, 'Type', 'Number', condition)

# --When AddressName contains a Street Type and Suburb is blank.
input_df['keycolumn'] = input_df['AddressName'].copy()
condition = (
    (input_df['keycolumn'].
        str.contains('|'.join(street_types)) == 0) |
    (input_df['Suburb'].str.len() > 0))
copycol(input_df, 'Number', 'Suburb', condition)
copycol(input_df, 'Type', 'Number', condition)
copycol(input_df, 'AddressName', 'Type', condition)

# logger.debug('2 - {}'.format(input_df.loc[input_df['Test'] == 'MATCH']))

# --  When AddressName is a StreetType & both Suburb and Number are not blank
input_df['keycolumn'] = input_df['AddressName'].copy()
condition = (
    (input_df['keycolumn'].
        str.contains('|'.join(street_types)) == 0) |
    (input_df['Suburb'].str.len() == 0) |
    (input_df['Number'].str.len() > 0))
# Only want to copy suburb if blank.
copycol(input_df, 'Type', 'Number', condition)
copycol(input_df, 'AddressName', 'Type', condition)

# logger.debug('7 - {}'.format(input_df.loc[input_df['Test'] == 'MATCH']))

# --  When AddressName contains a StreetType, Suburb is not blank but Number is
input_df['keycolumn'] = input_df['AddressName'].copy()
condition = (
    (input_df['keycolumn'].
        str.contains('|'.join(street_types)) == 0) |
    (input_df['Suburb'].str.len() == 0) |
    (input_df['Number'].str.len() == 0))
# Only want to copy suburb if blank.
copycol(input_df, 'AddressName', 'Type', condition)

# --  When Suburb is blank and PropertyType is not blank, Copy PropertyType to Suburb
input_df['keycolumn'] = input_df['Suburb'].copy()
condition = (
    (input_df['Suburb'].str.len() != 0) |
    (input_df['PropertyType'].str.len() == 0))
# Only want to copy suburb if blank.
copycol(input_df, 'PropertyType', 'Suburb', condition)

# logger.debug('8 - {}'.format(input_df.loc[input_df['Test'] == 'MATCH']))

# If AddressName is a number, copy Type to Suburb and AddressName to Number.
# Type is in Overlay
input_df['keycolumn'] = input_df['AddressName'].copy()
condition = (
    (input_df['keycolumn'].
        str.isnumeric() == 0))
# Only want to copy suburb if blank.
copycol(input_df, 'Type', 'Suburb', condition)
copycol(input_df, 'AddressName', 'Number', condition)

# logger.debug('9 - {}'.format(input_df.loc[input_df['Test'] == 'MATCH']))

'''
# --- SPLIT AND PROCESS OVERLAY  ----
'''
# If Overlay is longer than HOxxx, split it into sub strings.
# new df splits Overlay into two strings ['HO123', 'and the rest']
overlay_df = input_df['Overlay'].str.split(
    pat=r'(HO[\d]*)|(Street)|(Avenue)',
    n=2,
    expand=True)

overlay_df.columns = [
    'unused', 'overlaykey', 'b1', 'b2', 'addressname',
    'b4', 'is_street', 'is_avenue', 'addrnumber']
overlay_df['addressname'] = overlay_df['addressname'].str.strip()
# Write this new overlay dataframe for diagnostics.
overlay_df.to_csv(
    "{}".format("splits.csv"),
    mode='w', header=True, index=False, encoding='utf8')


def merge_in(input_df, overlay_df, from_field, to_field):
    # Copy from overlay_df to input_df if the condition is false.
    # ie. if from_field is not blank and to field is blank.
    condition = ((overlay_df[from_field].str.len() == 0) |
                 (input_df[to_field].str.len() > 0))
    input_df[to_field].where(
        condition,
        other=overlay_df[from_field],
        inplace=True)
    return input_df


# logger.debug('10 - {}'.format(input_df.loc[input_df['Test'] == 'MATCH']))

merge_in(input_df, overlay_df, 'addressname', 'AddressName')
merge_in(input_df, overlay_df, 'is_street', 'Type')
merge_in(input_df, overlay_df, 'is_avenue', 'Type')
merge_in(input_df, overlay_df, 'addrnumber', 'Number')
# Replace the overlay key column
input_df['Overlay'] = overlay_df['overlaykey']

# logger.debug('11 - {}'.format(input_df.loc[input_df['Test'] == 'MATCH']))

# tidy up
input_df.drop(['Overflow'], axis=1,  inplace=True)
input_df.drop(['keycolumn'], axis=1,  inplace=True)

# Update HeritageStatus when case is incorrect.
# This was fixed in C191 and made consistent.
'''
input_df['Number'] = input_df['Number'].str.replace(
     r'[Ii]ndividually [Ss]ignificant', 'Individually significant', regex=True)

input_df['Number'] = input_df['Number'].str.replace(
     r'Victorian Heritage register', 'Victorian Heritage Register', regex=True)
'''


# --- Fix street Numbers when converted to date buy Tabula ---
# First converts 'Jan-13' to '1/13', then '13-Jan' to '13/1'.
def fixdate(df, column, month, number):
    df[column] = df[column].str.replace(
            r"(.*)\-{}".format(month),
            "\\1/{}".format(number))
    df[column] = df[column].str.replace(
                r"{}\-(.*)".format(month),
                "{}/\\1".format(number))
    return df


fixdate(input_df, 'Number', 'Jan', 1)
fixdate(input_df, 'Number', 'Feb', 2)
fixdate(input_df, 'Number', 'Mar', 3)
fixdate(input_df, 'Number', 'Apr', 4)
fixdate(input_df, 'Number', 'May', 5)
fixdate(input_df, 'Number', 'Jun', 6)
fixdate(input_df, 'Number', 'Jul', 7)
fixdate(input_df, 'Number', 'Aug', 8)
fixdate(input_df, 'Number', 'Sep', 9)
fixdate(input_df, 'Number', 'Oct', 10)
fixdate(input_df, 'Number', 'Nov', 11)
fixdate(input_df, 'Number', 'Dec', 12)

# Normalise the (Unit n) to VicData address
input_df['Number'] = input_df['Number'].str.replace(
            r"(.*)( \()(Unit ?)(\d*)(\))",
            "\\4/\\1",
            regex=True)


# Insert 'Street' when missing for Johnston Street HO505
condition = (
    (input_df['Type'].str.match("")) |
    (input_df['AddressName'].str.match("Johnston")))
input_df['Type'].where(condition, other="Street", inplace=True)

# Make a new normalised address field.
# This fomrat matches VicData addresses except for the postcode we don't have.

input_df['NormalAddress'] = \
    input_df['Number'] \
    + ' ' + input_df['AddressName'].str.upper() \
    + ' ' + input_df['Type'].str.upper() \
    + ' ' + input_df['Suburb'].str.upper()

# Remove some of the spurious descriptions [part|tower|rear|sign|mural]
regex = re.compile(
  r'(.*)( \()(part|under|near|tower|rear|sign|mural|west|hall|northern|Ground ?Floor|First ?Floor)(\))(.*)'
)
input_df['NormalAddress'] = input_df['NormalAddress'].str.replace(
    regex,
    "\\1\\5",
    regex=True)


# Change '341 part (341-347) Fitzroy' to '341-347 FITZROY'
regex = re.compile(
  r'(.*)(\d*)( part ? ?\()(.*)(\))(.*)'
)
input_df['NormalAddress'] = input_df['NormalAddress'].str.replace(
    regex,
    "\\4\\6",
    regex=True)


# Remove some of the spurious descriptions [part|tower|rear|sign|mural]
input_df['NormalAddress'] = input_df['NormalAddress'].str.replace(
            r'(.*)(\()(WEST)(\))(.*)',
            "\\1\\5",
            regex=True)
# '-oonah' got converted by excel to '#NAME".
input_df['PropertyType'] = input_df['PropertyType'].str.replace(
            r'(\#NAME\?)',
            "Oonah",
            regex=True)

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
