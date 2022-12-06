import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D 
from sklearn import datasets
from sklearn.cluster import KMeans
from sklearn import preprocessing
from tqdm import tqdm_notebook
from scipy.cluster.hierarchy import linkage, dendrogram
import time


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

dfStr = pd.read_csv('checks_str.txt', sep='\t')
dfTitles = pd.read_csv('checks_titles.txt', sep='\t')
names = pd.read_csv('id.txt', sep='\t', names=['idtov','name'])
data = pd.merge(dfStr, names, on='idtov')

data = pd.merge(dfTitles, data, on='iddoc' )
data.head()
# data['idtov'] = data['idtov'].astype(str)
# data.head(100)
# print(data.shape)
# for indx, tmp in data.iterrows():
#     if type(data['idtov'][indx]) != str:
#         print(type(data['idtov'][indx]))

# names = pd.read_csv('id.csv', sep='\t', names=['idtov','name'])
# # names['idtov'] = names['idtov'].astype(str)
# print(names.head())
# names.head()
# type(names['idtov'][0])

# data.join(names, on ='idtov')
# data.head()

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
checks.head()

trainDF = pd.DataFrame(checks[:train_count])
train = trainDF.values


#описываем модель
model = KMeans(n_clusters = num_clusters)

#проводим моделирование
time1 = time.time()
model.fit(train)
time2 = time.time()
print((time2-time1)*1000.0)

#предсказания
all_predictions = model.predict(train)

x_axis = train[:plotted_point_count, 0]
y_axis = train[:plotted_point_count, 1]
z_axis = train[:plotted_point_count, 2]
fig = plt.figure(figsize=(8, 8))
ax = fig.add_subplot(111, projection='3d')
ax.set_xlabel(xlabel="kolvo")
ax.set_ylabel(ylabel="summa")
ax.set_zlabel(zlabel="unique")
ax.scatter(x_axis, y_axis, z_axis, c=all_predictions[:plotted_point_count])

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
 
plt.show()

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

x_axis = train[:plotted_point_count, 0]
y_axis = train[:plotted_point_count, 1]
z_axis = train[:plotted_point_count, 2]
fig = plt.figure(figsize=(18, 16))
ax = fig.add_subplot(111, projection='3d')
ax.set_xlabel(xlabel="kolvo")
ax.set_ylabel(ylabel="summa")
ax.set_zlabel(zlabel="unique")
ax.scatter(x_axis, y_axis, z_axis, c=all_predictions[:plotted_point_count])

dfrm = pd.Series({'predicted':all_predictions})
trainDF['predicted'] = dfrm['predicted']
trainDF.head(15)

testCheck = pd.DataFrame(checks[train_count+10:train_count+11])
pred = model.predict(testCheck.values)
print(pred)
print(testCheck.head())

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

print(testCheck.shape)
for index, t in testCheck.iterrows():
    closest = model.predict(np.array([t.values]))
    ax.scatter(t['kolvo'], t['summa'], t['count_uniq_good'], c=col[closest[0]])
    similar_checks = pd.DataFrame(trainDF[trainDF['predicted']==closest[0]])
    check_content = pd.DataFrame(data[data["iddoc"]==index])
    
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
#     print(b)

summ = pd.merge(summ, names, on='idtov')
summ.head()

for index, tov in check_content.iterrows():
    summ = summ[summ.idtov != tov.idtov]
summ = summ.sort_values(by = ['count_good'], ascending=False)
# print(summ)
summ.head(15)