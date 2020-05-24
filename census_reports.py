from census_utils import *
import pandas as pd
from census_geodata import get_geodata_from_shapefile
from utils import mkdir_r


c = get_census_object()

def generate_county_names_file(YEAR):
    census_object = c.sf3 if YEAR == 2000 else c.acs5
    df_names = census_get_county_equiv_data(census_object, ['NAME'], YEAR)

    df_names['County'] = df_names['NAME'].apply(lambda s: ','.join(s.split(',')[:-1]))
    df_names['State']  = df_names['NAME'].apply(lambda s: s.split(',')[-1])

    df_names[df_names.columns[-2:]].to_csv(f'./data/{YEAR}/county_names.csv')

def generate_county_data_file(YEAR):
    generate_county_names_file(YEAR)
    df_names = pd.read_csv(f'./data/{YEAR}/county_names.csv')
    df_names.set_index('FIPS', inplace=True)

    df_geodata = get_geodata_from_shapefile(YEAR)
    df_geodata.set_index('FIPS', inplace=True)

    df_names.join(df_geodata).to_csv(f'./data/{YEAR}/county_data.csv')


def generate_household_income_file(YEAR):
    if YEAR == 2000:
        df_search = pd.DataFrame({key: obj for key, obj in c.sf3.fields(year=2000).items() if obj['label'].lower().find('income') > -1 or obj['concept'].lower().find('income') > -1}).transpose()
        sf3_p52 = df_search[df_search['concept'].apply(lambda s : s.split('.')[0] == 'P52')].sort_index()

        variable_names = list(sf3_p52.index.values)
        df_income = census_get_county_equiv_data(c.sf3, ['NAME'] + variable_names, YEAR)

        df_income['INCOME_HOUSEHOLDS_ALL'] = pd.to_numeric(df_income['P052001'])
        df_income['INCOME_HOUSEHOLDS_BELOW_35K'] = df_income[df_income.columns[2:8]].astype(float).sum(axis=1)
        df_income['INCOME_HOUSEHOLDS_ABOVE_200K'] = pd.to_numeric(df_income['P052017'])
    else:
        # print(get_variables_for_group(c.acs5, 'B19001', YEAR, 'E'))
        variable_names = make_consecutive_variables_list('B19001', 1, 17, 'E')
        df_income = census_get_county_equiv_data(c.acs5, ['NAME', 'B01003_001E'] + variable_names, YEAR)

        df_income['INCOME_HOUSEHOLDS_ALL'] = df_income['B19001_001E']
        df_income['INCOME_HOUSEHOLDS_BELOW_35K'] = df_income[df_income.columns[3:9]].sum(axis=1)
        df_income['INCOME_HOUSEHOLDS_ABOVE_200K'] = df_income['B19001_017E']
        
    df_income['INCOME_HOUSEHOLDS_BELOW_35K_PCT'] = df_income['INCOME_HOUSEHOLDS_BELOW_35K'] / df_income['INCOME_HOUSEHOLDS_ALL'] 
    df_income['INCOME_HOUSEHOLDS_ABOVE_200K_PCT'] = df_income['INCOME_HOUSEHOLDS_ABOVE_200K'] / df_income['INCOME_HOUSEHOLDS_ALL'] 

    df_income[df_income.columns[-5:]].to_csv(f'./data/{YEAR}/income.csv')


def generate_median_income_file(YEAR):
    if YEAR == 2000:
        df_median_income = census_get_county_equiv_data(c.sf3, ['NAME','P053001'], YEAR)
        df_median_income.rename(columns={'P053001':'HOUSEHOLD_MEDIAN_INCOME'},inplace=True)
        
    else:
        df_median_income = census_get_county_equiv_data(c.acs5, ['NAME', 'B19013_001E'], YEAR)
        df_median_income.rename(columns={'B19013_001E':'HOUSEHOLD_MEDIAN_INCOME'},inplace=True)

    df_median_income[['HOUSEHOLD_MEDIAN_INCOME']].to_csv(f'./data/{YEAR}/median_income.csv')


