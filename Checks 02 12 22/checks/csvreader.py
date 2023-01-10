import pandas as pd

df = pd.read_csv('C:/Users/begku/Desktop/sell Data/2020-21.csv',sep=';', encoding='ANSI') 

data=data.rename(columns={'Номенклатура': 'name', 'Код':'idtov',
       'Документ продажи.Номер':'iddoc', 'Количество':'count','Цена':'price','Сумма':'summa'})

data['return'] = ''
data['kassa'] = ''

data['summa'] = data['summa'].replace(' ','', regex=True)
data['summa'] = data['summa'].replace(',','.', regex=True).astype(float)
#print(data.sort_values(by = ['summa'], ascending=False))

tovs = data.groupby(['idtov']).sum() #общее кол-во товаров по id товара
tovs['number_of_units_sold'] = data.groupby(['idtov']).size()
tovs = tovs.sort_values(by = ['summa'], ascending=False)

