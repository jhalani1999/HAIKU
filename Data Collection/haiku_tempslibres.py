import time
from tqdm import tqdm
from bs4 import BeautifulSoup
import pandas as pd
import requests

source = requests.get("http://www.tempslibres.org/tl/tlphp/dbauteursl.php?lang=en&lg=e").text
soup = BeautifulSoup(source, 'html.parser')

links = []
# print(soup.find('table').find_all('td', class_ = 'liensurl'))

# getting links for haiku
for link in soup.find('table').find_all('td', class_ = 'liensurl'):
    links.append(link.a.get('href'))
    
haiku = []

for l in tqdm(links):
    link = 'http://www.tempslibres.org/tl/tlphp/' + l
    sou = requests.get(link).text
    soup = BeautifulSoup(sou, 'html.parser')    
    for h in soup.find_all('p', class_ = 'haiku'):
        haiku.append(h.get_text().splitlines())
        
#%%
        
import numpy as np 

length = []
    
for h in haiku:
    length.append(len(h))
    
print(np.unique(np.array(length)))
        
#%%
        
for i in range(len(haiku)-1):
    if len(haiku[i]) == 3:
        pass
    elif len(haiku[i])==7:
        pass
    else:
        haiku.pop(i)

#%%
        
final = []

for i in range(len(haiku)):
    if len(haiku[i])==7:
        final.append(haiku[i][:3])
        final.append(haiku[i][4:])
    else:
        final.append(haiku[i])
        
#%%
        
length = []
    
for h in final:
    length.append(len(h))
    
print(np.unique(np.array(length)))

#%%
haikus2 = final[:11676]
haikus3 = []
for haiku in haikus2:
    try:
        haikus3.append([line.encode('latin1').decode('utf-8') for line in haiku])
    except:
        print(haiku)
    
df = pd.DataFrame.from_records(haikus3)
df['haiku'] = df.apply(lambda r: '\n'.join([l for l in r[0:9] if l]), axis=1)

from langdetect import detect
df['lang'] = df['haiku'].apply(lambda h: detect(h))

#%%
filters = df[1] != ""
df = df[filters]
df['source'] = 'tempslibres'
df_en = df[df['lang']=='en']

#%%

df_en.to_csv('haiku_en_tempslibres.csv')
