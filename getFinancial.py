# -*- coding : utf-8 -*- #

__author__ = "lawson"
import time
import requests,json,time
from bs4 import BeautifulSoup
from multiprocessing import Queue
from concurrent.futures import ThreadPoolExecutor
from utils import *
import os

'''
Func: 请求新浪财经拿到各家的财报数据
（1）将每家财报的数据放到一个单独的文件夹中
'''
class SinaFinancial():
    def __init__(self):
        self.queue=Queue()
        self.info=[]
        self.url_balance_template = "http://money.finance.sina.com.cn/corp/go.php/vFD_BalanceSheet/stockid/{}/ctrl/{}/displaytype/4.phtml"
        self.url_pofit_template = "http://money.finance.sina.com.cn/corp/go.php/vFD_ProfitStatement/stockid/{}/ctrl/{}/displaytype/4.phtml"
        self.url_cashflow_template = "http://money.finance.sina.com.cn/corp/go.php/vFD_CashFlow/stockid/{}/ctrl/{}/displaytype/4.phtml"

        self.name2url = {"balance":self.url_balance_template,
                         'profit':self.url_pofit_template,
                         "cashflow":self.url_cashflow_template}

    def post(self, ninfo):
        try:
            info=json.loads(ninfo)
            scode=info["SECCODE"]
            year=info["year"]
            # print(scode,year)
            data_=info

            data_year=[]
            for item in self.name2url.items():
                name = item[0]
                url_template = item[1]
                # print("url_template",url_template)
                cur_url = url_template.format(scode, year)
                headers={}
                # print("cur_url = ", cur_url)
                response=requests.get(cur_url, headers=headers, timeout=5)
                soup=BeautifulSoup(response.content.decode("gb2312"),"lxml")
                
                '''报表日期'''
                # 解析数据
                # extractData()
                trs = soup.select("tbody tr")
                data={}
                for tr in trs:
                    tds=tr.select("td")
                    if tds != []:
                        '''
                        tds 的值长下面这样
                        [<td style="padding-left:30px" width="200px"><a href="/corp/view/vFD_FinanceSummaryHistory.php?stockid=600036&amp;typecode=CASHNETR&amp;cate=xjll1" target="_blank">现金及现金等价物净增加额</a></td>, <td style="text-align:right;">15,750,800.00</td>, <td style="text-align:right;">--</td>, <td style="text-align:right;">13,688,700.00</td>, <td style="text-align:right;">--</td>]
                        '''
                        # print(tds)
                        try:
                            value = tds[1].text
                            # print("11111", tds[0].text, value )
                            if value == "--":
                                value = "0.00"
                            data[tds[0].text] = value
                        except:
                            pass
                data_year.append({name:data})

            data_["data"]=data_year
            # print(info["SECNAME"], info["year"])
            res = json.dumps(data_, ensure_ascii=False)
            return res
        except TimeoutError:
            print("超时")
            self.info.append(ninfo)
        except Exception as e:
            print(e)
            print("其他错误")
            info = json.loads(ninfo)
            print(info["SECNAME"], info["year"])
    

    def scheduler(self, stock_path, year_list, out_path):
        with open(stock_path, encoding="utf8") as f:
            lines=f.readlines()

        for line in lines:
            info=json.loads(line)
            for year in year_list:
                info["year"] = year
                info_str = json.dumps(info)
                # print(json.loads(info_str))
                self.queue.put(info_str)

        futures = []
        pool = ThreadPoolExecutor(max_workers = 8)
        while self.queue.qsize() > 0:
            # queue.get() 取出一个元素，并从队列中删除
            que_head = self.queue.get()
            future = pool.submit(self.post, que_head)
            futures.append([future, que_head])
        
        # TODO: 看下这个方法
        pool.shutdown()
        # print("剩下："+str(len(self.info)))
        # while len(self.info) > 0:
        #     self.post(self.info.pop())
        
        for item in futures:
            future = item[0]
            stock_info = json.loads(item[1])
            result = future.result()
            # print("result = ", result)
            # out_path 是根据股票代码组合得到
            print("stock_info = ", stock_info)
            stock_name = stock_info['SECCODE'] + "_" + stock_info['SECNAME']
            year = stock_info['year']
            out_path = "./data/" + stock_name + "/" + str(year)
            if not os.path.exists(out_path):
                os.makedirs(out_path)
            out_path_name = out_path + "/" +  "report.json"
            write_line_2_json(out_path_name, result)
            time.sleep(10)


if __name__ == '__main__':
    start_time=time.time()
    year_list = [2024]
    stock_path = "./stockCode.json"
    out_path = "./data.json"
    sina = SinaFinancial()
    # a = sina.url_balance.format("12","2014")
    # print(a)
    # print(sina.url_balance)
    sina.scheduler(stock_path, year_list, out_path)