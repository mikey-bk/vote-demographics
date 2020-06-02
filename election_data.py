import urllib.request
import pandas as pd
import os
from utils import mkdir_r

_dir_loc = './data/elections'
_file_loc = f'{_dir_loc}/countypres_2000-2016.tab'

def get_election_lab_file():
    '''Retrieve original files from the MIT election lab.
    Citation: MIT Election Data and Science Lab, 2018, "County Presidential Election Returns 2000-2016", https://doi.org/10.7910/DVN/VOQCHQ, Harvard Dataverse, V6, UNF:6:ZZe1xuZ5H2l4NUiSRcRf8Q== [fileUNF]
    '''
    url = 'https://dataverse.harvard.edu/api/access/datafile/:persistentId?persistentId=doi:10.7910/DVN/VOQCHQ/HEIJCQ'
    mkdir_r(_dir_loc)
    urllib.request.urlretrieve(url, _file_loc)


def get_election_data():
    '''Converts election data file to a format useable in the analysis (indexed by year / fips).
    The dataframe also includes a PVI column.
    '''

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

    df_year_totals = df.reset_index().groupby(by='YEAR').sum().drop('FIPS', axis=1).rename({'totalvotes':'nationaltotalvotes', 
    'dem_votes': 'national_dem_votes',
    'gop_votes': 'national_gop_votes'}, axis=1)

    df = df.reset_index().set_index('YEAR').join(df_year_totals).reset_index()

    df.loc[:,'national_dr_votes'] = df['national_dem_votes'] + df['national_gop_votes']
    df.loc[:,'national_avg'] = df['national_dem_votes'] / df['national_dr_votes']
    df.loc[:,'dr_votes'] = df['dem_votes'] + df['gop_votes']
    df.loc[:,'local_avg']  = df['dem_votes'] / df['dr_votes']
    df.loc[:, 'pvi'] = df['local_avg'] - df['national_avg']
    df.loc[:, 'pvi'] = df['pvi'] * 100
    
    df.drop(['national_dr_votes', 'national_avg', 'dr_votes', 'local_avg'], axis=1, inplace=True)
    df.set_index(['YEAR', 'FIPS'], inplace=True)
    
    return df


