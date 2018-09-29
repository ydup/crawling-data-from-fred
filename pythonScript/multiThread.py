import time, threading

from fredapi import Fred
import pandas as pd
from tqdm import tqdm
import numpy as np
fred = Fred(api_key='APIkey')
treeDF = pd.read_csv('../data/cateTree.csv', index_col=0)
treeDF.index = range(treeDF.shape[0])
# Divide the task into multi threads
totalWork = treeDF.shape[0]
threadNum = 10
# How many data to be crawled in the single thread
singleWork = int((totalWork+threadNum)/threadNum)

def download(rangeCato, name):
    print 'thread %s is running...' % threading.current_thread().name
    allData = []
    dataInfo = []
    error = []
    for index in rangeCato:
        if index < treeDF.shape[0]:
            try:
                popu = fred.search_by_category(treeDF.loc[index, 'cate3Index'], limit=10, order_by='popularity', sort_order='desc')
                for detailIndex, detialValues in popu.iterrows():
                    allData.append(pd.DataFrame(fred.get_series(detailIndex), columns=[detailIndex]))
                allDataIn = pd.concat(allData, axis=1)
                allDataIn.to_csv('../data/allData'+name+'.csv')
            except:
                print treeDF.loc[index, 'cate3Index'], 'can not be found'
                error.append(treeDF.loc[index, 'cate3Index'])
                np.savetxt('../data/errorLog'+name+'.csv',error,delimiter=',')
    print 'thread %s ended.' % threading.current_thread().name

threadList = [threading.Thread(target=download, args=(range(index*threadNum, (index+1)*threadNum), str(index),), name='DownloadThread'+str(index)) for index in range(threadNum)]

for index, value in enumerate(threadList):
    value.start()
for index, value in enumerate(threadList):
    value.join()