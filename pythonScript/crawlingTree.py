# Version 2.0
'''
Crawl three pages
but some of the second category data can't be matched.
'''
import requests
import re
cateTable = []
mainPage = requests.get('https://fred.stlouisfed.org/categories')
# First RES for the name and index of category - 1
fstRes = r'<p class="large fred-categories-parent">\n    <a href="/categories/(\d+)"><strong>(.*?)</strong>'
# Second RES for the name and index of category - 2
sndRes = r'<a href="( *)/categories/(\d+)">(.*?)</a>&nbsp;(.*?)</li>'
# Third RES for the name and index of category - 3
trdRes = r'<li><a href="(.*?)/categories/(\d+)">(.*?)</a>' # Some category has a space before the '/'

fstContent =  re.findall(fstRes, mainPage.text, re.S|re.M)
for value1st in fstContent:
    cate1Index = value1st[0]
    cate1Name = value1st[1]
    # Crawl the second category page
    cate2Page = requests.get(str('https://fred.stlouisfed.org/categories/'+ cate1Index))
    cate2 = re.findall(sndRes, cate2Page.text, re.S|re.M)
    for cate2item in cate2:
        # Give them names
        cate2Index = cate2item[1]
        cate2Name = cate2item[2]
        cate2NumString = cate2item[3]
        if cate2NumString == '':
            # Some of the second category which don't have the 'category-count' is the finanl category
            cateTable.append([int(cate1Index), cate1Name, int(cate2Index), cate2Name, int(cate2Index), cate2Name])
        else:
            # Get the page of category-3
            cate3Page = requests.get(str('https://fred.stlouisfed.org/categories/'+ cate2Index))
            trdContent =  re.findall(trdRes, cate3Page.text, re.S|re.M)
            for value3rd in trdContent:
                cate3Index = value3rd[1]
                cate3Name = value3rd[2]
                if cate3Index == cate1Index:
                    cateTable.append([int(cate1Index), cate1Name, int(cate2Index), cate2Name, int(cate2Index), cate2Name])
                else:
                    try:
                        # There are some illegal value in the cate3Index that should be removed.
                        # If it can't be converted into integer, we ignore this
                        cateTable.append([int(cate1Index), cate1Name, int(cate2Index), cate2Name, int(cate3Index), cate3Name])
                    except:
                        pass

treeDF = pd.DataFrame(cateTable, 
                      columns=['cate1Index', 'cate1Name', 'cate2Index', 'cate2Name', 'cate3Index', 'cate3Name'])
import sys
reload(sys)
sys.setdefaultencoding('utf8')
# Convert the name to utf8 string
treeDF = treeDF.drop_duplicates()
treeDF['cate1Name'] = treeDF['cate1Name'].astype(str)
treeDF['cate2Name'] = treeDF['cate2Name'].astype(str)
treeDF['cate3Name'] = treeDF['cate3Name'].astype(str)
treeDF.to_csv('../data/cateTree.csv')


# Save the name tree into a json file
tree = pd.read_csv('../data/cateTree.csv', index_col = 0)
#tree.loc[tree.shape[0]] = ['end','end','end','end','end','end']
tree.index = range(tree.shape[0])
tree.loc[tree.shape[0]] = ['end','end','end','end','end','end']
node3List = []
node2List = []
node1List = []
lastRow = tree.iloc[0]

for index, row in tree.iterrows():
    node3 = {"name": row['cate3Name'], "parent": row['cate2Name']}
    if lastRow['cate2Name'] != row['cate2Name']:
        node2 = {"name": lastRow['cate2Name'], "parent": lastRow['cate1Name'], "children": node3List}
        node2List.append(node2)     
        if lastRow['cate1Name'] != row['cate1Name']:
            node1 = {"name": lastRow['cate1Name'], "parent": "Fred", "children": node2List}
            if row['cate1Name'] != 'end':
                node1List.append(node1)
            node2List = []
            lastRow = row
        node3List = []
        lastRow = row
        
    if row['cate2Name'] != 'end':
        node3List.append(node3)

dictObj = {"name": "Fred", "parent": "null", "children": node1List}
import json
jsObj = json.dumps(dictObj) 
fileObject = open('jsonFile.json', 'w')
fileObject.write(jsObj)
fileObject.close()




