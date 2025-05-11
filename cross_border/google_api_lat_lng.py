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


def should_use_street(street):
    """判断是否优先使用STREET地址"""
    if not isinstance(street, str) or pd.isna(street):
        return False

    street = street.strip()
    # 条件1：不含特殊符号（/和,）
    if re.search(r"[/,]", street):
        return False
    # 条件2：最后一节是数字（如6-8或11A）
    if not re.search(r"\b\d+[A-Za-z]?$", street.split()[-1]):
        return False
    return True


def geocode_with_retry(address, api_key):
    """带自动切换密钥的重试机制"""
    global current_key_idx, FAILED_KEYS

    for attempt in range(MAX_RETRIES):
        try:
            url = "https://maps.googleapis.com/maps/api/geocode/json"
            params = {
                "address": address,
                "key": api_key,
                "region": "hk",
                "language": "en"
            }

            response = requests.get(url, params=params, timeout=15)
            data = response.json()

            if data["status"] == "OK":
                location = data["results"][0]["geometry"]["location"]
                accuracy = data["results"][0]["geometry"]["location_type"]
                return {
                    "lat": location["lat"],
                    "lng": location["lng"],
                    "accuracy": accuracy
                }
            elif data["status"] == "OVER_QUERY_LIMIT":
                logging.warning(f"API密钥配额不足: {api_key[:5]}***")
                FAILED_KEYS.add(api_key)
                return None
            else:
                logging.warning(f"Geocoding失败: {data['status']} - {address}")
                return None

        except Exception as e:
            logging.error(f"API请求异常: {str(e)} - {address}")
            time.sleep(2 ** attempt)  # 指数退避

    return None


def get_priority_address(row):
    """优化版地址选择逻辑"""
    street = str(row["STREET"]).strip() if pd.notna(row["STREET"]) else ""
    bname = str(row["BNAME"]).strip() if pd.notna(row["BNAME"]) else ""

    # 第一优先级：符合规则的STREET地址
    if should_use_street(street):
        return preprocess_address(street), "STREET"

    # 第二优先级：BNAME地址（移除括号内容）
    clean_bname = re.sub(r"$.*?$", "", bname).strip()
    if clean_bname:
        return preprocess_address(clean_bname), "BNAME"

    # 最后回退到STREET
    return preprocess_address(street), "STREET"


def compare_coordinates(new_lat, new_lng, orig_lat, orig_lng):
    """比较新旧坐标差异"""
    if pd.isna(new_lat) or pd.isna(orig_lat):
        return "坐标缺失"

    lat_diff = abs(round(new_lat, 2) - round(float(orig_lat), 2))
    lng_diff = abs(round(new_lng, 2) - round(float(orig_lng), 2))

    if lat_diff > 0.02 or lng_diff > 0.02:
        return f"经度差:{lng_diff:.2f}, 纬度差:{lat_diff:.2f}"
    return "匹配良好"

# ------------------- 主程序 -------------------


def main():
    # 读取输入文件
    try:
        input_path = "/Users/yangyidi/Library/CloudStorage/OneDrive-TheUniversityofHongKong-Connect/Documents/Research/Projects/Cross-border/Data/lat_test.xlsx"
        df = pd.read_excel(input_path)
        print("成功读取文件，样本数据预览：")
        print(df[["STREET", "BNAME", "LATITUDE", "LONGTITUDE"]].head(3))
    except Exception as e:
        print(f"文件读取失败：{str(e)}")
        return

    # 检查必要列
    required_columns = ["ID", "STREET", "BNAME", "LATITUDE", "LONGTITUDE"]
    if not all(col in df.columns for col in required_columns):
        missing = set(required_columns) - set(df.columns)
        print(f"错误：缺少必要列 {missing}，当前列名：{df.columns.tolist()}")
        return

    # 初始化结果列
    result_cols = ["修正纬度", "修正经度", "地址来源", "精确度", "坐标比对"]
    df[result_cols] = None

    # 处理每条记录
    success_count = 0
    pbar = tqdm(df.iterrows(), total=len(df))

    for idx, row in pbar:
        retries = 0
        result = None
        used_api_key = None

        # 获取优先级地址
        address, source = get_priority_address(row)
        if not address:
            df.at[idx, "坐标比对"] = "无效地址"
            continue

        # 重试逻辑（带自动密钥切换）
        while retries < MAX_RETRIES and not result:
            api_key = API_KEYS[current_key_idx]

            # 跳过已知失效的密钥
            if api_key in FAILED_KEYS:
                current_key_idx = (current_key_idx + 1) % len(API_KEYS)
                continue

            result = geocode_with_retry(address, api_key)
            used_api_key = api_key

            if result:
                # 检查精度，如果STREET精度不足则尝试BNAME
                if source == "STREET" and result["accuracy"] != "ROOFTOP":
                    alt_address, _ = get_priority_address(pd.Series({
                        "STREET": "",  # 强制使用BNAME
                        "BNAME": row["BNAME"]
                    }))
                    if alt_address and alt_address != address:
                        alt_result = geocode_with_retry(alt_address, api_key)
                        if alt_result and alt_result["accuracy"] == "ROOFTOP":
                            result = alt_result
                            source = "BNAME(回退)"

                # 保存结果
                df.at[idx, "修正纬度"] = result["lat"]
                df.at[idx, "修正经度"] = result["lng"]
                df.at[idx, "地址来源"] = source
                df.at[idx, "精确度"] = result["accuracy"]
                df.at[idx, "坐标比对"] = compare_coordinates(
                    result["lat"], result["lng"],
                    row["LATITUDE"], row["LONGTITUDE"]
                )
                success_count += 1

                # 更新进度条
                pbar.set_description(
                    f"处理中 | 成功: {success_count} | 当前密钥: {used_api_key[:5]}***"
                )
            else:
                retries += 1
                # 轮换API密钥
                current_key_idx = (current_key_idx + 1) % len(API_KEYS)
                # 所有密钥都失效时的处理
                if len(FAILED_KEYS) == len(API_KEYS):
                    logging.critical("所有API密钥均已失效！")
                    break

            time.sleep(REQUEST_DELAY)

    # 保存结果
    output_path = "EPRC_v3.2_geocoded.xlsx"
    df.to_excel(output_path, index=False)

    # 生成统计报告
    stats = {
        "总记录数": len(df),
        "成功修正数": success_count,
        "成功率": f"{success_count/len(df)*100:.1f}%",
        "STREET来源占比": f"{len(df[df['地址来源'] == 'STREET'])/len(df)*100:.1f}%",
        "ROOFTOP精度占比": f"{len(df[df['精确度'] == 'ROOFTOP'])/success_count*100:.1f}%",
        "坐标差异较大数": len(df[df['坐标比对'].str.contains('差')])
    }

    print("\n处理完成！统计信息：")
    for k, v in stats.items():
        print(f"{k}: {v}")
    print(f"\n结果已保存到：{output_path}")


if __name__ == "__main__":
    main()
