import string
from tracemalloc import stop
import pymysql
import pandas as pd
from sklearn import preprocessing
from sympy import false, true
from config import host,user,password,db_name
import json

def set_connection(): #установка соединения
    connection = pymysql.connect(
        host=host, #Указано в конфиге
        port=8080, #Выставить порт БД
        user=user, 
        password=password,
        database=db_name,
        cursorclass=pymysql.cursors.DictCursor

        )
    return connection
#для пользования необходимо выставить названия баз из которых берётся или вносится информация
def insert_check(check): #вставка чека
    iddoc_example=None

    for iddoc in check: 
        iddoc_example=iddoc['iddoc']
    
    connection=set_connection()
    try:
    #cursor=connection.cursor()
        with connection.cursor() as cursor:
            insert_query ="SELECT COUNT(*) FROM `checks_table` WHERE iddoc = %s"
            cursor.execute(insert_query,iddoc_example)
            connection.commit()
                 
    finally:
            connection.close()    

    is_exist = cursor.fetchone()
    print(is_exist["COUNT(*)"])
    
    if is_exist["COUNT(*)"]==0:
            connection=set_connection()
            for str in check:
                print (str["idtov"])
                try:
                #cursor=connection.cursor()
                    with connection.cursor() as cursor:
                            insert_query = "INSERT INTO `checks_table` (iddoc,idtov,count,price,summa) VALUES (%s,%s,%s,%s,%s)"
                            cursor.execute(insert_query,( str["iddoc"],str["idtov"],str["count"],str["price"],str["summa"]))
                            connection.commit()
                            print("Check %s inserted!" % str["iddoc"])
                finally:        
                    print("Check added!")

            connection.close()
    else:
            #connection.close()
            print ("Already exist")

def get_check(check): #считывание конкретного чека
    connection=set_connection()
    try:
    #cursor=connection.cursor()
        with connection.cursor() as cursor:
            insert_query ="SELECT * FROM checks_table WHERE iddoc = (%s)"
            cursor.execute(insert_query,check)
            connection.commit()
            print("Check %s showed!" % check)
    finally:
            connection.close()
    data=json.dumps(cursor.fetchall()), 200, {'Content-Type': 'application/json; charset=utf-8'}
    return data

def read_content(): #считывание чеков
    connection=set_connection()
    try:
    #cursor=connection.cursor()
        with connection.cursor() as cursor:
            insert_query ="SELECT iddoc,idtov,count,price,summa FROM checks_table"
            cursor.execute(insert_query)
            connection.commit()
            print("Data readed!")
    finally:
            connection.close()
    return cursor.fetchall()

def read_content_names(): #считывание наименований
    connection=set_connection()
    try:
    #cursor=connection.cursor()
        with connection.cursor() as cursor:
            insert_query ="SELECT id,name FROM names_table"
            cursor.execute(insert_query)
            connection.commit()
            print("Data readed!")
    finally:
            connection.close()
    return cursor.fetchall()

def delete_check(check): #удаление чека
    connection=set_connection()
    try:
    #cursor=connection.cursor()
        with connection.cursor() as cursor:
            insert_query ="DELETE FROM checks_table WHERE iddoc = (%s)"
            cursor.execute(insert_query,check)
            connection.commit()
            print("Check %s deleted!" % check)
    finally:
            connection.close()

def get_tov_price(tov): #получить цену товара
    connection=set_connection()
    try:
    #cursor=connection.cursor()
        with connection.cursor() as cursor:
            insert_query ="Select MAX(price) from tov_prices where idtov = (%s)"
            cursor.execute(insert_query,tov)
            connection.commit()
            print("Item %s showed!" % tov)
    finally:
            connection.close()
    #data=json.dumps(cursor.fetchall()), 200, {'Content-Type': 'application/json; charset=utf-8'}
    return cursor.fetchall()