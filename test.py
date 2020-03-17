#
import pandas as pd
df = pd.read_csv('NECSI-TRAVELDATAVIZ-20200311-0247.csv')
# df = pd.read_json('NECSI-TRAVELDATAVIZ-20200309-1846.old.json').T
df['DATE']=pd.to_datetime(df.DATE1, format='%Y-%m-%d', errors='coerce')
df['date_string']=df.DATE.astype(str)
df['day_of_year'] = df['DATE'].dt.dayofyear + (df['DATE'].dt.year - 2019) * 365
min_day = df['day_of_year'].min()
df['day_of_year'] = df['day_of_year'] - min_day
df = df.sort_values('day_of_year').reset_index(drop=True)

df.to_json('NECSI-TRAVELDATAVIZ-20200309-1846.json', orient='index')

######### 
# - retrieve time series from: 
# https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_19-covid-Confirmed.csv
df = pd.read_csv('time_series_19-covid-Confirmed.csv')
cols = ['Province/State', 'Country/Region', 'Lat', 'Long']
ind = list(df.columns.drop(cols).values)

# arg should be a pivot_table...
dfs = []
for col in ind:
    a = df[cols + [col]].copy()
    a.loc[:, 'ind'] = col
    a = a.rename(columns={col:'count'})
    dfs.append(a)

df=pd.concat(dfs)
df=df.reset_index(drop=True)
df['DATE']=pd.to_datetime(df['ind'], format='%m/%d/%y', errors='coerce')
df['date_string']=df.DATE.astype(str)
df['day_of_year'] = df['DATE'].dt.dayofyear + (df['DATE'].dt.year - 2019) * 365
# keep the min_day from above
df['day_of_year'] = df['day_of_year'] - min_day
df = df.sort_values('day_of_year').reset_index(drop=True)

df.to_json('time_series_19-covid-Confirmed.json', orient='index')
