import os
import json
import matplotlib.pyplot as plt
from pylab import mpl

# 设置中文显示字体
mpl.rcParams["font.sans-serif"] = ["SimHei"]
# 设置正常显示符号
mpl.rcParams["axes.unicode_minus"] = False

def write_line_2_json(out_path, line):
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

    # 保存图片
    plt.savefig(pic_name)
    plt.show()
    plt.close()  # 关闭窗口，防止图片丢失
    

# 画折线图
def draw_line_chart(x_label,y_label,title,x_data,y_data, pic_name):
    plt.plot(x_data, y_data)
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.title(title)
    # 保存图片
    plt.savefig(pic_name)
    plt.show()
    plt.close()  # 关闭窗口，防止图片


def get_stock_name_map(path):
    path = "./stockCode.json"
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
    code2name,name2code = get_stock_name_map("./stockCode.json")
    stock_name = code2name[stock_code]
    # 获取需要的数据
    path = "./data/" + stock_code + "_" + stock_name + "/" + str(year) +"1231/" 
    names = ['report_fzb.json', 'report_lrb.json', 'report_llb.json']
    
    data = []
    for name in names:
        path_name = path + name
        print(path_name)   
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
    for three_sheet in data:
        for sheet in three_sheet:
            print("sheet = ",sheet)
            for item in sheet.items():
                sheet_value = item[1]
                for name in fields:
                    print("name = ",name)
                    if name in sheet_value.keys():
                        name_value = sheet_value[name]
                        name_value = float(name_value.replace(',', ''))
                        
                        # 如果值为0，重找一下
                        if name_value == 0:
                            continue
                        select_data.append(name_value)
                        break
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
    all_data = []
    x_data = year_list
    for i in year_list:
        data = select_data(stock_code, i)
        all_data.append(data)

    y_data = select_data_by_name(all_data, fileds)
    code2name,name2code = get_stock_name_map("./stockCode.json")

    x_label = "年份"
    y_label = fileds[0]
    code_name = code2name[stock_code]
    title = fileds[0] + "-" + code_name

    print(x_data)
    print(y_data)
    assert len(x_data) == len(y_data)

    file_path =  "./result/" + code_name 
    file_name = fileds[0] +  "_" + str(year_list[0]) + "_" + str(year_list[1]) + ".png"
    if not os.path.exists(file_path):
        os.makedirs(file_path)
    # draw_histogram(x_label, y_label, title, [2014], [1], pic_name)
    draw_histogram(x_label, y_label, title, x_data, y_data, file_path + "/" + file_name)
    # draw_line_chart(x_label, y_label, title, categories, values, pic_name)


def net_profit():
    '''
    不同公司的名称不同
    '''
    return ["归属于母公司的净利润",
        "归属于母公司所有者的净利润"]

def deposit_received():
    return ['预收款项', '合同负债']

if __name__ == "__main__":
    stock_code = "600519"
    # filed = "归属于母公司所有者的净利润"
    year_list = [i for i in range(2014, 2024)]

    fields = deposit_received()
    get_pic_by_stock_year_field(stock_code, year_list, fields)