def generate_population_file(YEAR):
    if YEAR == 2000:
        df_population = census_get_county_equiv_data(c.sf1, ['NAME', 'P001001'], YEAR)
        df_population.rename(columns={'P001001': 'Total Population'}, inplace = True)
    else:
        df_population = census_get_county_equiv_data(c.acs5, ['NAME', 'B01003_001E'], YEAR)
        df_population.rename(columns={'B01003_001E': 'Total Population'}, inplace = True)

    df_population[['Total Population']].to_csv(f'./data/{YEAR}/population.csv')


def generate_education_file(YEAR):
    if YEAR==2000:
        df_search=pd.DataFrame(c.sf3.fields(year=2000)).transpose()
        sf3_p37 = df_search[df_search['concept'].apply(lambda s : s.split('.')[0] == 'P37')].sort_index()

        variable_names = list(sf3_p37.index.values)
        df_education = census_get_county_equiv_data(c.sf3, variable_names, YEAR)
        
        df_education['POPULATION_25Y_AND_OVER'] = pd.to_numeric(df_education['P037001'])
        df_education['HIGH_SCHOOL_AND_HIGHER'] = df_education[df_education.columns[10:18]].astype(float).sum(axis=1) + df_education[df_education.columns[27:35]].astype(float).sum(axis=1)
        df_education['BACHELOR_AND_HIGHER'] = df_education[df_education.columns[14:18]].astype(float).sum(axis=1) + df_education[df_education.columns[31:35]].astype(float).sum(axis=1)
        
    else:
        variable_names = make_consecutive_variables_list('B15002', 1, 35, 'E')
        df_education = census_get_county_equiv_data(c.acs5, ['NAME'] + variable_names, YEAR)
        
        df_education['POPULATION_25Y_AND_OVER'] = pd.to_numeric(df_education['B15002_001E'])
        df_education['HIGH_SCHOOL_AND_HIGHER'] = df_education[df_education.columns[11:19]].sum(axis=1) + df_education[df_education.columns[28:36]].sum(axis=1)
        df_education['BACHELOR_AND_HIGHER'] = df_education[df_education.columns[15:19]].sum(axis=1) + df_education[df_education.columns[32:36]].sum(axis=1)

    df_education['HIGH_SCHOOL_AND_HIGHER_PCT'] = df_education['HIGH_SCHOOL_AND_HIGHER']/df_education['POPULATION_25Y_AND_OVER']
    df_education['BACHELOR_AND_HIGHER_PCT'] = df_education['BACHELOR_AND_HIGHER']/df_education['POPULATION_25Y_AND_OVER']

    df_education[df_education.columns[-5:]].to_csv(f'./data/{YEAR}/education.csv')


