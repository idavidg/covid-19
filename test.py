#
#  curl https://raw.githubusercontent.com/necsi/database/master/mapping-data/ne_count18.json > ne_count18.json

import json
from pandas.io.json import json_normalize
data = json.load(open('ne_count18.json'))
json_normalize(data, max_level=2)


#
import pandas as pd
# https://raw.githubusercontent.com/necsi/database/master/traveldataviz/NECSI-TRAVELDATAVIZ-20200319-1957.csv
travel_df = pd.read_csv('NECSI-TRAVELDATAVIZ-20200319-1957.csv')
# travel_df = pd.read_json('NECSI-TRAVELDATAVIZ-20200309-1846.old.json').T
travel_df['DATE']=pd.to_datetime(travel_df.DATE1, format='%Y-%m-%d', errors='coerce')
travel_df['date_string']=travel_df.DATE.astype(str)
travel_df['day_of_year'] = travel_df['DATE'].dt.dayofyear + (travel_df['DATE'].dt.year - 2019) * 365
min_day = travel_df['day_of_year'].min()
travel_df['day_of_year'] = travel_df['day_of_year'] - min_day
travel_df = travel_df.sort_values('day_of_year').reset_index(drop=True)
travel_df.loc[travel_df['FROM'] == 'USA/WA', 'FROM'] = 'US'
travel_df.loc[travel_df['TO'] == 'USA/WA', 'TO'] = 'US'
travel_df.loc[travel_df['FROM'] == 'China', 'FROM'] = 'CN'
travel_df.loc[travel_df['TO'] == 'China', 'TO'] = 'CN'
travel_df.loc[travel_df['FROM'] == 'Italy', 'FROM'] = 'IT'
travel_df.loc[travel_df['TO'] == 'Italy', 'TO'] = 'IT'
travel_df.to_json('NECSI-TRAVELDATAVIZ-20200319-1957.json', orient='index')
#



policy_df = pd.read_csv('NECSI-TRAVELDATAVIZ-POLICYACT-20200321-1733.csv')
policy_df['DATE']=pd.to_datetime(policy_df.date1, format='%Y-%m-%d', errors='coerce')
policy_df['day_of_year'] = policy_df['DATE'].dt.dayofyear + (travel_df['DATE'].dt.year - 2019) * 365
policy_df['day_of_year'] = policy_df['day_of_year'] - min_day
policy_df.loc[policy_df['country'] == 'United States of America', 'country'] = 'US'
policy_df.loc[policy_df['country'] == 'China', 'country'] = 'CN'
policy_df.loc[policy_df['country'] == 'Italy', 'country'] = 'IT'
policy_df.loc[policy_df['country'] == 'United Kingdom of Great Britain & Northern Ireland', 'country'] = 'UK'
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
# keep the min_day from above
time_df['day_of_year'] = time_df['day_of_year'] - min_day
time_df = time_df.drop(['Lat', 'Long'], axis=1)
time_df.loc[time_df['Country/Region'] == 'China', 'Country/Region'] = 'CN'
time_df.loc[time_df['Country/Region'] == 'Italy', 'Country/Region'] = 'IT'
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
