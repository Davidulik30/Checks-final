#---------------------------- Запускать этот фаил ----------------------------
from tabnanny import check
import pandas as pd
import numpy as np
from sklearn import datasets
from sklearn.cluster import KMeans
from sklearn import preprocessing
#from sympy import content
from tqdm import tqdm_notebook
from scipy.cluster.hierarchy import linkage, dendrogram
import time
from flask import Flask, request
import json
import positions
from main import delete_check, get_check, insert_check, read_content,get_tov_price,token_check,auth_check

num_clusters = 6
train_count = 10000
plotted_point_count = 500

def timing(f):
    def wrap(*args):
        time1 = time.time()
        ret = f(*args)
        time2 = time.time()
        print('{:s} function took {:.3f} ms'.format(f.__name__, (time2-time1)*1000.0))
        return ret
    return wrap

#Функция обновления данных 

def checks_update():
    train_count = 10000
    dfStr = pd.DataFrame(read_content()) #Считать из БД чеки
    #dfStr = pd.read_csv('./checks_str.txt', sep='\t') # Считать из фаила txt
    dfTitles = pd.read_csv('C:/Users/Admin/Documents/GitHub/Checks-final/Checks 02 12 22/checks/checks_titles.txt', sep='\t') #Перенести в бд
    names = pd.read_csv('C:/Users/Admin/Documents/GitHub/Checks-final/Checks 02 12 22/checks/id.txt', sep='\t', names=['idtov','name']) #Перенести в бд
    data = pd.merge(dfStr, names, on='idtov')
    print (dfStr)
    data = pd.merge(dfTitles, data, on='iddoc' )
    data.head()

    #number_of_units_sold -  количество проданных единиц 
    tovs = data.groupby(['idtov']).sum() #общее кол-во товаров по id товара
    tovs['number_of_units_sold'] = data.groupby(['idtov']).size()
    tovs = tovs.sort_values(by = ['summa'], ascending=False)
    tovs.head()

    ch = data.groupby(['iddoc']).sum()
    ch['count_uniq_good'] = data.groupby(['iddoc']).size()

    checks = ch.drop(columns=["return","kassa","price"])
    checks = checks[checks['count_uniq_good'] > 2]
    checks = checks[checks['summa'] > 0]
    checks.head()

   #нормализация данных
    checks = pd.DataFrame(preprocessing.normalize(checks, axis=0), index = checks.index.values)
    checks.columns=["kolvo","summa","count_uniq_good"]
    print(checks.loc[checks.index=="240T4"]) #227G1
    checks.head(10)
    trainDF = pd.DataFrame(checks[:train_count])
    train = trainDF.values

    #описываем модель
    num_clusters = 6
    model = KMeans(n_clusters = num_clusters)

    #проводим моделирование
    time1 = time.time()
    model.fit(train)
    time2 = time.time()
    print((time2-time1)*1000.0)

    #предсказания
    all_predictions = model.predict(train)

    #сгенерировать матрицу связей

    #проводим моделирование
    time1 = time.time()
    mergings = linkage(train, method='ward')
    time2 = time.time()
    print((time2-time1)*1000.0)


    dendrogram(mergings,
            truncate_mode='lastp',
            show_leaf_counts=False,
            leaf_rotation=90,
            leaf_font_size=12,
            show_contracted=True,)
    
    from sklearn.cluster import DBSCAN
    from sklearn.decomposition import PCA

    # Определяем модель
    dbscan = DBSCAN(eps=0.0005, min_samples=100)
    
    # Обучаем
    time1 = time.time()
    dbscan.fit(trainDF)
    time2 = time.time()
    print((time2-time1)*1000.0)
    all_predictions = dbscan.labels_

    # a = sorted(dbscan.labels_)
    # for i in range(0, len(a)):
    #     print(a[i])

    dfrm = pd.Series({'predicted':all_predictions})
    trainDF['predicted'] = dfrm['predicted']
    trainDF.head(15)
    print ("mark 112 data.loc index>>>>>>>>>>>>>>:")
    print(checks.loc[checks.index=='TestCheck'])
    print ("mark 114 data.loc index end<<<<<<<<<<<<<<<:")
    return checks,trainDF,data,model,names

