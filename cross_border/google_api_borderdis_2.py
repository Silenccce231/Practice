import pandas as pd
import requests
import time
import logging
from tqdm import tqdm
from datetime import datetime  # 新增模块用于处理时间

# ------------------- 配置模块 -------------------
logging.basicConfig(
    filename='port_commute.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s: %(message)s'
)
API_KEYS = ["AIzaSyCDj1wexToNnyeWzdE05q19JRvRX5_DaS0"]  # 需替换为有效API密钥
current_key_idx = 0  # 当前使用的API密钥索引
REQUEST_INTERVAL = 2  # 请求间隔防止超限

# ------------------- 口岸坐标库 -------------------
PORT_LOCATIONS = {
    # 格式：口岸名称 : (纬度, 经度)
    # 数据来源：https://www.hzmb.gov.hk/
    "深圳湾口岸": (22.500009325541157, 113.9449225833629),
    "皇岗口岸": (22.510301854924847, 114.07403675592798),
    "文锦渡口岸": (22.53757547810692, 114.1286652284366),
    "莲塘口岸": (22.552929052352503, 114.1536201621786),
    "罗湖口岸": (22.529726295458538, 114.1134729938289),
    "福田口岸": (22.515270575975155, 114.06577765278918),
    "香港西九龙": (22.304425501999223, 114.16498506919883)

}

# ------------------- 新增固定时间配置 -------------------
# 设置固定出发时间为2025年5月9日上午11点（北京时间）
FIXED_DEPARTURE = int(datetime(2025, 5, 9, 11, 0).timestamp())
print(
    f"固定出发时间：{datetime.fromtimestamp(FIXED_DEPARTURE).strftime('%Y-%m-%d %H:%M')}")

# ------------------- 核心函数（含换乘优化）-------------------


def get_commute_data(port_coords, dest_coords, api_key):
    """
    获取口岸到目标地点的公共交通数据
    :param port_coords: 元组 (纬度, 经度) - 口岸位置
    :param dest_coords: 元组 (纬度, 经度) - 目标地点位置
    :param api_key: 当前使用的API密钥
    :return: 包含时间、距离、换乘次数的字典，失败返回None
    """
    global current_key_idx

    url = "https://maps.googleapis.com/maps/api/distancematrix/json"
    params = {
        "origins": f"{port_coords[0]},{port_coords[1]}",    # 出发点为口岸
        "destinations": f"{dest_coords[0]},{dest_coords[1]}",  # 目的地为研究地点
        "mode": "transit",       # 交通模式设置为公共交通
        "transit_mode": "bus|subway|train",  # 包含巴士、地铁、火车
        "transit_routing_preference": "fewer_transfers",  # 新增：优先换乘少的路线
        "departure_time": FIXED_DEPARTURE,  # 修改为固定时间戳
        "key": api_key
    }

    try:
        # 发送API请求
        response = requests.get(url, params=params, timeout=15)
        data = response.json()

        # 处理API响应
        if data["status"] == "OK":
            element = data["rows"][0]["elements"][0]
            if element["status"] == "OK":
                # 解析换乘次数（需要Directions API才能精确获取，此处为估算）
                transfers = element.get("duration", {}).get(
                    "details", {}).get("transfers", 0)
                return {
                    "time": element["duration"]["value"],  # 单位：秒
                    "distance": element["distance"]["value"],  # 单位：米
                    "transfers": transfers  # 换乘次数
                }
            else:
                logging.warning(f"路线不可达 | 口岸:{port_coords} → 地点:{dest_coords}")
                return None
        elif data["status"] == "OVER_QUERY_LIMIT":
            logging.info(f"切换API密钥 | 原密钥:{api_key[:8]}...")
            current_key_idx = (current_key_idx + 1) % len(API_KEYS)
            return None
        else:
            logging.error(f"API错误:{data['status']} | 口岸:{port_coords}")
            return None
    except Exception as e:
        logging.error(f"请求异常:{str(e)}")
        return None

# ------------------- 主程序（新增换乘记录）-------------------


def main():
    """主控制流程"""
    # 数据加载阶段
    try:
        # 假设输入文件包含目标地点坐标
        df = pd.read_excel(
            "/Users/yangyidi/Library/CloudStorage/OneDrive-TheUniversityofHongKong-Connect/Documents/Research/Projects/Cross-border/Data/border_distance/border_dis_2.xlsx")
        required_cols = ["ID", "LATITUDE_NEW", "LONGTITUDE_NEW"]
        assert set(required_cols).issubset(df.columns)
        print(f"成功加载 {len(df)} 个目标地点")
    except Exception as e:
        print(f"数据加载失败: {str(e)}")
        return

    # 结果列初始化（新增换乘次数列）
    for port_name in PORT_LOCATIONS:
        df[f"{port_name}_time(min)"] = None  # 时间（分钟）
        df[f"{port_name}_distance(km)"] = None  # 距离（公里）
        # df[f"{port_name}_transfers"] = None  # 新增换乘次数
    df["nearest_port"] = None  # 最近口岸
    df["min_transit_time(min)"] = None  # 最短时间

    # 数据处理阶段
    pbar = tqdm(df.iterrows(), total=len(df))
    for idx, row in pbar:
        location_id = row["ID"]
        dest_coords = (row["LATITUDE_NEW"], row["LONGTITUDE_NEW"])

        min_time = float('inf')
        nearest_port = None

        # 对每个口岸计算通勤数据
        for port_name, port_coords in PORT_LOCATIONS.items():
            result = None
            retry_count = 0

            # 带重试的请求逻辑
            while retry_count < 3 and not result:
                api_key = API_KEYS[current_key_idx]
                result = get_commute_data(port_coords, dest_coords, api_key)

                if not result:
                    retry_count += 1
                    time.sleep(2 ** retry_count)  # 指数退避策略
                time.sleep(REQUEST_INTERVAL)

            # 结果记录
            if result:
                # 记录单个口岸数据
                df.at[idx, f"{port_name}_time(min)"] = round(
                    result["time"]/60, 2)
                df.at[idx, f"{port_name}_distance(km)"] = round(
                    result["distance"]/1000, 2)
                # 记录换乘次数
                # df.at[idx, f"{port_name}_transfers"] = result["transfers"]

                # 更新最短时间口岸
                if result["time"] < min_time:
                    min_time = result["time"]
                    nearest_port = port_name

        # 记录最优结果
        if nearest_port:
            df.at[idx, "nearest_port"] = nearest_port
            df.at[idx, "min_transit_time(min)"] = round(min_time/60, 2)

        # 进度更新
        pbar.set_description(f"处理进度 | 地点:{location_id}")

    # 结果保存
    df.to_excel("port_transit_results0512_2.xlsx", index=False)
    print("处理完成！结果已保存至 port_transit_results.xlsx")


if __name__ == "__main__":
    main()
