import numpy as np
import os
import json
import matplotlib.pyplot as plt
from pylab import mpl
from constants import *
from LrbFields import LrbFields
from LlbFields import LlbFields
from FzbFields import FzbFields
# 设置中文显示字体
mpl.rcParams["font.sans-serif"] = ["SimHei"]
# 设置正常显示符号
mpl.rcParams["axes.unicode_minus"] = False


def write_line_2_json(out_path, line):
    # 如果文件已经存在，直接返回
    if os.path.exists(out_path):
        print(f"warn, out_path {out_path} is already exist!")
        return
    # 将得到的报表数据写入到文件中
    with open(out_path, 'a', encoding='utf-8') as fw:
        fw.write(line + "\n")


def write_list_2_json(out_path, lines):
    with open(out_path, 'a', encoding='utf-8') as fw:
        for line in lines:
        # 将得到的报表数据写入到文件中
            fw.write(line)

'''
将一个字典数据写到json中
dic = {"20240930":{...}}
'''
def write_dict_2_json(out_path, dict):
    with open(out_path, 'a', encoding='utf-8') as fw:
        fw.write()

# 画柱状图
def draw_histogram(x_label, y_label, title, x_data, y_data, pic_name):
    plt.bar(x_data, y_data)
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.title(title)
    plt.xticks(x_data, x_data)

    # 保存图片
    plt.savefig(pic_name)
    # plt.show()
    plt.close()  # 关闭窗口，防止图片丢失
    

# 画折线图
def draw_line_chart(x_label,y_label,title,x_data,y_data, pic_name):
    plt.plot(x_data, y_data)
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.title(title)
    # 保存图片
    plt.savefig(pic_name)
    # plt.show()
    plt.close()  # 关闭窗口，防止图片


def get_stock_name_map(path):
    code2name = {}
    name2code = {}
    with open(path, 'r', encoding='utf-8') as fr:
        lines = fr.readlines()
        for line in lines:
            item = json.loads(line)
            name = item['SECNAME']
            code = item['SECCODE']
            code2name[code] = name
            name2code[name] = code
    return code2name, name2code

'''
Function: 获取指定年的数据
'''
def select_data(stock_code, year):
    code2name,name2code = get_stock_name_map("./sample.json")
    stock_name = code2name[stock_code]
    # 获取需要的数据
    path = "./data/" + stock_code + "_" + stock_name + "/" + str(year) +"1231/" 
    names = ['report_fzb.json', 'report_lrb.json', 'report_llb.json']
    
    data = []
    for name in names:
        path_name = path + name
        if not os.path.exists(path_name):
            print(f"{path_name} 数据丢失...")
            continue
        print(f"阅读{path_name}中...")    
        # 读取数据
        with open(path_name, 'r', encoding='utf-8') as fr:
            lines = fr.readlines()
            for line in lines:
                item = json.loads(line)
                data.append(item)
    return data

def select_data_by_name(data, fields):
    '''
    Args: 根据传入的数据，找出指定字段的值
    '''
    select_data = []
    fields2value = {} # 不同的名字可能取到不同的值
    for item in data.items():
        year, three_sheet = item

        find_value = -1  # 要找到的值
        matched_value_cnt = 0 # 找到的(匹配成功)有效值个数
        for sheet in three_sheet:
            # print("sheet = ",sheet)
            for item in sheet.items():
                sheet_value = item[1]
                for name in fields:
                    # print("name = ",name)
                    if name in sheet_value.keys(): 
                        matched_value_cnt +=1
                        
                        name_value = sheet_value[name]
                        name_value = float(name_value.replace(',', ''))
                        
                        fields2value[name] = name_value
                        
                        # TODO: 这个选数的逻辑可以再优化一下，
                        if name_value != 0:
                            find_value = name_value
                            # break
                        
                        # 说明取到了值，但是值为0
                        elif name_value ==0 and find_value== -1:
                            find_value = 0

        if matched_value_cnt > 1:
            print(f"warning, valid_value_cnt > 1 in year = {year}.")
        elif matched_value_cnt == 0:
            print(f"没有找到 {year},{fields} 相关数据")
        # # 优先找非零的值
        # for item in fields2value:
        #     name, value = item
        #     find_value = name_value

        if find_value == -1:
            find_value = 0 # 设为默认值为-1
        select_data.append(find_value)
        # print(item['data']['profit'][name])
    if len(select_data) == 0:
        print(f"没有找到 {name} 相关数据")
    return select_data


