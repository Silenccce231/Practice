import pandas as pd
import requests
import time
import logging
import re
from tqdm import tqdm

# ------------------- 配置部分 -------------------
logging.basicConfig(filename='geocode_errors.log', level=logging.ERROR)
API_KEYS = ["AIzaSyDo_DxyS9uZIY7_EGFHkawyWmrY7TEMe5w",
            "AIzaSyCDj1wexToNnyeWzdE05q19JRvRX5_DaS0"]  # 替换为你的实际API密钥
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
        "CTR": "Centre",
        "ACR": "Arcade",
        "E": "East",
        "TWR": "Tower",
        "PH": "Phase",
        "COM": "Commercial",
        "RD": "Road",
        "HSE": "House",
        "C": "Central"
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
        "region": "hk",
        "language": "en"
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
    """强制使用BNAME，空时直接报错"""
    # 提取BNAME数据（强制字符串化处理）
    bname = str(row["BNAME"]).strip() if pd.notna(row["BNAME"]) else ""

    if bname:
        processed_address = preprocess_address(bname)
        # 即使预处理后为空也强制使用
        return processed_address, "BNAME"
    else:
        # 记录详细错误信息（含行号）
        logging.error(f"BNAME为空 | 行号: {row.name}")
        return "", "INVALID"

# def bename_fist(row):
#     """判断是否使用BNAME/STREET地址（BNAME优先）"""
#     # 优先检查BNAME是否可用
#     bname = str(row["BNAME"]).strip() if pd.notna(row["BNAME"]) else ""
#     if bname:  # 如果BNAME非空，则不使用STREET
#         return False

#     # 只有当BNAME为空时，才检查STREET
#     street = str(row["STREET"]).strip() if pd.notna(row["STREET"]) else ""
#     if not street:  # STREET也为空则报错
#         logging.warning(f"行列数据缺失: BNAME和STREET均为空")
#         return False

#     # 检查STREET有效性（保留原有规则）
#     if re.search(r"[/,]", street):  # 含特殊符号
#         return False
#     if not re.search(r"\b\d+[A-Za-z]?$", street.split()[-1]):  # 结尾无数字
#         return False

#     return True  # 仅当BNAME为空且STREET有效时返回True


# def get_priority_address(row):
#     """优化版地址选择逻辑"""
#     street = str(row["STREET"]).strip() if pd.notna(row["STREET"]) else ""
#     bname = str(row["BNAME"]).strip() if pd.notna(row["BNAME"]) else ""

#     # 第一优先级：BNAME地址（移除括号内容）
#     clean_bname = re.sub(r"$.*?$", "", bname).strip()
#     if clean_bname:
#         return preprocess_address(clean_bname), "BNAME"

#     # 第一优先级：符合规则的STREET地址
#     if bename_fist(row):
#         return preprocess_address(street), "STREET"

#     # 异常处理（保持图片中的日志风格）
#     logging.warning(f"无效地址: STREET='{street}', BNAME='{bname}'")
#     return preprocess_address(street), "INVALID"  # 仍调用预处理保证格式统一

# ------------------- 主程序 -------------------


def main():
    # 读取输入文件
    try:
        df = pd.read_excel(
            "/Users/yangyidi/Library/CloudStorage/OneDrive-TheUniversityofHongKong-Connect/Documents/Research/Projects/Cross-border/Data/lat_test.xlsx")
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
    output_path = "EPRC_v3.2_test.xlsx"
    df.to_excel(output_path, index=False)
    print(f"\n处理完成！成功修正 {success_count}/{len(df)} 条记录")
    print(f"结果已保存到：{output_path}")
    print("精确度说明：ROOFTOP(精确到门牌) > RANGE_INTERPOLATED(区间插值) > APPROXIMATE(近似) > GEOMETRIC_CENTER(几何中心)")


if __name__ == "__main__":
    main()
