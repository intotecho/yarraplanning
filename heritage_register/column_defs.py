# -*- coding: utf-8 -*-

"""
Match (Join) addresses in the heritage register with VicMap Address data
See README.md for more info

Address Components are
{
    number_last_suffix,
    state,
    postcode,
    number_first,
    street_type,
    number_last,
    locality_name,
    building_name,
    street_name,
    flat_number,
    number_first_suffix,
    flat_number_suffix
}

Matching Fields
[
    'state', STATE},
    'postcode', POSTCODE},
    'locality_name',LOCALITY},
    'street_name', ROAD_NAME},
    'street_type', ROAD_TYPE },
    'building_name', BUILDING, COMPLEX}
    'number_first', },
    'number_first_suffix', },
    'number_last', },
    'number_last_suffix', },
    'flat_number', },
    'flat_number_suffix', }
]

"""

# ------------------ CONFIGURATION -------------------------------

map_columns = {
    'RegisterAddress': str,
    'RegularAddress': str,
    'Comments': str
}

#=== VHD ===== #
# columns output of scrape_vhd.py

vhd_dtypes = {
    'VHRlng': float,
    'Name': str,
    'vhdplaceid': int,
    'Overlay': str,
    'Authority': str,
    'VHR': str,
    'href': str,
    'Location': str,
    'VHRlat': float,
    'SoSHash': str
}

vhd_columns = {
    'VHRlng',
    'Name',
    'vhdplaceid',
    'Overlay',
    'Image',
    'Municipality',
    'Authority',
    'VHR',
    'href',
    'Location',
    'VHRlat',
    'SoSHash'
}


# ======= ADDRESS_NET 2 GNAF ======= 

# These are the columns that _2gnaf will add.
# example usage: vhd_dtypes = dict()
# vhd_dtypes.update(cd.vhd_dtypes) # columns output of scrape_vhd.py
# vhd_dtypes.update(cd.gnaf_output_dtypes) #columns output of vhd_2gnaf.py

gnaf_output_cols = {
        'number_last_suffix',
        'state',
        'postcode',
        'number_first',
        'street_type',
        'number_last',
        'locality_name',
        'building_name',
        'street_name',
        'flat_number',
        'level_number',
        'level_number_suffix',
        'number_first_prefix',
        'flat_type',
        'flat_number_suffix',
        'number_first_suffix',
        'flat_number_prefix',
        'level_number_prefix',
        'street_suffix',
        'number_last_prefix',
        'level_type'
}

gnaf_output_dtypes = {
    # level_number,level_number_suffix,number_first_prefix,flat_type,flat_number_suffix,number_first_suffix,flat_number_prefix,level_number_prefix,street_suffix,number_last_prefix,level_type
    'number_last_suffix': str,
    'state': str,
    'postcode': str,
    'number_first': str,
    'street_type': str,
    'number_last': str,
    'locality_name': str,
    'building_name': str,
    'street_name': str,
    'flat_number': str,
    'level_number': str,
    'level_number_suffix': str,
    'number_first_prefix': str,
    'flat_type': str,
    'flat_number_suffix': str,
    'number_first_suffix': str,
    'flat_number_prefix': str,
    'level_number_prefix': str,
    'street_suffix': str,
    'number_last_prefix': str,
    'level_type': str,
}

register_dtypes_gnaf = {
    # level_number,level_number_suffix,number_first_prefix,flat_type,flat_number_suffix,number_first_suffix,flat_number_prefix,level_number_prefix,street_suffix,number_last_prefix,level_type
    'Overlay': str,
    'AddressName': str,
    'Type': str,
    'Number': str,
    'Suburb': str,
    'PropertyType': str,
    'PropertyId': str,
    'HeritageStatus': str,
    'EstimatedDate': str,
    'NormalAddress': str,
    'number_last_suffix': str,
    'state': str,
    'postcode': str,
    'number_first': str,
    'street_type': str,
    'number_last': str,
    'locality_name': str,
    'building_name': str,
    'street_name': str,
    'flat_number': str,
    'level_number': str,
    'level_number_suffix': str,
    'number_first_prefix': str,
    'flat_type': str,
    'flat_number_suffix': str,
    'number_first_suffix': str,
    'flat_number_prefix': str,
    'level_number_prefix': str,
    'street_suffix': str,
    'number_last_prefix': str,
    'level_type': str,
    'Matched': str,  # Added by this process
    'VHDMatched': str,  # Added by this process
    'EZI_ADD': str,  # Added by this process
    'PROPERTY_PFI': str,  # Added by this process
    'geom': str,   # Added by this process
    'vhdplaceid': str,
    'OriginalAddress': str  # Added by this process
}

