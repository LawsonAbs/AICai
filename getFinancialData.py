# -*- coding : utf-8 -*- #

__author__ = "lawson"
import time
import requests,json,time
from bs4 import BeautifulSoup
from multiprocessing import Queue
from concurrent.futures import ThreadPoolExecutor
from utils import *
import os
from constants import RETRY_NUM
'''
Func: 请求新浪财经拿到各家的财报数据
（1）将每家财报的数据放到一个单独的文件夹中
'''
class SinaFinancial():
    def __init__(self):
        self.queue=Queue()
        self.info=[]

        # fzb/llb/lrb
        self.url_template = "https://quotes.sina.cn/cn/api/openapi.php/CompanyFinanceService.getFinanceReport2022?paperCode={}&source={}&type=0&page={}&num={}"

        self.name2url = {"balance":"fzb",
                         'profit':"lrb",
                         "cashflow":"llb"}

    def post(self, url, ninfo, sleep_time):
        cnt = 0
        while(cnt < RETRY_NUM):
            try:
                headers={}
                # 可以作为日志记录
                # print("cur_url = ", url)
                response = requests.get(url, headers=headers, timeout=5)
                time.sleep(sleep_time)  # 防止被封 IP
                # print("response.text() = ", response.text)
                text = response.text
                # print(type(text))
                item = json.loads(text)
                # print(type(item))
                data = item['result']['data']     
                return data
            except TimeoutError:
                print("超时")
                continue
            except Exception as e:
                print(e)
                print(f"url = {url}, 其他错误")
                continue
        return None


    def scheduler(self, stock_path, report_count = 50):
        with open(stock_path, encoding="utf8") as f:
            lines=f.readlines()

        for line in lines:
            stock_info = json.loads(line)
            scode = stock_info['SECCODE']
            # report_count = 50 # 初始化为一个比较大的数，10年报表足够用了
            page = 1
            num = 10
            while (page-1) * num <= report_count:
                for item in self.name2url.items():  # 分三个报表依次取数据
                    # name = item[0]
                    source = item[1]
                    # print("url_template",url_template)
                    url = self.url_template.format(scode, source, page, num)
                    # print("", url)
                    # continue
                    
                    data = self.post(url, line, sleep_time = 30)
                    try:
                        report_count = min(report_count, int(data.get('report_count', '0')))
                        report_list = data.get('report_list',{})
                    except:
                        print("解析出了问题...")
                        pass

                    for item in report_list.items(): # 把每年的数据分别取出来
                        date, val = item
                        data = val['data']
                        cur_res = {}
                        for datum in data:
                            item_title = datum.get('item_title',"")
                            item_value = datum.get('item_value',"")
                            item_cate = datum.get('item_source',"")
                            if item_value is None:
                                item_value = "0"
                            
                            if item_cate not in cur_res.keys():
                                cur_res[item_cate] = {}
                            cur_res[item_cate][item_title] = item_value
                        cur_res = json.dumps(cur_res, ensure_ascii=False)
                        # out_path 是根据股票代码组合得到
                        # print("stock_info = ", stock_info)
                        stock_name = stock_info['SECCODE'] + "_" + stock_info['SECNAME']
                        # year = stock_info['year']
                        out_path = "./data/" + stock_name + "/" + date
                        
                        if not os.path.exists(out_path):
                            os.makedirs(out_path)                        
                        out_path_name = out_path + "/" +  f"report_{source}.json"
                        write_line_2_json(out_path_name, cur_res)

                # 往下翻一页
                page += 1

if __name__ == '__main__':
    start_time=time.time()
    stock_path = "./stockCode.json"
    sina = SinaFinancial()
    # a = sina.url_balance.format("12","2014")
    # print(a)
    # print(sina.url_balance)
    sina.scheduler(stock_path, report_count = 50)