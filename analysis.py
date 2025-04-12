
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

    for fields in all_fields: 
        get_pic_by_stock_year_field(stock_code, year_list, fields)


if __name__ == "__main__":
    code_path = "./stockCode.json"
    with open(code_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    for line in lines:
        item = json.loads(line)
        stock_code = item['SECCODE']
        stock_name = item['SECNAME']
        year_list = [i for i in range(2014, 2024)]
        main(stock_code, year_list)