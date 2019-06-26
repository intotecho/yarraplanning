# -*- coding: utf-8 -*-

"""
Match (Join) addresses in the heritage register with VicMap Address data
See README.md for more info
See column_defs.py for attributes info
"""
import pandas as pd
import logging
import re
import math
import column_defs as cd
import numpy as np
import time

logger = logging.getLogger("root")
logger.setLevel(logging.INFO)
# create console handler
ch = logging.StreamHandler()
#ch.setLevel(logging.DEBUG)
logger.addHandler(ch)
# ------------------ CONFIGURATION -------------------------------

# Set your input file
register_input = "yarra_heritage_register_C191_GNAF2.csv"  # output of register_2gnaf.py  # noqa: E501

addresses_input = "addresses_in_yarra_LGA376.csv"  # from VicMap Spatial Data Mart, filtered to LGA  # noqa: E501

#vhd_input = "../scrape_vhd/yarra_vhd-20190517.csv"  # from VicMap Spatial Data Mart, filtered to LGA  # noqa: E501
vhd_input = "VHD_YARRA_GNAF.csv"  # from VicMap Spatial Data Mart, filtered to LGA  # noqa: E501

# Set your output file name here.
register_output = "{}_MATCHED.csv".format(register_input)
addresses_output = "{}_MATCHED.csv".format(addresses_input)
map_file = "address_map.csv"
prematched_address = "prematched_addresses.csv"

map_columns = cd.map_columns
register_dtypes = cd.register_dtypes_gnaf
vicmap_address_attribs = cd.vicmap_address_attribs

vhd_dtypes = dict()
vhd_dtypes.update(cd.vhd_dtypes) # columns output of scrape_vhd.py
vhd_dtypes.update(cd.gnaf_output_dtypes) #columns output of vhd_2gnaf.py

# ---- save the results. ---- #
def save_results(df, filename):
    logging.debug('Saving: {}'.format(filename))
    df.to_csv("{}".format(
        filename),
        mode='w',
        header=True,
        index=False,
        encoding='utf8')

'''
open_file() will try to open the checkpoint file, otherwise will open the original file.  # noqa: E501
  @filetype: one of 'register' or 'addresses'
  @check_column is used to check the file has sane data.
  returns a dataframe or exits on fatal error.
'''

def open_file(filetype, check_column):
    logger.info('open {}'.format(filetype))
    columns = (register_dtypes if filetype == 'register' else vicmap_address_attribs)
    try:
        df = pd.read_csv(
            register_output if filetype == 'register' else addresses_output,
            dtype=columns,
            encoding='utf8'
        )
        if check_column in df.columns:
            return df
        else:
            logger.warning('{} output file not formatted!'.format(filetype))
    except Exception as e:
        logger.warning(
            "{} output File Not Found!".
            format(filetype))
    logger.info('Starting address matching from scratch')
    try:
        if filetype == 'register':
            columns.pop('OriginalAddress')
            columns.pop('Matched')
            columns.pop('VHDMatched')
            columns.pop('EZI_ADD')
            columns.pop('PROPERTY_PFI')
            columns.pop('geom')
            columns.pop('vhdplaceid')
        else:
            columns.pop('MatchCount')
        df = pd.read_csv(
            register_input if filetype == 'register' else addresses_input,
            dtype=columns,
            encoding='utf8'
        )
        # Add checkpoint columns to new frames and init new columns
        if check_column in df.columns:
            if filetype == 'register':
                df['OriginalAddress'] = df['NormalAddress']
                df['Matched'] = ""
                df['VHDMatched'] = ""
                df['EZI_ADD'] = ""
                df['PROPERTY_PFI'] = ""
                df['geom'] = ""
                df['vhdplaceid'] = ""
                logger.debug('added columns', df.columns)
            return df
        else:
            logger.error('Input {} is not not formatted.'.format(filetype))
    except Exception as e:
        logger.error('Input {}  not found. {}'.format(filetype, e))
    exit(1)


def open_map():
    try:
        df = pd.read_csv(
            map_file,
            dtype=map_columns,
            usecols=['RegisterAddress', 'RegularAddress', 'Comments'],
            encoding='utf8'
        )
        # Add checkpoint columns to new frames and init new columns
        if df is None:
            logger.warning("Address Map File not read: {}".format(map_file))
            logger.debug(df)
        return df
    except Exception as e:
        logger.warning('Map File not found. {}'.format(e))
        return None


