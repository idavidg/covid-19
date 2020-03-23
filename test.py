#
#  curl https://raw.githubusercontent.com/necsi/database/master/mapping-data/ne_count18.json > ne_count18.json

import json
from pandas.io.json import json_normalize
data = json.load(open('ne_count18.json'))
json_normalize(data, max_level=2)

iso_names = pd.read_csv('iso_names.csv')


#
import pandas as pd
# https://raw.githubusercontent.com/necsi/database/master/traveldataviz/NECSI-TRAVELDATAVIZ-20200319-1957.csv
travel_df = pd.read_csv('NECSI-TRAVELDATAVIZ-20200319-1957.csv')
# travel_df = pd.read_json('NECSI-TRAVELDATAVIZ-20200309-1846.old.json').T
travel_df['DATE']=pd.to_datetime(travel_df.DATE1, format='%Y-%m-%d', errors='coerce')
travel_df['date_string']=travel_df.DATE.astype(str)
travel_df['day_of_year'] = travel_df['DATE'].dt.dayofyear + (travel_df['DATE'].dt.year - 2019) * 365
travel_df['day_of_year'] = travel_df['day_of_year'].astype(int) 
travel_df = travel_df.sort_values('day_of_year')
travel_df = travel_df[1:]
min_day = travel_df['day_of_year'].min()
travel_df['day_of_year'] = travel_df['day_of_year'] - min_day
travel_df = travel_df.sort_values('day_of_year').reset_index(drop=True)

names = pd.DataFrame(['Malaysia', 'Taiwan', 'Japan', 'Thailand', 'Singapore',
       'Italy', 'Germany', 'France', 'Spain', 'Indonesia', 'Iran',
       'Egypt', 'US', 'Argentina', 'Latvia', 'Austria',
       'United Arab Emirates', 'Switzerland', 'Albania', 'Ecuador',
       'India', 'Ireland', 'Bahrain', 'United Kingdom', 'Portugal'], columns=['Country'])
more_names =  names.merge(iso_names, on='Country')[['Country', 'Alpha 2']].set_index('Country')['Alpha 2'].to_dict()
iso_map = {'Taiwan': 'TW', 'Italy':'IT', 'China':'CN', 'USA/CO':'US', 'USA/CA':'US', 'USA/NY':'US', 'USA/WA':'US', 'USA/FL':'US'}
iso_map.update(more_names)
travel_df['FROM'] = travel_df['FROM'].apply(lambda x: iso_map.get(x) if iso_map.get(x) else x)
travel_df['TO'] = travel_df['TO'].apply(lambda x: iso_map.get(x) if iso_map.get(x) else x)

travel_df = travel_df.groupby('day_of_year').apply(lambda x: x.drop(['day_of_year'], axis=1).set_index('FROM').to_dict(orient='index'))
travel_df.to_json('NECSI-TRAVELDATAVIZ-20200319-1957.json', orient='index')
#



policy_df = pd.read_csv('NECSI-TRAVELDATAVIZ-POLICYACT-20200321-1733.csv')
policy_df['DATE']=pd.to_datetime(policy_df.date1, format='%Y-%m-%d', errors='coerce')
policy_df['day_of_year'] = policy_df['DATE'].dt.dayofyear + (policy_df['DATE'].dt.year - 2019) * 365
policy_df['day_of_year'] = policy_df['day_of_year'].astype(int) 
policy_df['day_of_year'] = policy_df['day_of_year'] - min_day
names = policy_df[['country']].drop_duplicates()
more_names =  names.merge(iso_names, left_on='country', right_on='Country')[['Country', 'Alpha 2']].set_index('Country')['Alpha 2'].to_dict()
iso_map = {'Taiwan': 'TW', 'Italy':'IT', 'China':'CN', 'USA/CO':'US', 'USA/CA':'US', 'USA/NY':'US', 'USA/WA':'US', 'USA/FL':'US', 'United Kingdom of Great Britain & Northern Ireland': 'UK', 'Iran (Islamic Republic of)': 'IR'}
iso_map.update(more_names)
policy_df['country'] = policy_df['country'].apply(lambda x: iso_map.get(x) if iso_map.get(x) else x)

policy_df = policy_df.drop(['alltext', 'text'], axis=1)
policy_df = policy_df.groupby('day_of_year').apply(lambda x: x.drop(['day_of_year'], axis=1).set_index('country').to_dict(orient='index'))
policy_df.to_json('policy_act.json', orient='index')

######### 
# - retrieve time series from: 
# https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_19-covid-Confirmed.csv
time_df = pd.read_csv('time_series_19-covid-Confirmed.csv')
cols = ['Province/State', 'Country/Region', 'Lat', 'Long']
ind = list(time_df.columns.drop(cols).values)

