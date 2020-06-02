import urllib.request
import pandas as pd
import os

_file_loc = './data/countypres_2000-2016.tab'

def get_election_lab_file():
    url = 'https://dataverse.harvard.edu/api/access/datafile/:persistentId?persistentId=doi:10.7910/DVN/VOQCHQ/HEIJCQ'
    urllib.request.urlretrieve(url, _file_loc)


def get_election_data():
    if not os.path.exists(_file_loc):
        get_election_lab_file()
    df_raw = pd.read_csv(_file_loc, delimiter='\t')

    df_dem = df_raw[df_raw['party']=='democrat']
    df_gop = df_raw[df_raw['party']=='republican']

    df_dem.loc[:,'YEAR'] = df_dem['year']
    df_dem.loc[:,'dem_votes'] = df_dem['candidatevotes']

    df_gop.loc[:,'YEAR'] = df_gop['year']
    df_gop.loc[:, 'gop_votes'] = df_gop['candidatevotes']

    df = df_dem.loc[:,['YEAR', 'FIPS', 'totalvotes', 'dem_votes']].set_index(['YEAR','FIPS']).join(df_gop.loc[:, ['YEAR', 'FIPS', 'gop_votes']].set_index(['YEAR', 'FIPS']))

    return df