'''
Func:
    根据股票名+时间信息+报表字段 画出柱状图
params:
    stock_code: 股票代码
    year_list: 所需的年份列表
    fileds: 要查询的报表字段列表
    type: 所需的报表类型，annual_report/quarterly_report。 默认是annual_report
'''
def get_pic_by_stock_year_field(stock_code, year_list, fileds, type = 'annual_report'):
    all_data = {}
    x_data = year_list
    for i in year_list:
        data = select_data(stock_code, i)
        all_data[i] = data

    y_data = select_data_by_name(all_data, fileds)
    for x, y in zip(x_data, y_data):
        print(x,y)
    # 对返回的数据做规范化处理（简化单位）
    y_data, y_unit = normalize(y_data)
    code2name, name2code = get_stock_name_map("./sample.json")

    x_label = "年份"
    y_label = fileds[0] + f"（单位：{y_unit}）"
    code_name = code2name[stock_code]
    title = fileds[0] + "-" + code_name

    assert len(x_data) == len(y_data)

    file_path =  "./result/" + code_name 
    file_name = fileds[0] +  "_" + str(year_list[0]) + "_" + str(year_list[-1]) + ".png"
    if not os.path.exists(file_path):
        os.makedirs(file_path)
    # draw_histogram(x_label, y_label, title, [2014], [1], pic_name)
    draw_histogram(x_label, y_label, title, x_data, y_data, file_path + "/" + file_name)
    # draw_line_chart(x_label, y_label, title, categories, values, pic_name)


'''
Func:
(1)根据多项fields画图

args:
(1)operation代表是加、减、乘、除的操作
'''
def get_pic_by_stock_year_multi_fields(stock_code, 
                                       year_list, 
                                       fields, 
                                       operation,
                                       title = '',
                                       type = 'annual_report',
                                       pic_type = 'histogram'):
    all_data = {}
    x_data = year_list
    for i in year_list:
        data = select_data(stock_code, i)
        all_data[i] = data

    # 必须长度为2
    assert len(fields) == 2

    y1_data = select_data_by_name(all_data, fields[0])
    y2_data = select_data_by_name(all_data, fields[1])

    y_data = []

    if operation == 'minus':
        for y2, y1 in zip(y2_data, y1_data):
            y_data.append(y1 - y2)
        if title == "":
            title += (fields[0][0] + "-" + fields[1][0])

    if operation == 'divide':
        for y2, y1 in zip(y2_data, y1_data):
            y_data.append(y1 / (y2+0.001) * 100)
        if title == "":
            title += (fields[0][0] + "_" + fields[1][0])   
    for x, y in zip(x_data, y_data):
        print(x,y)
    
    if pic_type == 'histogram':
        # 对返回的数据做规范化处理（简化单位）
        y_data, y_unit = normalize(y_data)
        y_label = title + f"（单位：{y_unit}）"
    else:
        y_label = title

    code2name, name2code = get_stock_name_map("./sample.json")
    x_label = "年份"
    code_name = code2name[stock_code]
    title +=  ("(" + code_name +")")
    assert len(x_data) == len(y_data)

    file_path =  "./result/" + code_name 
    file_name = title +  "_" + str(year_list[0]) + "_" + str(year_list[-1]) + ".png"
    if not os.path.exists(file_path):
        os.makedirs(file_path)

    if pic_type == 'hitogram':
        # draw_histogram(x_label, y_label, title, [2014], [1], pic_name)
        draw_histogram(x_label, y_label, title, x_data, y_data, file_path + "/" + file_name)
    elif pic_type == 'line':
       draw_line_chart(x_label, y_label, title, x_data, y_data, file_path + "/" + file_name)

def normalize(data):
    """
    Func: 根据data 返回缩小后的数字+单位
    """
    scaled_data = []
    np_data = np.array([abs(i) for i in data])
    if np_data.mean() > HUNDRED_MILLION:
        scaled_data = [i/HUNDRED_MILLION for i in data]
        unit = "亿"
        return scaled_data, unit
    elif np_data.mean() > MILLION:
        scaled_data = [i/MILLION for i in data]
        unit = "百万"
        return scaled_data, unit
    return data, ""


def except_detect(x_data, y_data):
    '''
    func:
        针对给出的数据，判断是否有异常，如果有异常，给出警示
    判断准则：
    （1）：前后数值变动幅度超过50%
    '''
    pass
    

