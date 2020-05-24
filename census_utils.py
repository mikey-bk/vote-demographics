from census import Census
from us import states
import os
import pandas as pd


def get_census_object():
    API_KEY = os.environ.get("CENSUS_API_KEY")
    return Census(API_KEY)


def make_consecutive_variables_list(group_name, var_from, var_to, postfix='E'):
    return [f'{group_name}_{str(var).zfill(3)}{postfix}' for var in range(var_from, var_to + 1)]


def get_labels_from_variables(census_object, group_name, variable_names, year):
    if year == 2009 and census_object.dataset == 'acs5':
        census_object._switch_endpoints(2010)    
    else:
        census_object._switch_endpoints(year)
    group_url = census_object.groups_url.replace('.json', '/%s.json') % (year, census_object.dataset, group_name)
    resp = census_object.session.get(group_url)
    
    d = resp.json()['variables']
    return [d[var_name]['label'] for var_name in variable_names]


def get_variables_for_group(census_object, group_name, year, postfix=''):
    if year == 2009 and census_object.dataset == 'acs5':
        census_object._switch_endpoints(2010)    
    else:
        census_object._switch_endpoints(year)
    group_url = census_object.groups_url.replace('.json', '/%s.json') % (year, census_object.dataset, group_name)
    print(group_url)
    resp = census_object.session.get(group_url)
    
    return sorted([(k, v['label']) for k, v in resp.json()['variables'].items() if k.endswith(postfix)], key=lambda t: t[0])


def get_concept_from_group(census_object, group_name, year):
    return [gn['description'] for gn in census_object.tables(year=year) if gn['name'] == group_name][0]


def census_get_alaska_data(census_object, fields, year):
    if year == 2009 and census_object.dataset=='acs5':
        census_object.endpoint_url = 'https://api.census.gov/data/%s/acs/%s' % (year, census_object.dataset)
    data =census_object.get(fields, geo={'for': 'state legislative district (lower chamber):*', 'in':'state:02'},year=year)
    df = pd.DataFrame(data)
    df['FIPS'] = (df['state'] + df['state legislative district (lower chamber)']).astype(int)
    df['YEAR'] = year
    df.set_index(['YEAR','FIPS'], inplace=True)
    return df


def census_get_county_equiv_data(census_object, fields, year):
    data1 = None
    if year == 2009 and census_object.dataset=='acs5':
        census_object.endpoint_url = 'https://api.census.gov/data/%s/acs/%s' % (year, census_object.dataset)
        data1 =census_object.get(fields, geo={'for': 'county:*', 'in':'state:*'},year=year)
    else:
        data1 = census_object.state_county(fields, Census.ALL, Census.ALL, year=year)
    df1 = pd.DataFrame(data1)
    df1['FIPS'] = (df1['state'] + df1['county']).astype(int)
    df1['YEAR'] = year
    df1.set_index(['YEAR','FIPS'], inplace=True)
    try:
        df2 = census_get_alaska_data(census_object, fields, year)
        df2 = pd.concat([df1[df1['state']!='02'][fields+['state']],df2[fields+['state']]]).sort_index()
        return df2
    except:
        return df1[fields + ['state']].sort_index()

    