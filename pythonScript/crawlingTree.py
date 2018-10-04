"""
Author: Yadong Zhang
Email: ydup@foxmail.com 
Date: 10-4-2018
License: MIT license
Note: 
This script crawls the structure tree of the fred.
I match the name and index of the category with three regular expressions, 
and manage to establish a full map of all the categories.
This tree can help us download the data with ID of categories.
Finanlly, we get two files:
    1. save the csv file to data/cateTree.csv,
    ['cate1Index', 'cate1Name', 'cate2Index', 'cate2Name', 'cate3Index', 'cate3Name']
    2. save the json file to data/jsonFile.json for D3.js tree visualization
     {"name": name, "parent": parent, "children": children}
"""
import requests
import re
cateTable = []  # Placeholder list for saving the categories
# Main page
mainPage = requests.get('https://fred.stlouisfed.org/categories')
# First RES for the name and index of category - 1
fstRes = r'<p class="large fred-categories-parent">\n    <a href="/categories/(\d+)"><strong>(.*?)</strong>'
# Second RES for the name and index of category - 2
sndRes = r'<a href="( *)/categories/(\d+)">(.*?)</a>&nbsp;(.*?)</li>'  # Some category has a space before the '/'
# Third RES for the name and index of category - 3
trdRes = r'<li><a href="(.*?)/categories/(\d+)">(.*?)</a>' 
# Crawl the first category page
fstContent =  re.findall(fstRes, mainPage.text, re.S|re.M)

for value1st in fstContent:
    cate1Index = value1st[0]  # cate1 - index - string
    cate1Name = value1st[1]  # cate1 - name - string
    # Crawl the second category page
    cate2Page = requests.get(str('https://fred.stlouisfed.org/categories/'+ cate1Index))
    cate2 = re.findall(sndRes, cate2Page.text, re.S|re.M)
    for cate2item in cate2:
        # Give them names
        cate2Index = cate2item[1]  # cate2 - index - string
        cate2Name = cate2item[2]  # cate2 - name - string
        cate2NumString = cate2item[3]  # the sub-count of a specific item
        if cate2NumString == '':
            # Some of the second category which don't have the 'category-count' is the finanl category
            # Use cate2 as cate3(final category)
            cateTable.append([int(cate1Index), cate1Name, int(cate2Index), cate2Name, int(cate2Index), cate2Name])
        else:
            # Crawl the third category page
            cate3Page = requests.get(str('https://fred.stlouisfed.org/categories/'+ cate2Index))
            trdContent =  re.findall(trdRes, cate3Page.text, re.S|re.M)
            for value3rd in trdContent:
                cate3Index = value3rd[1]  # cate3 - index - string
                cate3Name = value3rd[2]  # cate3 - name - string
                if cate3Index == cate1Index:  
                    # this is a trap for the crawler
                    cateTable.append([int(cate1Index), cate1Name, int(cate2Index), cate2Name, int(cate2Index), cate2Name])
                else:
                    try:
                        # There are some illegal value in the cate3Index that should be removed.
                        # If it can't be converted into integer, we ignore this
                        cateTable.append([int(cate1Index), cate1Name, int(cate2Index), cate2Name, int(cate3Index), cate3Name])
                    except:
                        pass
# Convert the cateTable into dataframe
treeDF = pd.DataFrame(cateTable, 
                      columns=['cate1Index', 'cate1Name', 'cate2Index', 'cate2Name', 'cate3Index', 'cate3Name'])
import sys
reload(sys)
# Convert the name to utf8 string
sys.setdefaultencoding('utf8')
# Remove the duplicate items
treeDF = treeDF.drop_duplicates()
treeDF['cate1Name'] = treeDF['cate1Name'].astype(str)
treeDF['cate2Name'] = treeDF['cate2Name'].astype(str)
treeDF['cate3Name'] = treeDF['cate3Name'].astype(str)
# Save all data into csv file
treeDF.to_csv('../data/cateTree.csv')

'''
Convert the dataframe into the {"name", "parent", "children"} node structure
and save it into json
'''

# Save the name tree into a json file
tree = pd.read_csv('../data/cateTree.csv', index_col = 0)
tree.index = range(tree.shape[0])  # Reset the index
tree.loc[tree.shape[0]] = ['end','end','end','end','end','end']  # Add a end tail
# Node list placeholder
node3List = []  # The grandchildren nodes
node2List = []  # The children nodes
node1List = []  # The parent nodes
# Initialize the lastRow (previous row) as the first item of tree
lastRow = tree.iloc[0]

for index, row in tree.iterrows():
    # Generate the node3 every time with the cate3name, and they don't have children
    node3 = {"name": row['cate3Name'], "parent": row['cate2Name']}
    if lastRow['cate2Name'] != row['cate2Name']:
        # A set of cate2 ends. 
        # Collect the previous set of node3list into the node2 of lastRow node2
        node2 = {"name": lastRow['cate2Name'], "parent": lastRow['cate1Name'], "children": node3List}
        # Append node2
        node2List.append(node2)     
        if lastRow['cate1Name'] != row['cate1Name']:
            # A set of cate1 ends.
            # Collect the previous set of node2list into the node1 of lastRow
            node1 = {"name": lastRow['cate1Name'], "parent": "Fred", "children": node2List}
            if row['cate1Name'] != 'end':
                # If it is not the end of all data, we append the node1List with node1
                # The end of node2List is same as the node1List. We only implement one of them.
                node1List.append(node1)
            # Because a set of cate1 ends, the node2List should be cleaned and prepared for next collection
            node2List = []
            # Update the new lastRow with this row
            lastRow = row
        # Because a set of cate2 end, the node3List should be cleaned and prepared for next collection
        node3List = []
        lastRow = row

    if row['cate2Name'] != 'end':
        # If it is not the end of all data, we append the node3List with node3
        node3List.append(node3)

# The head node - grandparent node
dictObj = {"name": "Fred", "parent": "null", "children": node1List}

# Save all of the dict into json
import json
jsObj = json.dumps(dictObj) 
fileObject = open('../data/jsonFile.json', 'w')
fileObject.write(jsObj)
fileObject.close()

