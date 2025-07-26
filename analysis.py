
from utils import *

def main(stock_code, year_list):
    all_fields = []

    # 获取类对象的所有属性和方法
    # attributes = vars(FzbFields)
    fzb_attributes = FzbFields.__dict__
    for attr, val in fzb_attributes.items():
        if not callable(getattr(FzbFields, attr)) and not attr.startswith("__"):
            all_fields.append(val)

    lrb_attributes = LrbFields.__dict__
    for attr, val in lrb_attributes.items():
        if not callable(getattr(LrbFields, attr)) and not attr.startswith("__"):
            all_fields.append(val)

    llb_attributes = LlbFields.__dict__
    for attr, val in llb_attributes.items():
        if not callable(getattr(LlbFields, attr)) and not attr.startswith("__"):
            all_fields.append(val)

    print(f"all_fields = {all_fields}")
    for fields in all_fields: 
        get_pic_by_stock_year_field(stock_code, year_list, fields)

    print("....")
    # 获取ROE/毛利率/毛利润/净利率等指标
    roe(stock_code, year_list)
    gross_profit(stock_code, year_list)
    net_profit_rate(stock_code, year_list)

def roe(stock_code, year_list, ):
    fields = [["归属于母公司的净利润",
        "归属于母公司所有者的净利润"], ['归属于母公司股东权益合计']]
    # get_pic_by_stock_year_field(stock_code, year_list, fields)
    get_pic_by_stock_year_multi_fields(stock_code, 
                                       year_list, 
                                       fields,
                                       title = 'roe',
                                       operation='divide',
                                       pic_type='line')

def gross_profit(stock_code, year_list):
    '''
    Func: 毛利润=营业收入-营业成本
    '''
    fields = [['营业收入'], ['营业成本']]
    get_pic_by_stock_year_multi_fields(stock_code,
                                       year_list,
                                       fields,
                                       title = '毛利润',
                                       operation='minus')

def net_profit_rate(stock_code, year_list):
    '''
    Func: 净利率=净利润/营业收入
    '''
    fields = [['净利润'],['营业收入']]
    get_pic_by_stock_year_multi_fields(stock_code,
                                       year_list,
                                       fields,
                                       title = '净利率',
                                       operation='divide',
                                       pic_type='line')


if __name__ == "__main__":
    code_path = "./sample.json"
    with open(code_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    for line in lines:
        item = json.loads(line)
        stock_code = item['SECCODE']
        stock_name = item['SECNAME']
        year_list = [i for i in range(2018, 2025)]
        try:
            print(f"分析{stock_name}中...")
            main(stock_code, year_list)
        except:
            continue
        # break