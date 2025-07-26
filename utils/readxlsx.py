import numpy as np
from matplotlib import pyplot as plt
import os
import pandas as pd
from pylab import mpl

# 设置中文显示字体
# mpl.rcParams["font.sans-serif"] = ["SimHei"]
mpl.rcParams['font.sans-serif'] = ['Microsoft YaHei']
UNIT = '千' #将单位统一拆分成千
MILLION=1E6
HUNDRED_MILLION=1E8
RETRY_NUM = 3 # 请求接口的重试次数


def read_xlsx(path, sheet_name):   
    df_content = pd.read_excel(path, sheet_name=sheet_name)
    info_dic = {}
    
    headers = df_content.columns[1:6]
    
    for i in df_content.itertuples():
        # print(i)
        info_dic[i[1]] = {}
        print(info_dic)
        for a,b in zip(headers, i[2::]):
            info_dic[i[1]][a] = b
        # break
    # print(info_dic)
    info_dic['sheet_name'] = sheet_name
    return info_dic

def plot(info_dict):
    """
    Func: 根据info_dict中的数据绘制图表
    info_dict= {"总营收":{"2020":"xxx", "2021":"xxx"}}
    """
    # info_dict = {'总营业额': { 2023: '3375.92亿', 2022: '2767.45亿', 2021: '2199.55亿', 2020: '1791.28亿'}, '销售成本': { 2023: '2078.07亿', 2022: '1795.54亿', 2021: '1582.02亿', 2020: '1366.54亿'}}
    
    sheet_name = info_dic.pop('sheet_name')
    for item in info_dict.items():
        title = item[0]
        values = item[1]
        x_data = []
        y_data = []
        # print("values = ",values)
        for year, value in values.items():
            x_data.append(year)
            value = get_normalize_value(value)
            y_data.append(value)
        # print("x_data = ",x_data)
        # print("y_data = ",y_data)
        # 对y_data 的数据进行归一化处理
        y_data, unit = normalize(y_data)
        
        draw(x_data, y_data, title, unit, sheet_name)


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


def get_normalize_value(value):
    if type(value) == int:
        return value
    if type(value) == float:
        return value
    if value == '-':
        return 0
    # print(f'value = {value}')
    # 按照单位统一进行换算数值
    cur_unit = ""
    target_char = ['0', '1', '2','3','4','5','6', '7', '8','9',',','.', '-']
    # 找到当前的单位
    idx = -1
    for i in range(len(value)):
        if value[i] not in target_char:
            idx = i
            break
    # print(f"idx = {idx}")
    if idx == -1:
        return float(value)
    cur_unit = value[idx::]
    # print(cur_unit)
    
    # 需要进行单位换算
    if cur_unit == '亿':
        value = value.strip("亿")
        value = float(value)
        value = 1e8 * value
    elif cur_unit == '万':
        value = value.strip("万")
        value = float(value)
        value = 1e4 * value
    elif cur_unit == '元':
        value = value.strip("元")
        value = float(value)
    return value


def draw(x_data, y_data, title, unit, sheet_name):
    """绘制图表的函数
    """
    file_path = f"../pictures/农夫山泉/{sheet_name}/"
    if not os.path.exists(file_path):
        os.makedirs(file_path)
    file_name = title + ".png"
    if sheet_name != '综合指标':
        title = title + f"({unit})"

    plt.plot(x_data, y_data, marker='o')
    plt.title(title)
    # print(x_data)
    plt.xticks(x_data)
    plt.savefig(os.path.join(file_path, file_name))
    # plt.show()
    plt.close()


def plot_roe(all_sheets):
    neat_asset = all_sheets['资产负债表']['净资产']
    neat_profit = all_sheets['利润表']['归属于母公司股东的净利润']
    neat_asset_x_data = [item[0] for item in neat_asset.items()]
    neat_asset_y_data = [item[1] for item in neat_asset.items()]

    neat_profit_x_data = [item[0] for item in neat_profit.items()]
    neat_profit_y_data = [item[1] for item in neat_profit.items()]

    assert neat_asset_x_data == neat_profit_x_data
    print(neat_asset)
    print(neat_profit)
    print(neat_profit_y_data)
    print(neat_asset_y_data)

    neat_profit_y_data = [get_normalize_value(i) for i in neat_profit_y_data]
    neat_asset_y_data = [get_normalize_value(i) for i in neat_asset_y_data]

    y_data = [profit/asset for profit, asset in zip(neat_profit_y_data, neat_asset_y_data)]
    y_data, unit = normalize(y_data)
    title = "roe"
    draw(neat_asset_x_data, y_data, title, unit, '综合指标')
    
def plot_gross_profit_rate(all_sheets):
    neat_asset = all_sheets['利润表']['总营业额']
    neat_profit = all_sheets['利润表']['归属于母公司股东的净利润']
    neat_asset_x_data = [item[0] for item in neat_asset.items()]
    neat_asset_y_data = [item[1] for item in neat_asset.items()]

    neat_profit_x_data = [item[0] for item in neat_profit.items()]
    neat_profit_y_data = [item[1] for item in neat_profit.items()]

    assert neat_asset_x_data == neat_profit_x_data
    print(neat_asset)
    print(neat_profit)
    print(neat_profit_y_data)
    print(neat_asset_y_data)

    neat_profit_y_data = [get_normalize_value(i) for i in neat_profit_y_data]
    neat_asset_y_data = [get_normalize_value(i) for i in neat_asset_y_data]

    y_data = [profit/asset for profit, asset in zip(neat_profit_y_data, neat_asset_y_data)]
    y_data, unit = normalize(y_data)
    title = "毛利率"
    draw(neat_asset_x_data, y_data, title, unit, '综合指标')


def plot_stock_revenue_rate(all_sheets, title):
    '''
    numerator:
    denominator:
    '''
    numerator  = all_sheets['资产负债表']['存货'] # 分子项
    denominator = all_sheets['利润表']['总营业额']

    denominator_x_data = [item[0] for item in denominator.items()]
    denominator_y_data = [item[1] for item in denominator.items()]

    numerator_x_data = [item[0] for item in numerator.items()]
    numerator_y_data = [item[1] for item in numerator.items()]

    assert denominator_x_data == numerator_x_data
    print("numerator_x_data = ", numerator_x_data)
    print("numerator_y_data = ", numerator_y_data)

    print("denominator_x_data = ", denominator_x_data)
    print("denominator_y_data = ", denominator_y_data)

    numerators = [get_normalize_value(i) for i in numerator_y_data]
    denominators = [get_normalize_value(i) for i in denominator_y_data]

    y_data = [profit/asset for profit, asset in zip(numerators, denominators)]
    y_data, unit = normalize(y_data)
    
    draw(denominator_x_data, y_data, title, unit, '综合指标')



if __name__ == "__main__":
    path = "E:\投资\财报\农夫山泉\财报数据.xlsx"
    sheet_names = ['利润表' , '资产负债表', '现金流量表']
    all_sheets = {}
    for cur_sheet_name in sheet_names:
        info_dic = read_xlsx(path, sheet_name = cur_sheet_name)
        # plot(info_dic)
        all_sheets[cur_sheet_name] = info_dic
    
    # plot_roe(all_sheets)

    # 计算毛利率
    # plot_gross_profit_rate(all_sheets)
    # print("This is a test for read_xlsx function.")
    # plot(info_dict = {})

    # 计算存货营收占比
    plot_stock_revenue_rate(all_sheets, title = '存货占总营收比重')