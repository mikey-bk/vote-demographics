import urllib.request
from zipfile import ZipFile
import os

import geopandas as gpd
import pandas as pd

from utils import mkdir_r


def find_shapefiles(path):
    for _,_,f in os.walk(path):
        return [item for item in f if item.split('.')[-1] == 'shp']
    return []


def get_tiger_files(year, outpath, force_reload=False):
    

    if year in range(2011, 2021):
        url = f'https://www2.census.gov/geo/tiger/TIGER{year}/COUNTY/tl_{year}_us_county.zip'
    elif year == 2010:
        url = f'https://www2.census.gov/geo/tiger/TIGER2010/COUNTY/2010/tl_2010_us_county10.zip'
    elif year in range(2008, 2010):
        url = f'https://www2.census.gov/geo/tiger/TIGER{year}/tl_{year}_us_county.zip'
    elif year == 2000:
        url = f'https://www2.census.gov/geo/tiger/TIGER2010/COUNTY/2000/tl_2010_us_county00.zip'

    import urllib.request

    print(f'Downloading shapefiles: {url}')

    if not os.path.exists(outpath):
        mkdir_r(outpath)

    li = find_shapefiles(outpath)
    if not force_reload and len(li) > 0:
        return os.path.join(outpath, li[-1])

    urllib.request.urlretrieve(url, f'{outpath}/shapefiles.zip')

    olddir = os.getcwd()
    os.chdir(outpath)
    with ZipFile('shapefiles.zip', 'r') as zipObj:
        zipObj.extractall()

    for _,_,f in os.walk('.'):
        filename = [item for item in f if item.split('.')[-1] == 'shp'][0]
        break

    os.remove('./shapefiles.zip')
    os.chdir(olddir)

    return os.path.join(outpath, filename)

def get_geodata_from_shapefile(year):
    '''
    Returns a pandas dataframe with:
    * County FIPS
    * Land area
    * Centroid Latitude
    * Centroid Longitude
    '''
    df = pd.DataFrame()

    

    if year in [2000,2001]:
        sf = get_tiger_files(2000, './data/shapefiles/2000')
        gdf = gpd.read_file(sf)
        gdf = gdf.dissolve(by='CNTYIDFP00')
        gdf.reset_index(inplace=True)
        df['FIPS'] = gdf['CNTYIDFP00'].astype(int)
        df['ALAND'] = gdf['ALAND00'].astype('int64') / 1e6
        df['INTPTLAT'] = gdf.centroid.y
        df['INTPTLON'] = gdf.centroid.x
    
    elif year in range(2002, 2018):
        sf = get_tiger_files(2010, './data/shapefiles/2010')
        gdf = gpd.read_file(sf)
        gdf = gdf.dissolve(by='GEOID10')
        gdf.reset_index(inplace=True)
        df['FIPS'] = gdf['GEOID10'].astype(int)
        df['ALAND'] = gdf['ALAND10'].astype('int64') / 1e6
        df['INTPTLAT'] = gdf.centroid.y
        df['INTPTLON'] = gdf.centroid.x

    else:
        sf = get_tiger_files(year, f'./data/shapefiles/{year}')
        gdf = gpd.read_file(sf)
        gdf = gdf.dissolve(by='GEOID')
        gdf.reset_index(inplace=True)
        df['FIPS'] = gdf['GEOID'].astype(int)
        df['ALAND'] = gdf['ALAND'].astype('int64') / 1e6
        df['INTPTLAT'] = gdf.centroid.y
        df['INTPTLON'] = gdf.centroid.x

    return df

    







    


    