#,OriginalAddress
register_columns_gnaf = {
    # level_number,level_number_suffix,number_first_prefix,flat_type,flat_number_suffix,number_first_suffix,flat_number_prefix,level_number_prefix,street_suffix,number_last_prefix,level_type
    'Overlay',
    'AddressName',
    'Type',
    'Number',
    'Suburb',
    'PropertyType',
    'PropertyId',
    'HeritageStatus',
    'EstimatedDate',
    'NormalAddress',
    'number_last_suffix',
    'state',
    'postcode',
    'number_first',
    'street_type',
    'number_last',
    'locality_name',
    'building_name',
    'street_name',
    'flat_number',
    'level_number',
    'level_number_suffix',
    'number_first_prefix',
    'flat_type',
    'flat_number_suffix',
    'number_first_suffix',
    'flat_number_prefix',
    'level_number_prefix',
    'street_suffix',
    'number_last_prefix',
    'level_type'  #,
    # 'Matched',  # Added by this process
    # 'EZI_ADD',  # Added by this process
    # 'PROPERTY_PFI',  # Added by this process
    # 'geom',   # Added by this process
    # 'OriginalAddress',  # Added by this process
    # 'vhdplaceid'
}

vicmap_address_attribs = {
    'geom': str,
    'PFI': str,
    'PR_PFI': str,
    'EZI_ADD': str,
    'SOURCE': str,
    'SRC_VERIF': str,
    'IS_PRIMARY': str,
    'PROPSTATUS': str,
    'GCODEFEAT': str,
    'DIST_FLAG': str,
    'LOC_DESC': str,
    'BLGUNTTYP': str,
    'HSA_FLAG': str,
    'HSAUNITID': str,
    'BUNIT_PRE1': str,
    'BUNIT_ID1': int,
    'BUNIT_SUF1': str,
    'BUNIT_PRE2': str,
    'BUNIT_ID2': int,
    'BUNIT_SUF2': str,
    'FLOOR_TYPE': str,
    'FL_PREF1': str,
    'FLOOR_NO_1': int,
    'FL_SUF1': str,
    'FL_PREF2': str,
    'FLOOR_NO_2': int,
    'FL_SUF2': str,
    'BUILDING': str,
    'COMPLEX': str,
    'HSE_PREF1': str,
    'HSE_NUM1': int,
    'HSE_SUF1': str,
    'HSE_PREF2': str,
    'HSE_NUM2': int,
    'HSE_SUF2': str,
    'DISP_PREF1': str,
    'DISP_NUM1': int,
    'DISP_SUF1': str,
    'DISP_PREF2': str,
    'DISP_NUM2': int,
    'DISP_SUF2': str,
    'ROAD_NAME': str,
    'ROAD_TYPE': str,
    'RD_SUF': str,
    'LOCALITY': str,
    'LGA_CODE': str,
    'STATE': str,
    'POSTCODE': str,
    'MESH_BLOCK': str,
    'NUM_RD_ADD': str,
    'NUM_ADD': str,
    'ADD_CLASS': str,
    'ACCESSTYPE': str,
    'OUT_PROP': str,
    'LABEL_ADD': str,
    'FQID': str,
    'PFI_CR': str,
    'UFI': int,
    'UFI_CR': str,
    'UFI_OLD': int,
    'MatchCount': int,
}

# === BQ SCHEMA ===
# USe for importing to a  BQ Table
# Overlay,AddressName,Type,Number,Suburb,PropertyType,PropertyId,HeritageStatus,EstimatedDate,
# NormalAddress,number_last_suffix,state,postcode,number_first,street_type,number_last,locality_name,
# building_name,street_name,flat_number,level_number,level_number_suffix,number_first_prefix,flat_type,
# flat_number_suffix,number_first_suffix,flat_number_prefix,level_number_prefix,street_suffix,number_last_prefix,level_type,OriginalAddress,Matched,
# EZI_ADD,PROPERTY_PFI,geom,vhdplaceid,
# DatePrefix,earliest,latest,DateSuffix,sec_earliest,sec_latest
# "fields": []
# bq --location=australia-southeast1 load --source_format=NEWLINE_DELIMITED_JSON YarraPlanning.YARRA_HERITAGE_REGISTER_C191_WITH_VHD gs://yarra_planning_applications_au/yarra_heritage_register_C191_GNAF.csv_MATCHED_DATE.csv
# git a

# BQ SCHEMA
'Overlay:STRING,AddressName:STRING,Type:STRING,Number:STRING,Suburb:STRING,PropertyType:STRING,PropertyId:STRING,HeritageStatus:STRING,EstimatedDate:STRING,NormalAddress:STRING,number_last_suffix:STRING,state:STRING,postcode:STRING,number_first:STRING,street_type:STRING,number_last:STRING,locality_name:STRING,building_name:STRING,street_name:STRING,flat_number:STRING,level_number:STRING,level_number_suffix:STRING,number_first_prefix:STRING,flat_type:STRING,flat_number_suffix:STRING,number_first_suffix:STRING,flat_number_prefix:STRING,level_number_prefix:STRING,street_suffix:STRING,number_last_prefix:STRING,level_type:STRING,OriginalAddress:STRING,Matched:STRING,VHDMatched:STRING,EZI_ADD:STRING,PROPERTY_PFI:STRING,geom:STRING,vhdplaceid:STRING,DatePrefix:STRING,earliest:INTEGER,latest:INTEGER,DateSuffix:STRING,sec_earliest:INTEGER,sec_latest:INTEGER'