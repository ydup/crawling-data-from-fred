# Crawling Data from FRED

This is a tutorial about how to crawl the FRED big data in a rapid and methodical way

+ The tree figure of the category structure of the FRED is in the [webpage](tree.html)

+ A [jupyter notebook](https://github.com/ydup/crawling-data-from-fred/blob/master/jupyter/CrawlingFRED.ipynb) of the strategy implemention. 

+ Tree of the category [crawler](https://github.com/ydup/crawling-data-from-fred/blob/master/pythonScript/crawlingTree.py) and json file generator
	- [crawlingTree.py](pythonScript/crawlingTree.py)
	- [cateTree.csv](data/cateTree.csv)
	- [jsonFile.json](data/jsonFile.json)

+ Download the top-10 popular data in the single thread way
	- [singleThread.py](pythonScript/singleThread.py)

+ Download the top-10 popular data  in the __multi__ thread way
	- [multiThread.py](pythonScript/multiThread.py)

![tree][img/TreeExample.jpg]
