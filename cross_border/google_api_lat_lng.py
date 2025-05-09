import pandas as pd
import requests
import time
import logging
import re
from tqdm import tqdm

# ------------------- 配置部分 -------------------
logging.basicConfig(filename='geocode_errors.log', level=logging.ERROR)
API_KEYS = ["AIzaSyA8ZpXlLMd4flDomU_egV-aIz1XTU9-a0U",
            "AIzaSyDo_DxyS9uZIY7_EGFHkawyWmrY7TEMe5w"]  # 替换为你的实际API密钥
current_key_idx = 0  # 当前使用的API密钥索引
REQUEST_DELAY = 1  # 每次API请求间隔（秒）
MAX_RETRIES = 3  # 单条数据最大重试次数

# ------------------- 核心函数 -------------------


def preprocess_address(address):
    # 替换缩写
    abbreviation_map = {
        "ST": "Street",
        "BLDG": "Building",
        "GDN": "Garden",
        "PDM": "Podium",
        "CTR": "Center",
        "ACR": "Arcade",
        "E": "East",
        "TWR": "Tower",
        "PH": "Phase",
        "COM": "Commercial"
    }
    for abbr, full in abbreviation_map.items():
        address = address.replace(abbr, full)

    # 补充区域信息（示例为香港）
    if "Hong Kong" not in address:
        address += ", Hong Kong"

    return address


def geocode_address(address, api_key):
    """调用Google Geocoding API获取经纬度"""
    global current_key_idx

    url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {
        "address": address,
        "key": api_key,
        "region": "hk"
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        data = response.json()

        if data["status"] == "OK":
            location = data["results"][0]["geometry"]["location"]
            return {
                "lat": location["lat"],
                "lng": location["lng"],
                "accuracy": data["results"][0]["geometry"]["location_type"]
            }
        elif data["status"] == "OVER_QUERY_LIMIT":
            print(f"\n[警告] API密钥 {api_key[:5]}*** 超出配额，切换下一个密钥")
            current_key_idx = (current_key_idx + 1) % len(API_KEYS)
            return None
        else:
            logging.error(f"Geocoding失败：{data['status']} - 地址：{address}")
            return None
    except Exception as e:
        logging.error(f"API请求异常：{str(e)} - 地址：{address}")
        return None


def get_priority_address(row):
    """根据业务逻辑选择优先使用的地址"""
    street = str(row["STREET"]).strip()
    bname = str(row["BNAME"]).strip()

    # 规则1：检查STREET是否以数字结尾
    if re.search(r'\d+$', street):
        return preprocess_address(street), "STREET"

    # 规则2：检查STREET是否以RD结尾
    if street.upper().endswith("RD"):
        return preprocess_address(bname), "BNAME"

    # 默认使用BNAME
    return preprocess_address(bname), "BNAME"

# ------------------- 主程序 -------------------


def main():
    # 读取输入文件
    try:
        df = pd.read_excel(
            "/Users/yangyidi/Library/CloudStorage/OneDrive-TheUniversityofHongKong-Connect/Documents/Research/Projects/Cross-border/Data/EPRC_v3.1.xlsx")
        print("成功读取文件，样本数据预览：")
        print(df.head(3))
    except Exception as e:
        print(f"文件读取失败：{str(e)}")
        return

    # 检查必要列
    required_columns = ["STREET", "BNAME"]
    if not all(col in df.columns for col in required_columns):
        print(f"错误：缺少必要列 {required_columns}，当前列名：{df.columns.tolist()}")
        return

    # 初始化结果列
    df["修正纬度"] = None
    df["修正经度"] = None
    df["地址来源"] = None
    df["精确度"] = None

    # 处理每条记录
    success_count = 0
    pbar = tqdm(df.iterrows(), total=len(df))

    for idx, row in pbar:
        retries = 0
        result = None

        # 获取优先级地址
        address, source = get_priority_address(row)
        if pd.isna(address) or address == "":
            logging.error(f"空地址：行号 {idx+2}")
            continue

        # 重试逻辑
        while retries < MAX_RETRIES and not result:
            api_key = API_KEYS[current_key_idx]
            result = geocode_address(address, api_key)

            if result:
                df.at[idx, "修正纬度"] = result["lat"]
                df.at[idx, "修正经度"] = result["lng"]
                df.at[idx, "地址来源"] = source
                df.at[idx, "精确度"] = result["accuracy"]
                success_count += 1
                pbar.set_description(
                    f"处理中 | 成功率: {success_count/(idx+1)*100:.1f}%")
            else:
                retries += 1
                time.sleep(2**retries)  # 指数退避

            time.sleep(REQUEST_DELAY)

    # 保存结果
    output_path = "EPRC_v3.2.xlsx"
    df.to_excel(output_path, index=False)
    print(f"\n处理完成！成功修正 {success_count}/{len(df)} 条记录")
    print(f"结果已保存到：{output_path}")
    print("精确度说明：ROOFTOP(精确到门牌) > RANGE_INTERPOLATED(区间插值) > APPROXIMATE(近似) > GEOMETRIC_CENTER(几何中心)")


if __name__ == "__main__":
    main()
