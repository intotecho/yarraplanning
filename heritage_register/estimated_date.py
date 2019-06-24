import pandas as pd
import numpy as np

def get_dates(s):
    df = s.str.extract(r'([Cc]\.)?(\d\d\d\d)[-\/]?,? ?(\d{1,4})?(.*$)', expand=True )
    return df.replace(np.nan, '', regex=True)


def get_secondary(s):
    df =  s.str.extract(r'(\d{1,4})[-\/]?,? ?(\d{1,4})?(.*$)', expand=True )
    return df.replace(np.nan, '', regex=True)

distinct = pd.read_csv('DistinctEstimateDate.csv', usecols=['EstimatedDate'])

#Fixup a read error in input data
distinct.loc[distinct['EstimatedDate'].str.contains('18,731,913', case=False), 'EstimatedDate'] = '1873-1913'

dates = get_dates(distinct['EstimatedDate'])

distinct['Prefix'] = dates[0]
distinct['Earliest'] = dates[1] 
distinct['Latest'] = dates[2] 
distinct['Suffix'] = dates[3] 

distinct['earliest'] = pd.to_numeric(distinct['Earliest'], errors='coerce').fillna(0).astype(np.int64)
distinct['latest'] = pd.to_numeric(distinct['Latest'], errors='coerce').fillna(0).astype(np.int64)

# convert 1883-4 to 1883-1884
distinct['latest'] = distinct['latest'].mask((distinct['latest'] < 10) & (distinct['latest'] > 0), distinct['earliest'] + distinct['latest'] - distinct['earliest'] % 10)

# convert 1883-94 to 1883-1894
distinct['latest'] = distinct['latest'].mask((distinct['latest'] < 100) & (distinct['latest'] > 9), distinct['earliest'] + distinct['latest'] - distinct['earliest'] % 100)

secondary = get_secondary(distinct['Suffix'])
distinct['SecondaryEarliest'] = secondary[0] 
distinct['SecondaryLatest'] = secondary[1] 
distinct['Suffix2'] = secondary[2] 
distinct['sec_earliest'] = pd.to_numeric(distinct['SecondaryEarliest'], errors='coerce').fillna(0).astype(np.int64)
distinct['sec_latest'] = pd.to_numeric(distinct['SecondaryLatest'], errors='coerce').fillna(0).astype(np.int64)

# convert 1883-4 to 1883-1884
distinct['sec_latest'] = distinct['sec_latest'].mask((distinct['sec_latest'] < 10) & (distinct['sec_latest'] > 0), distinct['sec_earliest'] + distinct['sec_latest'] - distinct['sec_earliest'] % 10)

# convert 1883-94 to 1883-1894
distinct['sec_latest'] = distinct['sec_latest'].mask((distinct['sec_latest'] < 100) & (distinct['sec_latest'] > 9), distinct['sec_earliest'] + distinct['sec_latest'] - distinct['sec_earliest'] % 100)


print(distinct.head(50))
circa = distinct[distinct['EstimatedDate'].str.contains('C', case=False)]
print('Testing Circa\n', circa.head(10))
#test = distinct[distinct['SecondaryEarliest'].str.contains('1', case=False)]
#test = distinct[distinct['Latest'].str.len() < 3]
test = distinct[(distinct['latest'] > 0) & ( distinct['latest'] < 1800)]
test.pop('Earliest')
test.pop('Latest')
test.pop('SecondaryEarliest')
test.pop('SecondaryLatest')

print('Testing Secondary Dates\n', test)
gi