from fredapi import Fred
import pandas as pd
from tqdm import tqdm
import numpy as np
fred = Fred(api_key='APIkey')
treeDF = pd.read_csv('../data/cateTree.csv', index_col=0)
treeDF.index = range(treeDF.shape[0])
allData = []
dataInfo = []
error = []
treeDF.index = range(treeDF.shape[0])
for index in tqdm(range(treeDF.shape[0])):
    try:
        popu = fred.search_by_category(treeDF.loc[index, 'cate3Index'], limit=10, order_by='popularity', sort_order='desc')
        for detailIndex, detialValues in popu.iterrows():
            allData.append(pd.DataFrame(fred.get_series(detailIndex), columns=[detailIndex]))
        allDataIn = pd.concat(allData, axis=1)
        allDataIn.to_csv('../data/allData.csv')
    except:
        print treeDF.loc[index, 'cate3Index'], 'can not be found'
        error.append(treeDF.loc[index, 'cate3Index'])
        np.savetxt('../data/errorLog.csv', error, delimiter=',')