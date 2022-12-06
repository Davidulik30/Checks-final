import string
from tracemalloc import stop
import pymysql
import pandas as pd
from sklearn import preprocessing
from sympy import false, true
from torch import NoneType
from config import host,user,password,db_name
import json



def set_connection():
    connection = pymysql.connect(
        host=host,
        port=8080,
        user=user,
        password=password,
        database=db_name,
        cursorclass=pymysql.cursors.DictCursor

        )
    return connection

def insert_check(check):

    connection=set_connection()
    try:
    #cursor=connection.cursor()
        with connection.cursor() as cursor:
            insert_query ="SELECT COUNT(*) FROM `test_checks_table` WHERE iddoc = %s"
            cursor.execute(insert_query,check["iddoc"])
            connection.commit()
                 
    finally:
            connection.close()    
             
    is_exist = cursor.fetchone()
    print(is_exist["COUNT(*)"])
    if is_exist["COUNT(*)"]==0:
            connection=set_connection()
            
            try:
            #cursor=connection.cursor()
                  with connection.cursor() as cursor:
                        insert_query = "INSERT INTO `test_checks_table` (iddoc,idtov,count,price,summa) VALUES (%s,%s,%s,%s,%s)"
                        cursor.execute(insert_query,( check["iddoc"],check["idtov"],check["count"],check["price"],check["summa"]))
                        connection.commit()
                        print("Check %s inserted!" % check["iddoc"])
                        
            finally:
                    connection.close()
                    print("ADDED!")
                    return "Check added!"
    else:
            print("EXIST")
            return "Already exist"

insert_check({
    "iddoc":"2eR",
    "idtov":"KAKAO1aaweq",
    "count":"32",
    "price":"300",
    "summa":"900"
})