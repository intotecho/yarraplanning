# Heritage Register
Utilities in this folder 
- clean the Heritage Register returned by tabula, 
- decompose the addresses 
- match the addresses to VICMAP data.
- match the address to VHD data

# clean_register.py

## Input: 

Use tabula to convert Yarra Appendix 8 PDF to a CSV file.
Then call clean_register.py to clean up the mess.

## Output

Then call register_2gnaf.py to convert the output of clean_register.py to components matching the Australian GNAF dataset.

#register_2gnaf.py
This will decompose the address to these components and these columns to the output file.
[
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

This uses a RNN based on [address-net](https://github.com/jasonrig/address-net)

### dependencies 
To use the address-net, Setup your enviromnent to use python 3.5 and install the required packages.

```{python}
cd heritage_register
virtualenv --python python3 env
source env/bin/activate
pip install pandas
pip install address-net
pip install address-net[tf]
python register-2gnaf.py
```

The file *predict.py* is for info only. It changes one line to
`address_net_estimator = tf.estimator.Estimator(model_fn=model_fn, model_dir=model_dir, params={})`
Otherwise, you get a WARNING issued for each prediction.
WARNING:tensorflow:Estimator's model_fn (<function model_fn at 0x7fded56bc1e0>) includes params argument, but params are not passed to Estimator. 
I suppressed this by adding params={}
This makes it run faster.
However, the correct approach is to patch and install the library

### Note
register_2gnaf is slow, so is designed to allow interruption at anytime. It will pickup where it left off at the first non-matched item.


# match_addresses.py

Match (Join) addresses in the heritage register with VicMap Address data
Always delete the _MATCHED.csv output before running - (There is a bug so it doesn't work)
## Inputs 
1. Heritage register, cleaned with clean_register then decomposed with register2gnaf 
2. VicMap Address data filtered to 'Yarra' where LGA396 
  Select * from  yarrascrape.YarraPlanning.YARRA_ADDRESSES
  where LGA_CODE = 376

## Description

To handle interruptions, allow the process to be checkmarked, 
- Input files R.csv, A.csv
- checkpoint files R.wip.csv
- output files R_out.CSV
- Skip through all the R rows that have Matched <> null. NoMatch is not repeated.
- Every N rows, write the results to output files.
- On start, check for existance of output files and use these instead.

Objectives:
Match promiscuously. A near-miss is better than a total blank. Blanks don't show on the map.
For heritage, units, levels and flats are less prominent than buildings.

## Outputs
Each execution will first read the output files then kick off the process from where it left off.
To restart, delete the output files and they will be created.

register_MATCHED.csv contains new columns: 
  - Matched 
  - EZI_ADDRESS from matching address 
  - PROPERTY_PFI from matching address

Matched will be one of 
- '', No match tried
- 'NotAnAddress', The Road name, Road Type and Suburb don't exist
- 'NoMatch', None of the strategies mathced
- 'Full', Address is correct. Fully matches.
- 'FullSwapSuburb', Address fully matches after changing the suburb.
- 'Multiple', Address in Register matches more than one address
- 'MultipleSwapSuburb', Address in Register matches more than one address after swapping the suburb.
- 'FirstMatchedRange,  The Address matches the first of a range of numbers that make an address in VICMAP_ADDRESS.
- 'Building', 
- 'Range', 
- 'Complex'


address_MATCHED.csv contains new columns:
  - MatchCount
This is for recording when duplicate register sites match the same an address.

Address Components in register are
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

Addressc components in VicMap - 
For definition of attributes in Address Data see VMAddress_Product_Specification.doc

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

# VicMap Attributes
See buibuild_vicmap_address_attribs.py which generates a datatype object.
python build_vicmap_address_attribs.py > vicmap_address_attribs.json  
This is only needed once to generate the dtype map in match_addresses.py.
IS_PRIMARY,
PROPSTATUS,
LOC_DESC,
BLGUNTTYP,
HSA_FLAG,
HSAUNITID,
BUNIT_PRE1,
BUNIT_ID1,
BUNIT_SUF1,
BUNIT_PRE2,
BUNIT_ID2,
BUNIT_SUF2,
FLOOR_TYPE,
FL_PREF1,
FLOOR_NO_1,
FL_SUF1,
FL_PREF2,
FLOOR_NO_2,
FL_SUF2,
BUILDING,
COMPLEX,
HSE_PREF1,
HSE_NUM1,
HSE_SUF1,
HSE_PREF2,
HSE_NUM2,
HSE_SUF2,
DISP_PREF1,
DISP_NUM1,
DISP_SUF1,
DISP_PREF2,
DISP_NUM2,
DISP_SUF2,
ROAD_NAME,
ROAD_TYPE,
RD_SUF,
LOCALITY,
LGA_CODE,
STATE,
POSTCODE,
MESH_BLOCK,
NUM_RD_ADD,
NUM_ADD,
ADD_CLASS,
ACCESSTYPE,
OUT_PROP,
LABEL_ADD,