# arg should be a pivot_table...
dfs = []
for col in ind:
    a = time_df[cols + [col]].copy()
    a.loc[:, 'ind'] = col
    a = a.rename(columns={col:'count'})
    dfs.append(a)

time_df=pd.concat(dfs)
time_df=time_df.reset_index(drop=True)
time_df['DATE']=pd.to_datetime(time_df['ind'], format='%m/%d/%y', errors='coerce')
time_df['date_string']=time_df.DATE.astype(str)
time_df['day_of_year'] = time_df['DATE'].dt.dayofyear + (time_df['DATE'].dt.year - 2019) * 365
time_df['day_of_year'] = time_df['day_of_year'].astype(int) 
# keep the min_day from above
time_df['day_of_year'] = time_df['day_of_year'] - min_day
time_df = time_df.drop(['Lat', 'Long'], axis=1)

names = time_df[['Country/Region']].drop_duplicates()
more_names =  names.merge(iso_names, left_on='Country/Region', right_on='Country')[['Country', 'Alpha 2']].set_index('Country')['Alpha 2'].to_dict()
iso_map = {'Taiwan': 'TW', 'Italy':'IT', 'China':'CN', 'USA/CO':'US', 'USA/CA':'US', 'USA/NY':'US', 'USA/WA':'US', 'USA/FL':'US', 'United Kingdom of Great Britain & Northern Ireland': 'UK', 'Iran (Islamic Republic of)': 'IR'}
iso_map.update(more_names)
time_df['Country/Region'] = time_df['Country/Region'].apply(lambda x: iso_map.get(x) if iso_map.get(x) else x)

time_df = time_df.groupby(['day_of_year', 'Country/Region']).sum().reset_index()


# calculate C & g
# Lets try to set an algorithm based upon the fractional change per day in new cases g = (Delta C/C) where C is the number of new cases 
#   (so this is a second order difference_, averaged over past three days (use weighting 1/4, 1/4, 1/2). 

def calc_g(grp):
    a = grp.copy().reset_index()
    a['c1'] = a['count'].shift(1)
    a['d1'] = a['count'] - a['c1']
    a['d2'] = a['d1'].shift(1)
    a['d3'] = a['d1'].shift(2)
    a['C'] = (a['d1'] * 0.5) + (a['d2'] * 0.25) + (a['d3'] * 0.25)
    a['g'] = (a['C'] - a['C'].shift(1)) / a['C']
    a = a.drop(['c1', 'd1', 'd2', 'd3'], axis=1)
    return a

new_time = time_df.groupby(['Country/Region']).apply(calc_g)
#new_time = new_time.drop('index', axis=1)
#new_time[new_time['Country/Region'] == 'CN']

new_time = new_time.groupby('day_of_year').apply(lambda x: x.drop(['day_of_year'], axis=1).set_index('Country/Region').to_dict(orient='index'))
#.to_dict()
#new_time = new_time.sort_values('day_of_year').reset_index(drop=True)
new_time.to_json('time_series_19-covid-Confirmed.json', orient='index')



#### 

import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import matplotlib.cm as cm
import numpy as np

travel_point=travel_df[['TO_lat', 'TO_lon', 'FROM_lat', 'FROM_lon']].iloc[10]
points =  [ [travel_point.FROM_lat, travel_point.FROM_lon],
                        [travel_point.TO_lat, travel_point.TO_lon] ]

points =  [ [travel_point.FROM_lat, travel_point.TO_lat ], 
            [travel_point.FROM_lon, travel_point.TO_lon] ]

xd = (travel_point.FROM_lat - travel_point.TO_lat) / 9
yd = (travel_point.FROM_lon - travel_point.TO_lon) / 9

x =  [ travel_point.FROM_lat, 
             travel_point.FROM_lat - xd,      
             travel_point.TO_lat + xd,      
             travel_point.TO_lat   ]
y = [ travel_point.FROM_lon, 
            travel_point.FROM_lon - yd,
            travel_point.TO_lon + yd,
            travel_point.TO_lon ]


fig = plt.figure()
ax = fig.add_subplot(111)

xc = np.arange(10)
ys = [i+xc+(i*xc)**2 for i in range(10)]
colors = cm.rainbow(np.linspace(0, 1, len(ys)))

for i, v in enumerate(x):
    line = Line2D(x[i:i+2], y[i:i+2])
    line.set_color(colors[i])
    ax.add_line(line)

ax.set_xlim(min(x), max(x))
ax.set_ylim(min(y), max(y))

plt.show()

####
