# -*- coding: utf-8 -*-
# noqa: E501
"""

Convert the output of QGIS list of VICMAP_ADDRESS properties see metastring
to a format for Pandas to read dypes - of the format
dtypes = {'user_id': int}

This only has to be run once but worth keeping a copy.

"""
import re


# ------------------ CONFIGURATION -------------------------------
dtype={'user_id': int}

metastring = """geom, String
PFI, String
PR_PFI, String
EZI_ADD, String
SOURCE, String
SRC_VERIF, Date
IS_PRIMARY, String
PROPSTATUS, String
GCODEFEAT, String
DIST_FLAG, String
LOC_DESC, String
BLGUNTTYP, String
HSA_FLAG, String
HSAUNITID, String
BUNIT_PRE1, String
BUNIT_ID1, Integer
BUNIT_SUF1, String
BUNIT_PRE2, String
BUNIT_ID2, Integer
BUNIT_SUF2, String
FLOOR_TYPE, String
FL_PREF1, String
FLOOR_NO_1, Integer
FL_SUF1, String
FL_PREF2, String
FLOOR_NO_2, Integer
FL_SUF2, String
BUILDING, String
COMPLEX, String
HSE_PREF1, String
HSE_NUM1, Integer
HSE_SUF1, String
HSE_PREF2, String
HSE_NUM2, Integer
HSE_SUF2, String
DISP_PREF1, String
DISP_NUM1, Integer
DISP_SUF1, String
DISP_PREF2, String
DISP_NUM2, Integer
DISP_SUF2, String
ROAD_NAME, String
ROAD_TYPE, String
RD_SUF, String
LOCALITY, String
LGA_CODE, String
STATE, String
POSTCODE, String
MESH_BLOCK, String
NUM_RD_ADD, String
NUM_ADD, String
ADD_CLASS, String
ACCESSTYPE, String
OUT_PROP, String
LABEL_ADD, String
FQID, String
PFI_CR, Date
UFI, Integer64
UFI_CR, Date
UFI_OLD, Integer64
"""
output = '{\n'
lines = metastring.split('\n')
index = len(lines)-1
for l in lines:
    m = re.sub(r"^(.*), (.*)$", r"    '\1': \2", l)
    m = re.sub('String', 'unicode', m)
    m = re.sub('Integer64', 'long', m)
    m = re.sub('Integer', 'int', m)
    m = re.sub('Date', 'unicode', m) # we don't use it.
    output = output + m
    index = index-1
    if index > 0:
        output = output + (',\n')
output = output + ('\n}\n')
print(output)
exit(0)
