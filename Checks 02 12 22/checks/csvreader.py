import pandas as pd

data = pd.read_csv('C:/Users/begku/Desktop/sell Data/2020-21-edited.csv',sep=',', encoding='utf-8',low_memory=False) 

data['summa'] = data['summa'].replace(' ','', regex=True)
data['summa'] = data['summa'].replace(',','.', regex=True).astype(float)

data['count'] = data['count'].replace(' ','', regex=True)
data['count'] = data['count'].replace(',','.', regex=True).astype(float)

data['price'] = data['price'].replace(' ','', regex=True)
data['price'] = data['price'].replace(',','.', regex=True).astype(float)
#print(data.sort_values(by = ['summa'], ascending=False))

print(data['price'][1]*data['count'][1])
print(data['summa'][1])

ch = data.groupby(['iddoc']).sum()
#print(data.keys())
ch['count_uniq_good'] = data.groupby(['iddoc']).size()