def generate_race_ethnicity_file(YEAR):
    if YEAR==2000:
        df_search=pd.DataFrame(c.sf3.fields(year=2000)).transpose()
        sf3_p7 = df_search[df_search['concept'].apply(lambda s : s.split('.')[0] == 'P7')].sort_index()

        variable_names = list(sf3_p7.index.values)
        df_race_ethnicity = census_get_county_equiv_data(c.sf3, ['P001001'] + variable_names, YEAR)
        
        df_race_ethnicity['POP'] = pd.to_numeric(df_race_ethnicity['P001001'])
        df_race_ethnicity['RACE_WHITE_NON_HISPANIC'] = pd.to_numeric(df_race_ethnicity['P007003'])
        df_race_ethnicity['RACE_BLACK_NON_HISPANIC'] = pd.to_numeric(df_race_ethnicity['P007004'])
        df_race_ethnicity['RACE_NATIVE_AM_NON_HISPANIC'] = pd.to_numeric(df_race_ethnicity['P007005'])
        df_race_ethnicity['RACE_ASIAN_NON_HISPANIC'] = pd.to_numeric(df_race_ethnicity['P007006'])
        df_race_ethnicity['HISPANIC_OR_LATINO'] = pd.to_numeric(df_race_ethnicity['P007010'])
    else:        
        variable_names = make_consecutive_variables_list('B03002', 1, 21, 'E')
        df_race_ethnicity = census_get_county_equiv_data(c.acs5, ['NAME'] + variable_names, YEAR)
        
        df_race_ethnicity['POP'] = df_race_ethnicity['B03002_001E']
        df_race_ethnicity['RACE_WHITE_NON_HISPANIC'] = df_race_ethnicity['B03002_003E']
        df_race_ethnicity['RACE_BLACK_NON_HISPANIC'] = df_race_ethnicity['B03002_004E']
        df_race_ethnicity['RACE_NATIVE_AM_NON_HISPANIC'] = df_race_ethnicity['B03002_005E']
        df_race_ethnicity['RACE_ASIAN_NON_HISPANIC'] = df_race_ethnicity['B03002_006E']
        df_race_ethnicity['HISPANIC_OR_LATINO'] = df_race_ethnicity['B03002_012E']
        
    df_race_ethnicity['RACE_WHITE_NON_HISPANIC_PCT'] = df_race_ethnicity['RACE_WHITE_NON_HISPANIC'] / df_race_ethnicity['POP']
    df_race_ethnicity['RACE_BLACK_NON_HISPANIC_PCT'] = df_race_ethnicity['RACE_BLACK_NON_HISPANIC'] / df_race_ethnicity['POP']
    df_race_ethnicity['RACE_NATIVE_AM_NON_HISPANIC_PCT'] = df_race_ethnicity['RACE_NATIVE_AM_NON_HISPANIC'] / df_race_ethnicity['POP']
    df_race_ethnicity['RACE_ASIAN_NON_HISPANIC_PCT'] = df_race_ethnicity['RACE_ASIAN_NON_HISPANIC'] / df_race_ethnicity['POP']
    df_race_ethnicity['HISPANIC_OR_LATINO_PCT'] = df_race_ethnicity['HISPANIC_OR_LATINO'] / df_race_ethnicity['POP']

    df_race_ethnicity[df_race_ethnicity.columns[-10:]].to_csv(f'./data/{YEAR}/race_and_ethnicity.csv')


def generate_household_types_file(YEAR):
    if YEAR==2000:
        variable_names = ['P010001', 'P010007', 'P010006']
        df_households = census_get_county_equiv_data(c.sf3, ['NAME'] + variable_names, YEAR)

        df_households['NUM_HOUSEHOLDS'] = pd.to_numeric(df_households['P010001'])
        df_households['MARRIED_COUPLE_FAMILIES'] = pd.to_numeric(df_households['P010007'])
        df_households['NON_FAMILY_HOUSEHOLDS'] = df_households['NUM_HOUSEHOLDS'] - pd.to_numeric(df_households['P010006'])
        
    else:
        variable_names = ['B11001_001E', 'B11001_003E', 'B11001_007E']
        df_households = census_get_county_equiv_data(c.acs5, ['NAME'] + variable_names, YEAR)
        df_households.head()

        df_households['NUM_HOUSEHOLDS'] = df_households['B11001_001E']
        df_households['MARRIED_COUPLE_FAMILIES'] = df_households['B11001_003E']
        df_households['NON_FAMILY_HOUSEHOLDS'] = df_households['B11001_007E']
    
    df_households['MARRIED_COUPLE_FAMILIES_PCT'] = df_households['MARRIED_COUPLE_FAMILIES']/df_households['NUM_HOUSEHOLDS']
    df_households['NON_FAMILY_HOUSEHOLDS_PCT'] = df_households['NON_FAMILY_HOUSEHOLDS']/df_households['NUM_HOUSEHOLDS']
        
    df_households[df_households.columns[-5:]].to_csv(f'./data/{YEAR}/households.csv')


