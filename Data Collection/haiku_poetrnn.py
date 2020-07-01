import pandas as pd


df = pd.read_csv('haiku_poetrnn.csv', names=["haiku"])

df = df['haiku'].str.split('\n', expand=True)

# Drop ones without at least three lines
df = df.dropna(subset=[0,1,2])

# Keep only the ones with exactly three lines
df = df[(((df[3] == '') | pd.isnull(df[3])) & pd.isnull(df[[4, 5, 6, 7, 8]]).all(axis=1))]


df = df[[0, 1, 2]]
df['source'] = 'sballas'

df.to_csv("haiku_poetrnn.csv")