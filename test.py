#
import pandas as pd
df = pd.read_csv('NECSI-TRAVELDATAVIZ-20200309-1846.csv')
pd.to_datetime(df.DATE)

df.to_json('NECSI-TRAVELDATAVIZ-20200309-1846.json', orient='index')


