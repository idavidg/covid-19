#
import pandas as pd
df = pd.read_json('NECSI-TRAVELDATAVIZ-20200309-1846.old.json').T
df['DATE']=pd.to_datetime(df.DATE, format='%d.%m.%Y', errors='coerce')
df['date_string']=df.DATE.astype(str)
df['day_of_year'] = df['DATE'].dt.dayofyear + (df['DATE'].dt.year - 2019) * 365
df['day_of_year'] = df['day_of_year'] - df['day_of_year'].min()
df = df.sort_values('day_of_year').reset_index(drop=True).dropna()

df.to_json('NECSI-TRAVELDATAVIZ-20200309-1846.json', orient='index')


