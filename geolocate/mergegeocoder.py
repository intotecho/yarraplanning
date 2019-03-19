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
import requests
import logging
import time
import os
import sys

logger = logging.getLogger("root")
logger.setLevel(logging.INFO) 
# create console handler
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
logger.addHandler(ch)


#------------------	FUNCTION DEFINITIONS ------------------------

def get_google_results(address, api_key=None, return_full_response=False):
    """
    Get geocode results from Google Maps Geocoding API.
    Based on Shane Lynn GitHub 5th November 2016
    
    Note, that in the case of multiple google geocode reuslts, this function returns details of the FIRST result.
    
    @param address: String address as accurate as possible. For Example "18 Grafton Street, Dublin, Ireland"
    @param api_key: String API key if present from google. 
                    If supplied, requests will use your allowance from the Google API. If not, you
                    will be limited to the free usage of 2500 requests per day.
    @param return_full_response: Boolean to indicate if you'd like to return the full response from google. This
                    is useful if you'd like additional location details for storage or parsing later.
    """
    # Set up your Geocoding url
    geocode_url = "https://maps.googleapis.com/maps/api/geocode/json?address={}".format(address)
    if api_key is not None:
        geocode_url = geocode_url + "&components=country:{}".format(COUNTRY) + "&bounds={}".format(REGION) + "&key={}".format(api_key)
    # Ping google for the reuslts:
    results = requests.get(geocode_url)
    # Results will be in JSON format - convert to dict using requests functionality
    results = results.json()

    # if there's no results or an error, return empty results.
    if len(results['results']) == 0:
        output = {
            "formatted_address" : None,
            "latitude": None,
            "longitude": None,
            "accuracy": None,
            "google_place_id": None,
            "type": None,
            "postcode": None
        }
    else:    
        answer = results['results'][0]
        output = {
            "formatted_address" : answer.get('formatted_address'),
            "latitude": answer.get('geometry').get('location').get('lat'),
            "longitude": answer.get('geometry').get('location').get('lng'),
            "accuracy": answer.get('geometry').get('location_type'),
            "google_place_id": answer.get("place_id"),
            "type": ",".join(answer.get('types')),
            "postcode": ",".join([x['long_name'] for x in answer.get('address_components') 
                                  if 'postal_code' in x.get('types')])
        }
     
    # Append some other details:    
    output['input_string'] = address
    output['number_of_results'] = len(results['results'])
    output['status'] = results.get('status')
    if return_full_response is True:
        output['response'] = results

    return output

#------------------ GET API KEY  -------------------------------
# "Google Maps Geocoding API" key from https://console.developers.google.com/apis/, 
try:
    API_KEY = os.environ['MAPS_API_KEY']
    logger.info("Found private API_KEY : {}".format(API_KEY))
except KeyError: 
    logger.error(
        "MAPS_API_KEY not found in environment.\n \
        For example in ~/.bashrc or startup-script.sh, add the line \n\
        'export MAPS_API_KEY='AIzaSyC9azed9tLdjpZNjg2_kVePWvMIBq154eA'"
    )
    exit()

#------------------ TEST THE API WORKS -----------------------------

# Return Full Google Results? If True, full JSON results from Google are included in output
RETURN_FULL_RESULTS = False
# Bias the Geolocater to prefer addresses near your area of interest
COUNTRY = "AU"  #Australia https://en.wikipedia.org/wiki/List_of_ISO_3166_country_codes
REGION="-37.83893673803455,144.95155334472656|-37.77397129533325,145.0301742553711"  #southwest and northeast corners of this bounding box
#administrative_area = "CITY OF YARRA" 

# Ensure, before we start, that the API key is ok/valid, and internet access is ok
test_result = get_google_results("Richmond, Victoria", API_KEY, RETURN_FULL_RESULTS)
if (test_result['status'] != 'OK') or (test_result['formatted_address'] != 'Richmond VIC 3121, Australia'):
    logger.warning("There was an error when testing the Google Geocoder. {}".format(test_result))
    raise ConnectionError('Problem with test results from Google Geocode - check your API key and internet connection.')


#------------------ CONFIGURATION -------------------------------
 
# Set your input file here
input_filename = "data/yarra_apps_complete_run.csv"

# Set your geocoded addresses file here
geocoded_addresses_filename = "data/encoded_addresses.csv"

# Set your output file name here. It can be the same as the input file but safer to write to a new file.
output_filename = "{}_out".format(input_filename)