def open_vhd():
    try:
        df = pd.read_csv(
            vhd_input,
            dtype=vhd_dtypes,
            encoding='utf8'
        )
        # Add checkpoint columns to new frames and init new columns
        if df is None:
            logger.warning("VHD addresses read error: {}".format(vhd_input))
            logger.debug(df)
        return df
    except Exception as e:
        logger.warning('Open VHD exception: {}'.format(e))
        return None


# ------------------ DATA LOADING --------------------------------
start_time = time.time()

# Read the addresss_map data to a Pandas Dataframe
m = open_map()
if m is None:
    logger.info("Address Map File not read: {}".format(map_file))
else:
     logger.warning('Loaded Map File with {} entries. {}'.format(m.size, m.columns))

# Read the input register data to a Pandas Dataframe
r = open_file('register', 'Overlay')


# Read the input address data to a Pandas Dataframe
a = open_file('addresses', 'EZI_ADD')

v = open_vhd()
if v is None:
    logger.info("No VHD read: {}".format(vhd_input))
    exit(-1)
else:
     logger.info('Loaded VHD  with {} entries. {}'.format(v.size, v.columns))

# ---- FILTER ROWS ----------------
# Filter out rows that were not read or cleaned well and cause problems.
# r = r.loc[r['Overlay'] == 'HO452']  # Address in address_map?
r = r.dropna(subset=['AddressName', 'Suburb'])  
# pd.set_option('display.max_columns', 20)
# print (r)
# exit()

# ------------------ INITIALIZE --------------------------------

register_count = len(r['Overlay'])
matched_count = register_count - len(r[r['Matched'] == ''])
if matched_count == 0:
    a['EZI_MATCH'] = a['EZI_ADD'].str.replace(r'^(.*) (\d{4})$', '\\1', regex=True)  # noqa: E501
logger.info('So far matched {} of {}\n'.format(matched_count, register_count))


# ------------------ MATCH ADDRESS   --------------------------------


def testmatch(mask, row):
    if row['Matched'] == np.isnan:
        row['Matched'] = ''
    if not mask.empty:
        matchcount = len(mask['EZI_ADD'])
        if matchcount == 1:
            row['Matched'] += 'Full'
            row['EZI_ADD'] = mask['EZI_ADD'].values[0]  # collect the postcode.
            row['PROPERTY_PFI'] = mask['PR_PFI'].values
            row['geom'] = mask['geom'].values[0]
            logger.debug('Found one match!')
        else:
            row['Matched'] += 'Multiple'
            row['EZI_ADD'] = mask['EZI_ADD'].values[0]  # collect the postcode.
            row['PROPERTY_PFI'] = mask['PR_PFI'].values
            row['geom'] = mask['geom'].values
            logger.debug('\n!Multiple ({}) matches found for: {}'.format(matchcount, row['NormalAddress']))  # noqa: E501
        return True
    else:
        return False

def to_int(string, name):
    try:
        f = float(string)
        if not math.isnan(f):
            number = int(f)
            return number
    except Exception as e:
        logger.debug('Could not convert {}={} to number:\nException {}'.format(name, string, e))
        return -1


