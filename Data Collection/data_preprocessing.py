import pandas as pd
import re

df_temps = pd.read_csv('haiku_en_tempslibres.csv')
df_img2 = pd.read_csv('haiku_img2poems.csv')
df_poet = pd.read_csv('haiku_poetrnn.csv')
df_gut = pd.read_csv('haiku_gutenberg.csv')
df_twaiku = pd.read_csv('haiku_twaiku.csv')


df_temps = df_temps.drop(['Unnamed: 0', 'haiku', 'lang'], axis=1)
df_temps['source'] = 'tempslibres'
df_img2 = df_img2.drop('Unnamed: 0', axis=1)
df_poet = df_poet.drop('Unnamed: 0', axis=1)
df_gut = df_gut.drop('Unnamed: 0', axis=1)
df_twaiku = df_twaiku.drop('Unnamed: 0', axis=1)

all_haikus = []

all_haikus.append(df_temps)
all_haikus.append(df_img2)
all_haikus.append(df_poet)
all_haikus.append(df_gut)
all_haikus.append(df_twaiku)


#%%
all_haikus = pd.concat(all_haikus, sort=False)

#%%
# Drop duplicates because there are some poems in multiple sources
# all_haikus = all_haikus.rename(columns={'0':'First', '1':'Second', '2':'Third'})
# all_haikus.First.apply(str)
# all_haikus.Second.apply(str)
# all_haikus.Third.apply(str)

all_haikus['hash'] = (all_haikus['0'] + all_haikus['1'] + all_haikus['2']).str.replace(r'[^A-Za-z]', '').str.upper()
all_haikus = all_haikus.drop_duplicates(subset=['hash'])
#%%

all_haikus.to_csv('all_haiku.csv')

#%%

# Standard Dict
WORDS = {}
f = open('cmudict.dict.txt','r')
for line in f.readlines():
    word, phonemes = line.strip().split(' ', 1)
    word = re.match(r'([^\(\)]*)(\(\d\))*', word).groups()[0]
    phonemes = phonemes.split(' ')
    syllables = sum([re.match(r'.*\d', p) is not None for p in phonemes])
    #print(word, phonemes, syllables)
    if word not in WORDS:
        WORDS[word] = []
    WORDS[word].append({
        'phonemes': phonemes,
        'syllables': syllables
    })
        
# Load custom phonemes
CUSTOM_WORDS = {}
vowels = ['AA', 'AE', 'AH', 'AO', 'AW', 'AX', 'AXR', 'AY', 'EH', 'ER', 'EY', 'IH', 'IX', 'IY', 'OW', 'OY', 'UH', 'UW', 'UX']
f = open('custom.dict.txt','r')
for line in f.readlines():
    try:
        word, phonemes = line.strip().split('\t', 1)
    except:
        print(line)
        continue
    word = re.match(r'([^\(\)]*)(\(\d\))*', word).groups()[0].lower()
    phonemes = phonemes.split(' ')
    syllables = sum([(p in vowels) for p in phonemes])
    
    if word not in CUSTOM_WORDS:
        CUSTOM_WORDS[word] = []
    CUSTOM_WORDS[word].append({
        'phonemes': phonemes,
        'syllables': syllables
    })

#%%

import inflect    
inflect_engine = inflect.engine()

# Dictionary of words not found, must go get the phonemes
# http://www.speech.cs.cmu.edu/tools/lextool.html
NOT_FOUND = set()

def get_words(line):
    """
    Get a list of the words in a line
    """
    line = line.lower()
    # Replace numeric words with the words written out
    ws = []
    for word in line.split(' '):
        if re.search(r'\d', word):
            x = inflect_engine.number_to_words(word).replace('-', ' ')
            ws = ws + x.split(' ')
        else:
            ws.append(word)

    line = ' '.join(ws)

    words = []
    for word in line.split(' '):
        word = re.match(r'[\'"]*([\w\']*)[\'"]*(.*)', word).groups()[0]
        word = word.replace('_', '')
        words.append(word)
        
    return words

def count_non_standard_words(line):
    """
    Count the number of words on the line that don't appear in the default CMU Dictionary.
    """
    count = 0
    for word in get_words(line):
        if word and (word not in WORDS):
            count += 1
    return count

def get_syllable_count(line):
    """
    Get the possible syllable counts for the line
    """
    counts = [0]
    return_none = False
    for word in get_words(line):
        try:
            if word:
                if (word not in WORDS) and (word not in CUSTOM_WORDS):
                    word = word.strip('\'')
                    
                if word in WORDS:
                    syllables = set(p['syllables'] for p in WORDS[word])
                else:
                    syllables = set(p['syllables'] for p in CUSTOM_WORDS[word])
                #print(syllables)
                new_counts = []
                for c in counts:
                    for s in syllables:
                        new_counts.append(c+s)

                counts = new_counts
        except:
            NOT_FOUND.add(word)
            return_none = True

    if return_none:
        return None
    
    return ','.join([str(i) for i in set(counts)])

import numpy as np
# Likely either non-english or just lots of typos
all_haikus['unknown_word_count'] = np.sum([all_haikus[i].apply(count_non_standard_words) for i in range(3)], axis=0)
all_haikus = all_haikus[all_haikus['unknown_word_count'] < 3].copy()

for i in range(3):
    all_haikus['%s_syllables' % i] = all_haikus[i].apply(get_syllable_count)
    
print("Unknown Words: ", len(NOT_FOUND))

with open('unrecognized_words.txt', 'w') as f:
    for w in NOT_FOUND:
        f.write(w)
        f.write('\n')


#%%