def generate_age_file(YEAR):
    if YEAR==2000:
        variable_names = [f'P008{str(num).zfill(3)}' for num in range(1,80)]
        df_ages = census_get_county_equiv_data(c.sf3, variable_names, YEAR)
        df_ages.rename(columns={'P008001':'POP'}, inplace=True)
        df_ages['TOTAL_POP_18+']=df_ages[df_ages.columns[20:40]].astype(float).sum(axis=1) + df_ages[df_ages.columns[59:79]].astype(float).sum(axis=1)
        df_ages['TOTAL_POP_65+']=df_ages[df_ages.columns[34:40]].astype(float).sum(axis=1) + df_ages[df_ages.columns[73:79]].astype(float).sum(axis=1)
    
    else:
        variable_names = make_consecutive_variables_list('B01001', 1, 49, 'E')
        df_ages = census_get_county_equiv_data(c.acs5, ['NAME'] + variable_names, YEAR)
        df_ages.rename(columns={'B01001_001E':'POP'}, inplace=True)
        df_ages['TOTAL_POP_18+']=df_ages[df_ages.columns[7:26]].sum(axis=1) + df_ages[df_ages.columns[31:50]].sum(axis=1)
        df_ages['TOTAL_POP_65+']=df_ages[df_ages.columns[20:26]].sum(axis=1) + df_ages[df_ages.columns[44:50]].sum(axis=1)
    
    df_ages['TOTAL_POP_18+_PCT'] = df_ages['TOTAL_POP_18+'] / df_ages['POP'].astype(float)
    df_ages['TOTAL_POP_65+_PCT'] = df_ages['TOTAL_POP_65+'] / df_ages['POP'].astype(float)
    df_ages[df_ages.columns[-4:]].to_csv(f'./data/{YEAR}/ages.csv')


def generate_files(years, functions):
    from itertools import product

    for year, fun in product(years, functions):
        mkdir_r(f'./data/{year}')

        print(f'{fun.__name__}({year})...')
        fun(year)


def combine_files_into_topics(topics):
    years = [2016,2012,2009,2000]
    datasets = {}
    from itertools import product

    for year, topic in product(years, topics):
        if topic not in datasets:
            datasets[topic] = []
        try:
            df = pd.read_csv(f'./data/{year}/{topic}.csv')
            if year == 2009:
                df['YEAR'] = 2008
            datasets[topic].append(df.set_index(['YEAR', 'FIPS']))
        except:
            pass
        
    for topic, data in datasets.items():
        df = pd.concat(data)
        if topic == 'county_names' or topic == 'county_data':
            df_2004 = df.xs(2008)
        else:
            df_2004 = pd.merge(df.xs(2000), df.xs(2008),on='FIPS', suffixes=('_2000', '_2008'))
            for col in df.columns:
                df_2004[col] = (5 * df_2004[col + '_2000'].astype(float) + 4 * df_2004[col + '_2008'].astype(float)) / 9
        df_2004.loc[: ,'YEAR'] = 2004
        df_2004 = df_2004.reset_index().set_index(['YEAR', 'FIPS'])
        df_2004 = df_2004[df.columns]
        df = pd.concat([df, df_2004])
        df.to_csv(f'./data/{topic}.csv')



if __name__ == '__main__':
    years = [2000, 2009, 2012, 2016]
    funs = [generate_county_data_file, 
            generate_household_income_file, 
            generate_median_income_file, 
            generate_population_file, 
            generate_education_file,
            generate_race_ethnicity_file,
            generate_household_types_file,
            generate_age_file]

    generate_files(years, funs)

    topics = ['county_data', 'education', 'population', 'race_and_ethnicity', 'households', 'income', 'median_income', 'ages']
    combine_files_into_topics(topics)



