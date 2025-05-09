import pandas as pd
import requests
import time
import logging
from tqdm import tqdm

# 配置日志和API密钥
logging.basicConfig(filename='error.log', level=logging.ERROR)
API_KEYS = ["AIzaSyA8ZpXlLMd4flDomU_egV-aIz1XTU9-a0U", "AIzaSyDo_DxyS9uZIY7_EGFHkawyWmrY7TEMe5w",
            "AIzaSyCDj1wexToNnyeWzdE05q19JRvRX5_DaS0"]  # 替换为你的实际API密钥
current_key_idx = 0
MAX_RETRIES = 3
RATE_LIMIT_DELAY = 2  # 每次请求间隔（秒）


def get_nearby_subway_stations(lat, lng, api_key):
    """通过Places API获取附近地铁站"""
    url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    params = {
        "location": f"{lat},{lng}",
        "radius": 2500,
        "type": "subway_station",
        "key": api_key
    }
    try:
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        if data["status"] == "OK":
            return data["results"]
        else:
            logging.error(
                f"Places API error: {data['status']} (Lat: {lat}, Lng: {lng})")
            return []
    except Exception as e:
        logging.error(f"Places API request failed: {str(e)}")
        return []


def get_walking_details(origin_lat, origin_lng, destinations, api_key):
    """通过Distance Matrix API获取步行时间和距离"""
    url = "https://maps.googleapis.com/maps/api/distancematrix/json"
    params = {
        "origins": f"{origin_lat},{origin_lng}",
        "destinations": "|".join(destinations),
        "mode": "walking",
        "key": api_key
    }
    try:
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        if data["status"] == "OK":
            return data["rows"][0]["elements"]
        else:
            logging.error(f"Distance Matrix error: {data['status']}")
            return None
    except Exception as e:
        logging.error(f"Distance Matrix request failed: {str(e)}")
        return None


def process_location(location, api_key):
    """处理单个地点"""
    lat = location["LATITUDE_NEW"]
    lng = location["LONGTITUDE_NEW"]
    location_id = location["ID"]

    stations = get_nearby_subway_stations(lat, lng, api_key)
    if not stations:
        return {"nearest_subway": None, "walking_time": None, "walking_distance": None}

    # 提取地铁站坐标
    destinations = [
        f"{s['geometry']['location']['lat']},{s['geometry']['location']['lng']}" for s in stations]

    # 分批次处理（每批最多25个目的地）
    batch_size = 25
    min_time = float("inf")
    nearest_station_name = None
    nearest_distance = None

    for i in range(0, len(destinations), batch_size):
        batch_dest = destinations[i:i+batch_size]
        elements = get_walking_details(lat, lng, batch_dest, api_key)
        if not elements:
            continue

        for j, element in enumerate(elements):
            if element["status"] == "OK":
                time_sec = element["duration"]["value"]
                distance_m = element["distance"]["value"]
                if time_sec < min_time:
                    min_time = time_sec
                    nearest_station_name = stations[i + j]["name"]
                    nearest_distance = distance_m

    if nearest_station_name:
        return {
            "nearest_subway": nearest_station_name,
            "walking_time": round(min_time / 60, 1),  # 分钟
            "walking_distance": nearest_distance  # 米
        }
    else:
        return {"nearest_subway": None, "walking_time": None, "walking_distance": None}


# ------------------- 主程序开始 -------------------
# 读取输入文件（适配你的列名：ID, LATITUDE, LONGTITUDE）
print("[步骤1] 正在读取Excel文件...")
try:
    df = pd.read_excel(
        "/Users/yangyidi/Library/CloudStorage/OneDrive-TheUniversityofHongKong-Connect/Documents/Research/Projects/Cross-border/Data/EPRC_v3.2.xlsx")  # 确保文件路径正确
    print(f"成功读取文件，共 {len(df)} 条数据")
    print("列名验证：", df.columns.tolist())  # 打印列名用于检查
except Exception as e:
    print(f"文件读取失败！错误：{str(e)}")
    exit()

# 检查列名是否存在
required_columns = ["ID", "LATITUDE_NEW", "LONGTITUDE_NEW"]
if not all(col in df.columns for col in required_columns):
    print(f"错误：Excel必须包含列 {required_columns}，当前列名为：{df.columns.tolist()}")
    exit()

# 初始化进度条
results = []
print("\n[步骤2] 开始处理经纬度数据...")
pbar = tqdm(df.iterrows(), total=len(df))

# 遍历处理每个地点
for idx, row in pbar:
    retries = 0
    success = False

    while retries < MAX_RETRIES and not success:
        api_key = API_KEYS[current_key_idx]
        try:
            result = process_location(row, api_key)
            results.append(result)
            success = True
            time.sleep(RATE_LIMIT_DELAY)
        except Exception as e:
            logging.error(f"Error processing ID {row['ID']}: {str(e)}")
            retries += 1
            if "OVER_QUERY_LIMIT" in str(e):
                current_key_idx = (current_key_idx + 1) % len(API_KEYS)
                print(f"API配额不足，已切换密钥（当前密钥索引：{current_key_idx}）")
            time.sleep(5)

    if not success:
        print(f"处理失败：ID {row['ID']} 超过最大重试次数")
        results.append(
            {"nearest_mtr": None, "walking_time(min)": None, "walking_distance(m)": None})

# 合并结果并保存
print("\n[步骤3] 正在保存结果到Excel...")
output_df = pd.concat([df, pd.DataFrame(results)], axis=1)
output_df.to_excel("output_with_mtr.xlsx", index=False)
print("处理完成！结果已保存到 output_with_subway.xlsx")
