import urllib.request
import json
import pandas as pd
from datetime import datetime

# 定义 API 地址
url = 'https://api.hkma.gov.hk/public/market-data-and-statistics/monthly-statistical-bulletin/er-ir/er-eeri-daily?pagesize=1000&offset=0&choose=end_of_month&from=2005-01&to=2024-04'


try:
    # 发送请求并读取数据
    with urllib.request.urlopen(url) as req:
        data = json.loads(req.read().decode('utf-8'))  # 解析 JSON

    # 提取关键字段（假设数据在 "records" 列表中）
    records = data["result"]["records"]

    # 转换为 DataFrame
    df = pd.DataFrame(records)

    # 保存为 Excel 文件
    excel_path = "/Users/yangyidi/Library/CloudStorage/OneDrive-TheUniversityofHongKong-Connect/Documents/Code/balala/Practice/cross_border/output/exchange_periodaverage.xlsx"
    df.to_excel(excel_path, index=False, engine="openpyxl")

    print(f"数据已保存到：{excel_path}")

except Exception as e:
    print(f"发生错误: {e}")
