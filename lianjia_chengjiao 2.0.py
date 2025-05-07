import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
from typing import List
import re

# 链家基础地址
BASE_URL = 'https://sz.lianjia.com/chengjiao/'
# 登录后从浏览器接口中获取
COOKIE = 'lianjia_uuid=547d3d52-a643-4087-9a67-e88845388c4a; _ga=GA1.2.1452629490.1740069522; crosSdkDT2019DeviceId=ev0z9w--hqoi59-6ao2hzdtadf7adw-iu6q0rpu7; ftkrc_=37fb9819-ebcd-42e4-b73f-085e8421596f; lfrc_=ec9ecc62-7a9d-4d46-9627-e6ca90b10b46; sensorsdata2015jssdkcross=%7B%22distinct_id%22%3A%221952439a73b3f0-08d9f9bbee6103-1d525636-1764000-1952439a73c8ce%22%2C%22%24device_id%22%3A%221952439a73b3f0-08d9f9bbee6103-1d525636-1764000-1952439a73c8ce%22%2C%22props%22%3A%7B%22%24latest_traffic_source_type%22%3A%22%E7%9B%B4%E6%8E%A5%E6%B5%81%E9%87%8F%22%2C%22%24latest_referrer%22%3A%22%22%2C%22%24latest_referrer_host%22%3A%22%22%2C%22%24latest_search_keyword%22%3A%22%E6%9C%AA%E5%8F%96%E5%88%B0%E5%80%BC_%E7%9B%B4%E6%8E%A5%E6%89%93%E5%BC%80%22%7D%7D; Hm_lvt_46bf127ac9b856df503ec2dbf942b67e=1740325246,1741012099; HMACCOUNT=F26A4887B55DF921; _jzqc=1; _ga_XRDEC2G0T9=GS1.2.1742294321.3.1.1742294465.0.0.0; _ga_XGP5EDPZTV=GS1.2.1742294321.3.1.1742294465.0.0.0; _ga_SNG6R1B3VY=GS1.2.1742294321.3.1.1742294465.0.0.0; lianjia_ssid=0a28be61-e02f-4fc7-96fa-bfe6b92b0e68; login_ucid=2000000467299247; lianjia_token=2.001213e13c4462e77f03bec80d61b28ca3; lianjia_token_secure=2.001213e13c4462e77f03bec80d61b28ca3; security_ticket=a/CZwNMLvV7BIAWwwbr1K6owH/p0Bi0WOJhn2C3WoRgH7kpUr40iiyqOcZ7Ilmqp+Gz9Y6nKADPQI06FmZIPoeaENKJq3w1QGiJBWsFTIEtCGHn7j9Z2l4y/gWh7H0HogVJMRta1ItK+5Bf5fOppKJtB/mNyjNV7WopYYbLUdtM=; select_city=440300; session_id=e97ae020-9b84-ef33-aec5-b973cd4408c0; beikeBaseData=%7B%22parentSceneId%22%3A%22452182030296064513%22%7D; jiaxin_token=2.001213e13c4462e77f03bec80d61b28ca3; hip=OjMXq5ikywtFmKs6Y-xq0rUmnp8jXf8jy92jP_P-BVcbj5cwHLGHpO6cB8qF82TgeE193muuwHR7BmoogLc6AG6s07O34vlNfs1KOfbZz8BwHa0QlaqliMh7FFttCz019BrEpnWZKvw6ct5IhWtbgKhs8rNs5gu0EIofyFQOAIUEcmBHiseZKdGnyw%3D%3D; _jzqa=1.493861098530465800.1740325246.1741012100.1742398906.5; _jzqx=1.1740998231.1742398906.3.jzqsr=clogin%2Elianjia%2Ecom|jzqct=/.jzqsr=hip%2Elianjia%2Ecom|jzqct=/; _jzqckmp=1; Hm_lpvt_46bf127ac9b856df503ec2dbf942b67e=1742398906; _jzqb=1.1.10.1742398906.1; _gid=GA1.2.1275773507.1742398916; _ga_C4R21H79WC=GS1.2.1742398916.5.0.1742398916.0.0.0'
# 结果储存位置
OUT_DIR = './output'


"""
获得页面html解析后的soup对象
"""


def get_html_soup(url: str) -> BeautifulSoup:
    # 设置请求头，模拟浏览器访问
    headers = {
        "Cookie": COOKIE,
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36"
    }
    # 发送GET请求
    response = requests.get(url=url, headers=headers)
    if response.status_code != 200:
        print(f"页面 {url} 请求失败，状态码：{response.status_code}")
        return None
    return BeautifulSoup(response.text, "html.parser")


