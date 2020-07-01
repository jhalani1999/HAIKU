import pandas as pd

df_gut = pd.read_csv('gutenberg.csv')
df_gut = df_gut['haiku'].str.split('\n', expand=True)
df_gut['source'] = 'gutenberg'
df_gut.to_csv('haiku_gutenberg.csv')

#%%

df_twaiku = pd.read_csv('twaikugc.csv')
df_twaiku = df_twaiku[df_twaiku['id_str'] >= 941376356746702848] # After the account was out of testing

df_twaiku = df_twaiku['text'].str.split(r'\n+', expand=True)
df_twaiku = df_twaiku.drop(3, axis=1)

df_twaiku[0] = df_twaiku[0].str.strip().str.strip('"')
df_twaiku[2] = df_twaiku[2].str.strip().str.strip('"')

df_twaiku['source'] = 'twaiku'

df_twaiku.to_csv('haiku_twaiku.csv')