# Specify the column name in your input data that contains addresses here.
input_address_column_name = "Property_Address"  #

# Specify the column name in the returned geocoded addresses that contains the input addresses.
geocoded_input_address_column_name = "input_string"

# Specify the columns from address file to append to output file. 

# We don't want to include the response field in our CSV, even if RETURN_FULL_RESULTS is True, because the column contains json. type is OK as the commans are inside a string. 
geo_columns = [ 'accuracy','formatted_address','google_place_id','input_string','latitude','longitude','number_of_results','postcode','status', 'type']

# Specify the columns we wish to read from the apps file. Note that we ignore the columns of geocoded data as it is easier to join this in with the latest addresses. 
# This is also a good time to drop unwanted fields like 'Responsible Officer'.
app_columns = [ 'Application_Number', 'Date_Received', 'Property_Address', 'Description', 'Advert_Date', 'Determination', 'Decision', 'Estimated_Cost', 'Status', 'Ward', 'Results_Page']

# Columns to extract from the decsion_map file.
decision_map_columns = ['Decision',	'Abandoned', 'Refused', 'Approved', 'In_Progress']     # For ML, should drop one of these columns as it can be deduced from the others => dependant var

BACKOFF_TIME = 5 #minutes
LATITUDE = 'latitude' # test existince of key column name.

decision_map_file = "data/decisions_to_outcomes_map.csv"

#------------------ DATA LOADING --------------------------------
results = []
output_pd = None

# Read the input data to a Pandas Dataframe
try:
    input_df = pd.read_csv(input_filename, encoding='utf8', usecols=app_columns)
except Exception as e:
    logger.error("Input File Not Found. Exception {} ".format(e))
    exit()
if input_address_column_name not in input_df.columns:
	raise ValueError("Missing Address column in input data")
applications_count = len(input_df[input_address_column_name])

# Lets' convert the dolllar strings to an integer
input_df['Estimated_Cost']= (input_df['Estimated_Cost']
                              .str.replace(r'[^-+\d.]', '').astype(float))



# ------------ Perform One Hot Encoding on Decision ----------------------

try:
    decision_map_df = pd.read_csv(decision_map_file, encoding='utf8', usecols=decision_map_columns)
    decision_map_df.fillna(0, inplace=True) # Convert NaN to 0 in the map
    input_df = pd.merge(input_df, decision_map_df,  how='left', on=["Decision"])
except Exception as e:
    logger.warn("Error with Decisions to Outcomes Mapping File. Exception {} ".format(e))
    exit()

# Test for Duplicates in input data
try: 
    duplicate_rows_df = pd.concat(g for _, g in input_df.groupby("Application_Number") if len(g) > 1)
    num_dups = len(duplicate_rows_df["Application_Number"])
    #print(df_dups)
    if num_dups > 0:
        logger.error('Duplicates {}'.format(duplicate_rows_df))
        exit()
    else: logger.debug("No Duplicates found")
except ValueError:
    logger.debug('Confirmed No Duplicate Application_Numbers')




# Read the geocoded addresses file into another Pandas Dataframe
try:
    encoded_addresses_df = pd.read_csv(geocoded_addresses_filename, encoding='utf8', usecols=geo_columns)
except Exception as e:
    if len(sys.argv) > 1  and sys.argv[1] == 'reset_cache':
        encoded_addresses_df = pd.DataFrame(columns=geo_columns)
        logger.warning("WARNING! Re-encoding all addresses.")
        encoded_addresses_df.to_csv("{}".format(geocoded_addresses_filename), mode='w', header=True, index=True, encoding='utf8', columns=geo_columns)
    else:
        logger.error("Encoded address file not found or not usable. To regenerate a new empty cache, use parameter `reset_cache`.")
        exit()

if geocoded_input_address_column_name not in encoded_addresses_df.columns:
	raise ValueError("Missing Address column in merge data")
encoded_addresses_df = encoded_addresses_df.rename(columns={geocoded_input_address_column_name: input_address_column_name}) # rename for the join
preconverted_addresses = len(encoded_addresses_df[input_address_column_name])
encoded_addresses_df.tail()

