class LrbFields:
    # ------  利润表 ---------
    '''
    不同公司的名称不同，所以这里使用了一个list
    '''
    net_profit = ["归属于母公司的净利润",
        "归属于母公司所有者的净利润"]
    deposit_received = ['预收款项', '合同负债']
    revenue=  ['营业收入']
    sale_cost = ['销售费用']
    development_cost = ['研发费用']
    management_cost = ['管理费用']
    financial_cost = ['财务费用']


if __name__ == "__main__":
    a = LrbFields.__dict__
    print(a)