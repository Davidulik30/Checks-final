import pandas as pd

df = pd.read_csv('C:/Users/begku/Desktop/sell Data/2020-21.csv',sep=';', encoding='ANSI') 

df=df.rename(columns={'Номенклатура': "name", 'Код':"idtov",
       'Документ продажи.Номер':"iddoc", 'Количество':"count",'Цена':"price",'Сумма':"summa"})

print(df.head(5))

print(df.keys())

#print(df["Цена"].to_list())