def merge_and_save(input_df, encoded_addresses_df, input_address_column_name):
    logger.info("Joining applications with geocoded addresses")

    output_df = pd.merge(input_df, encoded_addresses_df,  how='left', on=[input_address_column_name])
    # Pandas doesn't mind columns that differ only in case, but BigQuery won't accept it.
    # Also big query doesn't like spaces in column names.

    output_df.rename(columns={
                'Status':'Application_Status',
                'status':'encodingstatus'
    
                #'Application Number':'Application_Number',
                #'Date Received':'Date_Received',
                ##'Estimated Cost':'Estimated_Cost',
                #'Property Address':'Property_Address',
                #'Results Page':'Results_Page',
                #'Advert Date':'Advert_Date'
                }, 
                    inplace=True)
    logger.debug("merge_and_save input columns: {}".format(input_df.columns.values.tolist()))
    logger.debug("merge_and_save address columns: {}".format(encoded_addresses_df.columns.values.tolist()))
    logger.debug("merge_and_save output columns: {}".format(output_df.columns.values.tolist()))


    # And convert the commas to semis in the placetype returned by geocoder.                              
    output_df['type']= (output_df['type']
                              .str.replace(',', ';', regex=False))


    output_df.to_csv("{}".format(output_filename), mode='w', header=True, index=False, encoding='utf8')
    return output_df

#------------------ MERGE EXISTING GEOCODING RESULTS INTO THE INPUT FILE AND SAVE --------------------

output_df = merge_and_save(input_df, encoded_addresses_df, input_address_column_name)

if LATITUDE not in output_df.columns:
	raise ValueError("Missing {} column in output_df: {}".format(LATITUDE, output_df.columns))

missing_addresses_count = output_df[LATITUDE].isna().sum() 
encoded_addresses_df = encoded_addresses_df.rename(columns={input_address_column_name: geocoded_input_address_column_name}) # return these back to normal in case we append to this file.

#------------------ GET UNPROCESSED APPLICATIONS -----------------------------

# Make a dataframe of only those applications with no geocoded address. 
# Make a complete list of all unique addresses from the input.
# This will remove all other columns except address and index, drop duplicates and sort.
applications_to_process  = output_df[output_df[LATITUDE].isna()]
pd_addresses_to_convert = applications_to_process[input_address_column_name].drop_duplicates().sort_values(ascending=True)
addresses = pd_addresses_to_convert.tolist()
logger.info('{} of {} applications have address that was not found in list of {} geocoded addresses.'.format(missing_addresses_count, applications_count, preconverted_addresses))
logger.info('Convering list of {} unique addresses.'.format(len(addresses)))

#------------------ MAIN PROCESSING LOOP -----------------------------

# Go through each address in turn
for address in addresses:

    # While the address geocoding is not finished:
    geocoded = False
    while geocoded is not True:
        # Geocode the address with google
        try:
            geocode_result = get_google_results(address, API_KEY, return_full_response=RETURN_FULL_RESULTS)
        except Exception as e:
            logger.exception(e)
            logger.error("Major error with {}".format(address))
            logger.error("Skipping!")
            geocoded = True
            
        # If we're over the API limit, backoff for a while and try again later.
        if geocode_result['status'] == 'OVER_QUERY_LIMIT':
            logger.info("Hit Query Limit! Backing off for a bit.")
            time.sleep(BACKOFF_TIME * 60) # sleep for BACKOF_TIME minutes
            geocoded = False
        else:
            # ---- APPEND NEW GEOCODING TO If we're ok with API use, appnedsave the results
            # Note that the results might be empty / non-ok - log this
            if geocode_result['status'] != 'OK':
                logger.warning("Error geocoding {}: {}".format(address, geocode_result['status']))
            logger.info("Geocoded: {}: {}".format(address, geocode_result['status']))
            results.append(geocode_result)           
            geocoded = True
            new_pd = pd.DataFrame([geocode_result])
            # Append geo_columns of new result to file.
            new_pd[geo_columns].to_csv("{}".format(geocoded_addresses_filename), mode='a', header=False, index=True, encoding='utf8', columns=geo_columns)
            encoded_addresses_df = pd.concat([encoded_addresses_df, new_pd], ignore_index=True, sort=False)

    # Print status every N addresses
    if len(results) % 100 == 0:
    	logger.info("Converted {} of {} addresses".format(len(results), len(addresses)))

#------------------ COMPLETED  -----------------------------
num_converted = len(results)
if num_converted > 0:
    encoded_addresses_df = encoded_addresses_df.rename(columns={geocoded_input_address_column_name: input_address_column_name}) # rename before the join

    logger.info("<<< Merging {} new results and saving.>>>".format(num_converted))
    output_df = merge_and_save(input_df, encoded_addresses_df, input_address_column_name)
else:
    logger.info("<<< All applications have a geocoded address. >>>")
exit(num_converted)
