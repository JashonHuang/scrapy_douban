from multiprocessing import Process
from scrapy import cmdline
from crawl_proxy import crawl_proxy
import os


if __name__ == "__main__":
    subProcessList = list()
    # 开始爬取代理
    print("Begin crawl proxy:")
    p = Process(target=crawl_proxy(),)
    p.start()
    subProcessList.append(p)
    print("Begin crawl proxy:")
    # 切换工作目录
    os.chdir("./scrapy_douban")
    p = Process(target=cmdline.execute, args=("scrapy crawl douban-spider".split(),))
    p.start()
    subProcessList.append(p)
    for p in subProcessList:
        p.join()
    print("End this process ！！！")