#Функция получения рекомендаций
def get_rec(check,rec_count):
    num_clusters = 6
    checks,trainDF,data,model,names = checks_update()
    #testCheck = pd.DataFrame(checks.loc[checks.index==check_id])
    summ = pd.DataFrame()
    testCheck = checks.loc[checks.index==check]
    #testCheck = pd.DataFrame(checks[train_count+9:train_count+10])
    #pred = model.predict(testCheck.values)
    #print(check_id)
    # print(pred)
    # print("testCheck:")
    # print(pd.DataFrame(checks[train_count+8:train_count+9]))
    # print("check ended")
    # print(pd.DataFrame(checks.loc[checks.index==check_id]))
    # print(checks.loc[checks.index==check_id])
    # print("checks.index")
    # print(testCheck)
    # print("testCheck end")
    
    test_check_content = pd.DataFrame(data[data['iddoc'].isin(testCheck.index.values)])
    
    test_check_content.head()
    
    group = trainDF[trainDF['predicted']==1]
    group.shape

    c = []
    for i in range(num_clusters):
        group = trainDF[trainDF['predicted']==i]
        c.append(group.mean().values[:-1])
    # print(c)

    col = ['r','g','b','m', 'y', 'c']
    a = []
    
    print("mark:testCheck.shape")
    print(testCheck.shape)
    
    for index, t in testCheck.iterrows():
        closest = model.predict(np.array([t.values]))
        similar_checks = pd.DataFrame(trainDF[trainDF['predicted']==closest[0]])
        check_content = pd.DataFrame(data[data["iddoc"]==index])
        print(t.values)
        #получить все товары из похожих чеков
        train_tov = pd.DataFrame(data[data['iddoc'].isin(similar_checks.index.values)])

        
        for check_inedx, tovar in check_content.iterrows():
            #отбираем все те чеки в которых встречаются эти товары
            a.append(train_tov[train_tov['idtov'] == tovar['idtov']])             
        a = pd.concat(a)
        a = pd.DataFrame(a.groupby(['iddoc']).size().reset_index(name='count'))
        a = a.sort_values(by=['count', 'iddoc'], ascending=False)
        
        b = []
        for ind, k in a.iterrows():
            t = pd.DataFrame(data[data["iddoc"]==a.iloc[ind]['iddoc']])
            b.extend(t.values)
            
        b = pd.DataFrame(b, columns = data.columns)
        summ = b.groupby(['idtov']).sum()
        summ['count_good'] = b.groupby(['idtov']).size()
        summ = summ.sort_values(by = ['count_good'], ascending=False)
    
    print ("mark 182 summ:")
    print (summ)
    
    summ = pd.merge(summ, names, on='idtov')
    summ.head()

    for index, tov in check_content.iterrows():
        summ = summ[summ.idtov != tov.idtov]
    summ = summ.sort_values(by = ['count_good'], ascending=False)
    print("WORKES")
    summ = summ.rename(columns={"return": "ret"})
    print(summ.to_dict(orient='records'))
    # result = [positions.Positions(**kwargs) for kwargs in summ.to_dict(orient='records')]
    return json.dumps(summ[:rec_count].to_dict(orient="records"),indent=1), 200, {'Content-Type': 'application/json; charset=utf-8'}
    #summ.to_json(orient="split"), 200, {'Content-Type': 'application/json; charset=utf-8'}

#print(get_rec("228EQ"))#240T3
print("Start server:")

app = Flask(__name__)
print(__name__)

@app.route('/auth',methods=['POST'])
def authorization_check():
    content = request.get_json()
    return auth_check(content)


@app.route('/get_recomendation',methods=['POST'])
def show_rec_check():
    content = request.get_json()
    print(token_check(content["token"]))
    if(token_check(content["token"])):
        delete_check("TestCheck")
        iddoc_example=None
        for iddoc in content["tov_content"]:
            iddoc["price"] = get_tov_price(iddoc["idtov"])[0]["MAX(price)"]
            iddoc["summa"] = iddoc["price"]*iddoc["count"]
            iddoc_example=iddoc["iddoc"]
            print(iddoc_example)
        if iddoc_example=="TestCheck":
            insert_check(content["tov_content"])
            print ("mark:")
            print (type("TestCheck"))
            return get_rec("TestCheck",content["rec_count"])
        else: 
            return "none"
    else:
        return "not valid token"

@app.route('/get_check/<check>',methods=['GET'])
def show_check(check):
    return get_check(check)
    #return json.dumps(get_check(check)), 200, {'Content-Type': 'application/json; charset=utf-8'}

@app.route('/add_check',methods=['POST'])
def post_check():
    content = request.get_json()
    #insert_check(content)
    return insert_check(content)

@app.route('/delete_check/<check>',methods=['DELETE'])
def delete_checks(check):
    delete_check(check)
    return "Check deleted!"

@app.route('/update_db',methods=['POST'])
def update_db():
    checks_update()
    return 0
    
if __name__ == '__main__':
    app.run()#host='162.55.190.16',port=53
