import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
import re

# 设置请求头，模拟浏览器访问
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

# 深圳成交房源页面
city = "sz"
base_url = f"https://{city}.lianjia.com/chengjiao/"

# 存储数据
data_list = []

# 爬取前 5 页数据
for page in range(1, 6):
    url = f"{base_url}pg{page}/"
    print(f"正在爬取：{url}")

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"页面请求失败，状态码：{response.status_code}")
        break

    soup = BeautifulSoup(response.text, "html.parser")
    house_list = soup.find_all("div", class_="info")

    for house in house_list:
        try:
            # 标题
            title = house.find("div", class_="title").text.strip()

            # 链家编号（从URL提取）
            link = house.find("a")["href"]
            house_id = re.search(r"/chengjiao/(\d+)\.html",
                                 link).group(1) if link else None

            # 成交价
            price = house.find("div", class_="totalPrice").text.strip()

            # 成交日期
            deal_date = house.find("div", class_="dealDate").text.strip()

            # 额外数据需要访问详情页
            detail_url = f"https://{city}.lianjia.com{link}"
            detail_response = requests.get(detail_url, headers=headers)
            detail_soup = BeautifulSoup(detail_response.text, "html.parser")

            # 挂牌价
            price_info = detail_soup.find(text="挂牌价格")
            listing_price = price_info.find_next(
                "span").text.strip() if price_info else "N/A"

            # 上市日期
            listing_date_info = detail_soup.find(text="挂牌时间")
            listing_date = listing_date_info.find_next(
                "span").text.strip() if listing_date_info else "N/A"

            # 房屋面积
            area_info = detail_soup.find(text="建筑面积")
            area = area_info.find_next(
                "span").text.strip() if area_info else "N/A"

            # 带看次数
            views_info = detail_soup.find(text="带看次数")
            views = views_info.find_next(
                "span").text.strip() if views_info else "N/A"

            # 关注人数
            follows_info = detail_soup.find(text="关注人数")
            follows = follows_info.find_next(
                "span").text.strip() if follows_info else "N/A"

            # 浏览次数
            views_count_info = detail_soup.find(text="浏览次数")
            views_count = views_count_info.find_next(
                "span").text.strip() if views_count_info else "N/A"

            # 调价次数
            price_changes_info = detail_soup.find(text="调价次数")
            price_changes = price_changes_info.find_next(
                "span").text.strip() if price_changes_info else "N/A"

            # 所在楼层
            floor_info = detail_soup.find(text="所在楼层")
            floor = floor_info.find_next(
                "span").text.strip() if floor_info else "N/A"

            # 房屋类型
            house_type_info = detail_soup.find(text="房屋类型")
            house_type = house_type_info.find_next(
                "span").text.strip() if house_type_info else "N/A"

            # 具体位置信息（小区名称）
            position_info = detail_soup.find("div", class_="communityName").text.strip(
            ) if detail_soup.find("div", class_="communityName") else "N/A"

            # 房屋朝向
            orientation_info = detail_soup.find(text="房屋朝向")
            orientation = orientation_info.find_next(
                "span").text.strip() if orientation_info else "N/A"

            # 装修情况
            decoration_info = detail_soup.find(text="装修情况")
            decoration = decoration_info.find_next(
                "span").text.strip() if decoration_info else "N/A"

            # 是否配备电梯
            elevator_info = detail_soup.find(text="配备电梯")
            elevator = elevator_info.find_next(
                "span").text.strip() if elevator_info else "N/A"

            # 梯户比例
            ladder_info = detail_soup.find(text="梯户比例")
            ladder = ladder_info.find_next(
                "span").text.strip() if ladder_info else "N/A"

            # 卧室数量
            bedroom_count = re.search(r"(\d+)室", title)
            bedrooms = bedroom_count.group(1) if bedroom_count else "N/A"

            # 客厅数量
            livingroom_count = re.search(r"(\d+)厅", title)
            livingrooms = livingroom_count.group(
                1) if livingroom_count else "N/A"

            # 浴室数量（一般不会直接标注，可能需要额外处理）
            bathroom_count = re.search(r"(\d+)卫", title)
            bathrooms = bathroom_count.group(1) if bathroom_count else "N/A"

            # 存入数据
            data_list.append([
                title, house_id, price, listing_price, deal_date, listing_date, area,
                views, follows, views_count, price_changes, floor, house_type, position_info,
                orientation, decoration, elevator, ladder, bedrooms, bathrooms, livingrooms
            ])

            print(f"成功获取：{title}")

            # 避免访问过快被封
            time.sleep(random.uniform(1, 3))

        except Exception as e:
            print(f"爬取 {title} 失败，错误：{e}")

# 存储数据到 CSV
df = pd.DataFrame(data_list, columns=[
    "标题", "链家编号", "成交价", "挂牌价", "成交日期", "上市日期", "房屋面积", "带看次数",
    "关注人数", "浏览次数", "调价次数", "所在楼层", "房屋类型", "位置信息", "房屋朝向",
    "装修情况", "配备电梯", "梯户比例", "卧室个数", "浴室个数", "客厅个数"
])

df.to_csv("shenzhen_lianjia_chengjiao.csv", index=False, encoding="utf-8-sig")
print("爬取完成，数据已保存到 shenzhen_lianjia_chengjiao.csv")