"""
获得成交页面所有列表页信息[[xxx,xxx],[xxx,xxx],...]
"""


def get_chengjiao_info_by_page(start_page: int, end_page: int) -> List[List[str]]:
    all_data = []
    # 遍历每一页得到
    for page in range(start_page, end_page+1):
        url = ''
        if page == 1:
            url = BASE_URL
        else:
            url = f"{BASE_URL}pg{page}/"
        print(f"正在爬取：{url}")
        page_data = get_chengjiao_info(url)
        all_data += page_data
        # 阻塞5秒模拟人类分页访问
        time.sleep(5)
    return all_data


"""
获得单个成交页面的信息[[xxx,xxx],[xxx,xxx],...]
"""


def get_chengjiao_info(url: str) -> List[List[str]]:
    soup = get_html_soup(url)
    if soup == None:
        return []
    house_list: List[BeautifulSoup] = soup.find_all('div', class_='info')
    # 遍历house_list找到你需要的信息
    data = []  # 二维数组
    for house in house_list:
        try:
            ############# TODO:根据标签找到你所需要的信息 #############
            title_div = house.find('div', class_='title')
            title = title_div.text.strip()
            cleaned_text = ' '.join(title.split())
            parts = cleaned_text.split(' ')
            estate_name = parts[0]
            room_info = parts[1]
            area_text = parts[2]
            area = re.search(r'\d+', area_text).group()

            # 从房间信息分别提取卧室数量+客厅数量
            pattern = r"(\d+)室(\d+)厅"  # 匹配模式：数字+室+数字+厅
            match = re.search(pattern, room_info)
            if match:
                bedroom_num = int(match.group(1))   # 卧室数量：3 → int
                living_room_num = int(match.group(2))  # 客厅数量：1 → int
            else:  # 容错处理（如字段缺失或格式不符）
                bedroom_num = 0
                living_room_num = 0

            link = title_div.find('a').get('href')
            id = parse_house_id(link)
            dealDate = house.find("div", class_="dealDate").text.strip()
            transprice = house.find("div", class_="totalPrice").find(
                "span", class_="number").text.strip()
            direction = house.find(
                "div", class_="houseInfo").get_text(strip=True)
            floor = house.find(
                "div", class_="positionInfo").get_text(strip=True)
            match = re.search(r'(.+?$共?\d+层?$)', floor)  # 匹配到第一个括号前的内容
            if match:
                floor_level = match.group(1).strip()
            else:
                floor_level = floor.split()[0]  # 容错处理
            unitprice = house.find("div", class_="unitPrice").find(
                "span", class_="number").text.strip()

            # 挂牌+成交周期
            listTOM = house.find("div", class_="dealCycleeInfo").find(
                "span", class_="dealCycleTxt")
            listTOMall = listTOM.find_all("span", recursive=False)  # 仅查找直接子集
            list_text = listTOMall[0].get_text(strip=True)
            tom_text = listTOMall[1].get_text(strip=True)
            listprice = re.search(r'\d+', list_text).group()
            tom = re.search(r'\d+', tom_text).group()

            row = [id, title, estate_name, area, dealDate, transprice, listprice, tom,
                   unitprice, direction, floor_level, bedroom_num, living_room_num, link]
            #########################################################
            data.append(row)
        except Exception as e:
            print(f"爬取 {url} 失败, 需重新登录, 错误：{e}")
    return data


def get_chengjiao_details(url_list: List[str]) -> List[List[str]]:
    details = []
    for url in url_list:
        print(f"正在爬取：{url}")
        detail = get_chengjiao_detail(url)
        details.append(detail)
        # 阻塞5秒模拟人类分页访问
        time.sleep(5)
    return details


"""获得单个成交页面的详情信息"""


