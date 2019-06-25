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
    'RegisterAddress': unicode,
    'RegularAddress': unicode,
    'Comments': unicode
}


vhd_dtypes = {
    'VHRlng': float,
    'Name': unicode,
    'vhdplaceid': long,
    'Overlay': unicode,
    'Authority': unicode,
    'VHR': unicode,
    'href': unicode,
    'Location': unicode,
    'VHRlat': float,
    'SoSHash': unicode
}

register_dtypes_gnaf = {
    # level_number,level_number_suffix,number_first_prefix,flat_type,flat_number_suffix,number_first_suffix,flat_number_prefix,level_number_prefix,street_suffix,number_last_prefix,level_type
    'Overlay': unicode,
    'AddressName': unicode,
    'Type': unicode,
    'Number': unicode,
    'Suburb': unicode,
    'PropertyType': unicode,
    'PropertyId': unicode,
    'HeritageStatus': unicode,
    'EstimatedDate': unicode,
    'NormalAddress': unicode,
    'number_last_suffix': unicode,
    'state': unicode,
    'postcode': unicode,
    'number_first': unicode,
    'street_type': unicode,
    'number_last': unicode,
    'locality_name': unicode,
    'building_name': unicode,
    'street_name': unicode,
    'flat_number': unicode,
    'level_number': unicode,
    'level_number_suffix': unicode,
    'number_first_prefix': unicode,
    'flat_type': unicode,
    'flat_number_suffix': unicode,
    'number_first_suffix': unicode,
    'flat_number_prefix': unicode,
    'level_number_prefix': unicode,
    'street_suffix': unicode,
    'number_last_prefix': unicode,
    'level_type': unicode,
    'Matched': unicode,  # Added by this process
    'VHDMatched': unicode,  # Added by this process
    'EZI_ADD': unicode,  # Added by this process
    'PROPERTY_PFI': unicode,  # Added by this process
    'geom': unicode,   # Added by this process
    'vhdplaceid': unicode,
    'OriginalAddress': unicode  # Added by this process
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
    'geom': unicode,
    'PFI': unicode,
    'PR_PFI': unicode,
    'EZI_ADD': unicode,
    'SOURCE': unicode,
    'SRC_VERIF': unicode,
    'IS_PRIMARY': unicode,
    'PROPSTATUS': unicode,
    'GCODEFEAT': unicode,
    'DIST_FLAG': unicode,
    'LOC_DESC': unicode,
    'BLGUNTTYP': unicode,
    'HSA_FLAG': unicode,
    'HSAUNITID': unicode,
    'BUNIT_PRE1': unicode,
    'BUNIT_ID1': int,
    'BUNIT_SUF1': unicode,
    'BUNIT_PRE2': unicode,
    'BUNIT_ID2': int,
    'BUNIT_SUF2': unicode,
    'FLOOR_TYPE': unicode,
    'FL_PREF1': unicode,
    'FLOOR_NO_1': int,
    'FL_SUF1': unicode,
    'FL_PREF2': unicode,
    'FLOOR_NO_2': int,
    'FL_SUF2': unicode,
    'BUILDING': unicode,
    'COMPLEX': unicode,
    'HSE_PREF1': unicode,
    'HSE_NUM1': int,
    'HSE_SUF1': unicode,
    'HSE_PREF2': unicode,
    'HSE_NUM2': int,
    'HSE_SUF2': unicode,
    'DISP_PREF1': unicode,
    'DISP_NUM1': int,
    'DISP_SUF1': unicode,
    'DISP_PREF2': unicode,
    'DISP_NUM2': int,
    'DISP_SUF2': unicode,
    'ROAD_NAME': unicode,
    'ROAD_TYPE': unicode,
    'RD_SUF': unicode,
    'LOCALITY': unicode,
    'LGA_CODE': unicode,
    'STATE': unicode,
    'POSTCODE': unicode,
    'MESH_BLOCK': unicode,
    'NUM_RD_ADD': unicode,
    'NUM_ADD': unicode,
    'ADD_CLASS': unicode,
    'ACCESSTYPE': unicode,
    'OUT_PROP': unicode,
    'LABEL_ADD': unicode,
    'FQID': unicode,
    'PFI_CR': unicode,
    'UFI': long,
    'UFI_CR': unicode,
    'UFI_OLD': long,
    'MatchCount': long,
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