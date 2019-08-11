# scrapy_douban
 A project to scrapy all posts of  Shenzhen Rent Group（深圳租房团）  in Douban
- sz_rent_group_analysis.ipynb  数据清洗
- sz_rent_group_analysis_v2.ipynb 数据分析
- sz_rent_group_analysis_v2.html 分析图表展示

## Notice:
1. your python environment needs mongodb support, or you can customized your own db support like MySQL or csv writer as well.
2. you can't run this project at once  after you run "git commit xxx" cmd or download this project  ,  because you need to specify some parms or some settings in your owns,  for more about scrapy ,you can read its documentation via [Scrapy](https://docs.scrapy.org/en/latest/)
3. .ipynb document is run in jupyter notebook
## step 1
you should build up a virtual scrapy environment

## step 2 
activate your scrapy env

## step 3
scrapy startproject "your project name" (this step can be ignored for i have build up the project)

## step 4
in your work path run the crawl_proxy_process.py


