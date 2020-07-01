import json
import pandas as pd

f = open('unim_poem.json', 'r')
data = json.loads(f.read())

df = pd.DataFrame({'haiku': [i['poem'] for i in data if len(i['poem'].split('\n')) == 3]})

# Split them into lines
df = df['haiku'].str.split('\n', expand=True)

df['source'] = 'img2poems'

df.to_csv('haiku_img2poems.csv')