def fullmatch(i, row, r, a):
    address = ' '.join(row['NormalAddress'].split())  # Remove multiple spaces.
    road_type = str(row['Type']).upper()
    road_name = str(row['AddressName']).upper()
    locality = str(row['Suburb']).upper()
    if 'ESPLANADE' in address:
        road_type = None
        road_name = 'THE ESPLANADE'
        logger.info('Adjusting for The Esplanade')
    if road_name == 'APPERLY':
        road_name = 'APPERLEY'
        logger.info('Adjusting APPERLY STREET to APPERLEY')
    if road_name == 'ABBOT':
        road_name = 'ABBOTT'
        logger.info('Adjusting ABBOT STREET to ABBOTT')

    # === Map Address for Outliers === #
    mapmask = m.loc[m['RegisterAddress'] == address]  # Address in address_map?
    if not mapmask.empty:
        matchcount = len(mapmask['RegisterAddress'])
        if matchcount == 1:
            mapped_address = mapmask['RegularAddress'].values[0]  # Swap it
            address = ' '.join(mapped_address.split())  # Remove spaces.
            row['Matched'] = 'Mapped'
            logger.info('MAPPING to {}'.format(address))
            if address == 'NotExist':
                row['Matched'] = address  # This address has been checked and is non-existent
                return False
        # After mapping, can only match on the mapped address directly
        matchingstreet = a.loc[a['EZI_MATCH'] == address]
    else:
        # Match on these candidates in the same street
        matchingstreet = a.loc[(a['ROAD_NAME'] == road_name) & (a['ROAD_TYPE'] == road_type) & (a['LOCALITY'] == locality)]  # noqa: E501

    # print(row['AddressName'], row['Type'], row['Suburb'])
    # if row['Matched'] == 'Mapped':
    #    logger.info(address)
    #    logger.info(matchingstreet)

    if matchingstreet.empty:
        #logger.warning('No matching street found! {}. Trying suburb swaps'.format(address))
        #print("\n\nNotAnAddress {}".format(address))
        #print("\n\nRowMatched {}".format(row['Matched']))
        row['Matched'] += 'NotAnAddress'
        matchingstreet = a.loc[a['EZI_MATCH'] == address]
    else:
        mask = matchingstreet.loc[matchingstreet['EZI_MATCH'] == address]
        if testmatch(mask, row):
            return True
    # === TRY FULL MATCH === #


# === TRY FULL MATCH WITH SWAPPED SUBURB (Richmond -> Cremorne or Burnley -> Richmond ===  # noqa: E501
    if locality == 'RICHMOND':
        swap_locality = 'CREMORNE'
        swap_address = address.replace(r'RICHMOND', 'CREMORNE')
        matchingstreet_swap = a.loc[(a['ROAD_NAME'] == road_name) & (a['ROAD_TYPE'] == road_type) & (a['LOCALITY'] == swap_locality)]  # noqa: E501
        mask = matchingstreet_swap.loc[matchingstreet_swap['EZI_MATCH'] == swap_address]  # noqa: E501
        if testmatch(mask, row):
            row['Matched'] += 'SwapSuburb'
            return True
        locality = 'BURNLEY'
        swap_address = re.sub(r'RICHMOND$', 'BURNLEY', address)
        matchingstreet_swap = a.loc[(a['ROAD_NAME'] == road_name) & (a['ROAD_TYPE'] == road_type) & (a['LOCALITY'] == swap_locality)]  # noqa: E501
        mask = matchingstreet_swap.loc[matchingstreet_swap['EZI_MATCH'] == swap_address]  # noqa: E501
        if testmatch(mask, row):
            row['Matched'] += 'SwapSuburb'
            return True

    elif locality == 'BURNLEY':
        swap_locality = 'RICHMOND'
        swap_address = re.sub(r'BURNLEY$', 'RICHMOND', address)
        matchingstreet_swap = a.loc[(a['ROAD_NAME'] == road_name) & (a['ROAD_TYPE'] == road_type) & (a['LOCALITY'] == swap_locality)]  # noqa: E501
        mask = matchingstreet_swap.loc[matchingstreet_swap['EZI_MATCH'] == swap_address]  # noqa: E501
        if testmatch(mask, row):
            row['Matched'] += 'SwapSuburb'
            return True

    if locality == 'CARLTON NORTH':
        swap_locality = 'PRINCES HILL'
        swap_address = re.sub(r'CARLTON NORTH$', 'PRINCES HILL', address)
        matchingstreet_swap = a.loc[(a['ROAD_NAME'] == road_name) & (a['ROAD_TYPE'] == road_type) & (a['LOCALITY'] == swap_locality)]  # noqa: E501
        mask = matchingstreet_swap.loc[matchingstreet_swap['EZI_MATCH'] == swap_address]  # noqa: E501
        if testmatch(mask, row):
            row['Matched'] += 'SwapSuburb'
            return True

    # === TRY MATCH R.address to first address in range === #
    # 2 HODDLE STREET ABBOTSFORD -> 2-8 HODDLE STREET ABBOTSFORD 3067
    number_first = to_int(row['number_first'], 'number_first')
    if number_first != -1: 
        mask = matchingstreet.loc[(matchingstreet['HSE_NUM1'] == number_first)]
        if testmatch(mask, row):
            row['Matched'] += 'MatchedFirstInRange'
            return True
        # === TRY MATCH R.address to last address in range === #
        # 13 GROSVENOR => 9-13 GROSVENOR 3066
        mask = matchingstreet.loc[(matchingstreet['HSE_NUM2'] == number_first)]
        if testmatch(mask, row):
            row['Matched'] += 'MatchedSecondInRange'
            return True

        # === TRY MATCH First Address in R to A  === #
        # 13-16 GROSVENOR => 13 GROSVENOR 3066
        mask = matchingstreet.loc[(matchingstreet['HSE_NUM1'] == number_first)]
        if testmatch(mask, row):
            row['Matched'] += 'FirstInRangedMatched'
            return True

    # === TRY MATCH A.address to last address in R.range === #
    # 13-16 GROSVENOR => 16 GROSVENOR 3066
    number_last = to_int(row['number_last'], 'number_last')
    if number_last!= -1: 
        mask = matchingstreet.loc[(matchingstreet['HSE_NUM1'] == number_last)]
        if testmatch(mask, row):
            row['Matched'] += 'LastInRangedMatched'
            return True

        # === TRY MATCH A.SECOND address to last address in R.range === #
        # 319-339 GEORGE STREET FITZROY => 317-339 GEORGE STREET FITZROY 3065
        mask = matchingstreet.loc[(matchingstreet['HSE_NUM2'] == number_last)]
        if testmatch(mask, row):
            row['Matched'] += 'RangedInRangeMatched'
            return True

    # === TRY SWAPPING FLAT AND BUILDING ===
    flat_number = to_int(row['flat_number'], 'flat_number')
    if flat_number != -1 and number_first != -1:
        bldg_mask = matchingstreet.loc[(matchingstreet['HSE_NUM1'] == flat_number)]
        if not bldg_mask.empty:
            mask = bldg_mask.loc[(matchingstreet['BUNIT_ID1'] == number_first)]
            if testmatch(mask, row):
                row['Matched'] += 'SwappedFlatAndBuilding'
                # logger.warning('Swapped FlatAndBuilding: {}'.format(address))
                return True
        # === SEE IF FLAT/BUILDING MATCHES A RANGE FLAT-BUILDING ===
            mask = bldg_mask.loc[(matchingstreet['HSE_NUM2'] == number_first)]
            if testmatch(mask, row):
                row['Matched'] += 'ConvertFlatToRange'
                # logger.warning('Converted  Flat/Building to Flat-Building: {}'.format(address))
                return True

    # === GIVE UP NO MATCH FOUND === 
    logger.info('NO EZI_ADD for: {}'.format(address))
    row['Matched'] += 'NoMatch'  # provisional for now
    return

