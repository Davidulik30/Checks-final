import pandas as pd

df = pd.read_csv('C:/Users/Admin/Desktop/sell Data/2020-21.csv',sep='|', encoding='ANSI') 

ch = df.drop(columns='Цена')

for col in ch.columns:
    print (col)
    #print(df.to_string())


        