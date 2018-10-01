import time, threading

from fredapi import Fred
import pandas as pd
from tqdm import tqdm
import numpy as np
fred = Fred(api_key='APIkey')
treeDF = pd.read_csv('cateTree.csv', index_col=0)
treeDF.index = range(treeDF.shape[0])
# Divide the task into multi threads
totalWork = treeDF.shape[0]
threadNum = 10
# How many data to be crawled in the single thread
singleWork = int((totalWork)/threadNum)+1

def download(rangeCato, name):
    print 'thread %s is running...' % threading.current_thread().name
    allData = []
    dataInfo = []
    error = []
    dataCate = []
    for index in rangeCato:
        if index < treeDF.shape[0]:
            try:
                popu = fred.search_by_category(treeDF.loc[index, 'cate3Index'], limit=10, order_by='popularity', sort_order='desc')
                for detailIndex, detialValues in popu.iterrows():
                    try:
                        dataInfo.append(fred.get_series_info(detailIndex))
                    except:
                        pass
                    dataCate.append(list(np.hstack((treeDF.loc[index, :].values, detailIndex))))
                    allData.append(pd.DataFrame(fred.get_series(detailIndex), columns=[detailIndex]))
                allDataIn = pd.concat(allData, axis=1)
                dataInfoIn = pd.concat(dataInfo, axis=1)
                dataCateIn = pd.DataFrame(dataCate, columns=['cate1Index', 'cate1Name', 'cate2Index', 'cate2Name', 'cate3Index','cate3Name', 'itemID'])
                allDataIn.to_csv('data/allData'+name+'.csv')
                dataInfoIn.to_csv('data/info'+name+'.csv')
                dataCateIn.to_csv('data/dataCate'+name+'.csv')
            except:
                print treeDF.loc[index, 'cate3Index'], 'can not be found'
                error.append(treeDF.loc[index, 'cate3Index'])
                np.savetxt('data/errorLog'+name+'.csv',error,delimiter=',')
    print 'thread %s ended.' % threading.current_thread().name


threadList = [threading.Thread(target=download, args=(range(index*singleWork, (index+1)*singleWork), str(index),), name='DownloadThread'+str(index)) for index in range(threadNum)]

for index, value in enumerate(threadList):
    value.start()
for index, value in enumerate(threadList):
    value.join()