# ------ VHD MATCH -----------------------


def vhdtestmatch(mask, row):
    if row['VHDMatched'] == np.isnan:
        row['VHDMatched'] = ''

    if not mask.empty:
        matchcount = len(mask['vhdplaceid'])
        if matchcount == 1:
            #row['Matched'] += 'VHDS'
            logger.debug('Found one VHD match!')
        else:
            #row['Matched'] += 'VHDM'
            logger.debug('\n!VHD Multiple ({}) matches found for: {}'.format(matchcount, row['OriginalAddress']))  # noqa: E501
        row['vhdplaceid'] = mask['vhdplaceid'].values  # collect all matching VHD places
        return True
    else:
        return False


# use search(), so the match doesn't have to happen 
# at the beginning of "big string"
def vhd_match(i, row, r, a):

    # === TRY FULL MATCH NormalAddress -> Location === #
    address = ' '.join(row['NormalAddress'].split())  # Remove multiple spaces.
    mask = v.loc[v['Location'] == address]
    if vhdtestmatch(mask, row):
        row['VHDMatched'] += 'VHDNF'  # provisional for now
        return True

    # === TRY FULL MATCH EZI_ADD -> Location === #
    ezi_add_with_postcode = row['EZI_ADD']
    removepostcode = re.compile(r'(^.*)( \d{4}$)')
    if ezi_add_with_postcode:
        ezi_add_match = removepostcode.match(ezi_add_with_postcode)
        if ezi_add_match:
            ezi_add = ezi_add_match.group(1)
            mask = v.loc[v['Location'] == ezi_add]
            if vhdtestmatch(mask, row):
                logger.debug('Matched VHD to EZI_ADDRESS: {}'.format(ezi_add))
                row['VHDMatched'] += 'VHDEF'  # provisional for now
                return True
            # === TRY PARTIAL MATCH EZI_ADD -> Location === #
            mask = v.loc[v['Location'].str.contains(ezi_add, regex=True)]
            if vhdtestmatch(mask, row):
                logger.debug('Matched VHD Partial to EZI_ADDRESS: {}'.format(ezi_add))
                row['VHDMatched'] += 'VHDEP'  # provisional for now
                return True
    # === TRY FULL MATCH OriginalAddress -> Location === #
    originalAddress = row['OriginalAddress']
    if originalAddress:
        mask = v.loc[v['Location'] == originalAddress]
        if vhdtestmatch(mask, row):
            logger.debug('Matched VHD to OriginalAddress: {}'.format(originalAddress))
            row['VHDMatched'] += 'VHDOF'  # provisional for now
            return True
        mask = v.loc[v['Location'].str.contains(originalAddress, regex=True)]
        if vhdtestmatch(mask, row):
            logger.debug('Matched VHD Partial to OriginalAddress: {}'.format(originalAddress))
            row['VHDMatched'] += 'VHDOP'  # provisional for now
            return True
    
    # TRY TO MATCH ADDRESS TO FIRST NUMBER IN v.location
    road_type = str(row['Type']).upper()
    road_name = str(row['AddressName']).upper()
    locality = str(row['Suburb']).upper()
    vhd_matchingstreet =  v.loc[(v['street_name'] == road_name) & (v['street_type'] == road_type) & (v['locality_name'] == locality)] 
    
    number_first = to_int(row['number_first'], 'number_first')
    #address = ' '.join(row['NormalAddress'].split())  # Remove multiple spaces.

    if number_first != -1: 
        mask = vhd_matchingstreet.loc[(vhd_matchingstreet['number_first'] == number_first)]
        if testmatch(mask, row):
            row['VHDMatched'] += 'VHDFirstInRange'
            return True
        # === TRY MATCH R.address to last address in range === #
        # 13 GROSVENOR => 9-13 GROSVENOR 3066
        mask = vhd_matchingstreet.loc[(vhd_matchingstreet['number_last'] == number_first)]
        if testmatch(mask, row):
            row['Matched'] += 'MatchedSecondInRange'
            return True

        # === TRY MATCH First Address in R to A  === #
        # 13-16 GROSVENOR => 13 GROSVENOR 3066
        number_last = to_int(row['number_last'], 'number_last')
        mask = vhd_matchingstreet.loc[(vhd_matchingstreet['number_first'] == number_last)]
        if testmatch(mask, row):
            row['Matched'] += 'FirstInRangedMatched'
            return True

    # === GIVE UP NO MATCH FOUND === 
    if str(row['HeritageStatus']).upper() != 'NOT CONTRIBUTORY':
        logger.warning('NO VHD ENTRY FOUND for {} place: {}, {}\n'.format(row['HeritageStatus'], address, row['PropertyType']))
    row['VHDMatched'] += 'VHDN'  # provisional for now
    return False