def get_chengjiao_detail(url: str) -> List[str]:
    soup = get_html_soup(url)
    if soup == None:
        return []
    # 返回结果为一维数组
    data = []
    try:
        # 从url中解析单个成交的id
        id = parse_house_id(url)
        data.append(id)

        # 解析线上信息
        msg = soup.find('div', class_='msg')
        span_tags: List[BeautifulSoup] = msg.find_all('span')
        msg_labels = ['调价（次）', '带看（次）', '关注（人）', '浏览（次）']
        msg_data = [''] * len(msg_labels)
        for span in span_tags:
            # 获得标签值
            value = span.find('label').get_text(strip=True)
            # 获得标签名
            name = span.get_text(strip=True).replace(value, '')
            if name in msg_labels:
                # 保证返回结果和标签一致
                index = msg_labels.index(name)
                msg_data[index] = value
        data += msg_data

        # 解析基本属性
        base = soup.find('div', class_='base')
        li_tags: List[BeautifulSoup] = base.find_all('li')
        base_labels = ['房屋户型', '房屋朝向', '建成年代',
                       '装修情况', '梯户比例', '配备电梯', '建筑类型', '建筑结构']
        base_data = [''] * len(base_labels)
        # 新增厨卫存储位置（追加到数据末尾）
        kitchen_idx = len(base_labels)
        bathroom_idx = kitchen_idx + 1
        base_data += ['', '']  # 扩展存储空间
        # 新增户梯比字段
        ratio_idx = len(base_data)
        base_data += ['']
        for li in li_tags:
            # 获得标签名
            name = li.find('span').get_text(strip=True)
            # 获得标签值
            value = li.get_text(strip=True).replace(name, '')
            # 处理房屋户型特殊字段
            if name == '房屋户型':
                # 使用正则表达式分离厨卫信息
                kitchen = re.search(
                    # 2. 提取厨房数量
                    r'(\d+)厨', value).group(1) if re.search(r'\d+厨', value) else '0'
                bathroom = re.search(
                    # 3. 提取卫生间数量
                    r'(\d+)卫', value).group(1) if re.search(r'\d+卫', value) else '0'

                # 存储到扩展字段
                base_data[kitchen_idx] = f"{kitchen}厨"
                base_data[bathroom_idx] = f"{bathroom}卫"

            # 处理户梯比特殊字段
            if name == '梯户比例':
                match = re.search(r'(\d+)梯(\d+)户', value)
                if match:
                    elevators = int(match.group(1))
                    households = int(match.group(2))
                    # 计算梯户比（户型/电梯）
                    ratio = households / elevators if elevators != 0 else 0
                    base_data[ratio_idx] = f"{ratio:.1f}"  # 保留1位小数
                else:
                    base_data[ratio_idx] = '0.0'  # 异常值默认

            if name in base_labels:
                # 保证返回结果和标签一致
                index = base_labels.index(name)
                base_data[index] = value
        data += base_data

        # TODO: 添加交易属性信息
    except Exception as e:
        print(f"爬取详情页 {url} 失败, 需重新登录, 错误：{e}")
    return data


"""保存文件到csv"""


def save_as_csv(data: List[List[str]], columns: List[str], file_name: str) -> None:
    df = pd.DataFrame(data, columns=columns)
    file_path = f'{OUT_DIR}/{file_name}.csv'
    df.to_csv(file_path, index=False, encoding="utf-8-sig")
    print(f"爬取完成，数据已保存到{file_path}")


"""从链接中解析house的id"""


def parse_house_id(url: str) -> str:
    # 定义更通用的正则表达式模式
    pattern = r'https?://[^/]+/chengjiao/(\d+)\.html'
    # 使用re.search匹配URL
    match = re.search(pattern, url)

    # 如果匹配成功，返回ID
    if match:
        return match.group(1)
    else:
        return None


# 程序主入口
if __name__ == "__main__":
    test_url = 'https://sz.lianjia.com/chengjiao/105117332004.html'
    house_details = get_chengjiao_detail(test_url)
    print(house_details)
    # house_info = get_chengjiao_info_by_page(1, 1)
    # # TODO: 把字段对应的表头顺序一一对应补充到这里
    # info_columns = ['id', 'title', 'estate_name', 'area','trans_date', 'listprice', 'TOM', 'trans_price', 'unitprice', 'bedroom', 'living_room', 'direction', 'floor', 'link']
    # save_as_csv(house_info, info_columns, '成交列表信息_P1')
    # # 拿到所有详情url
    # detail_urls = [row[-1] for row in house_info]
    # house_details = get_chengjiao_details(detail_urls)
    # detail_columns = ['id', '调价（次）', '带看（次）',
    #                   '关注（人）', '浏览（次）', '房屋户型', '房屋朝向','建成年代', '装修情况', '梯户比例', '配备电梯','建筑类型','建筑结构','厨房数目','卫生间数目','户梯比']
    # save_as_csv(house_details, detail_columns, '成交房屋详情_P1')