# ------------------ MAIN LOOP  --------------------------------

SAVE_ROWS = 200
next_batch = 0
start_pt = 0 # matched_count 
if 'VHDMatched' not in r:
    r['VHDMatched'] = ""
for i in range(start_pt, register_count):
    row = r.iloc[i]  # not a copy
    # logger.debug('row', i, 'Matching Address: ', row['NormalAddress'])
    try:
        if (row['Matched'] == 'NoMatch') or (row['Matched'] == ''):
            fullmatch(i, row, r, a)
        if row['vhdplaceid'] == '':
            vhd_match(i, row, r, a)
        if i % SAVE_ROWS == SAVE_ROWS-1:  # save after every Nth row
            logger.info('\nSAVING ROWS {} to {} of {}\n'.format(next_batch, matched_count + i, register_count))  # noqa: E501
            save_results(r, register_output)
            next_batch = i
    except Exception as e:
        logger.error('Exception processing row {}\nException:{}'.format(i, e))
        logger.info('Row {}:\n {}'.format(i, row))
        save_results(r, register_output)
        exit()

logger.info('\nSAVING ROWS {} to {} of {}\n'.format(next_batch, matched_count + i, register_count))  # noqa: E501
save_results(r, register_output)
logger.info('Finished matching addresses after {} seconds'.format(time.time() - start_time))
exit(1)
