import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
from typing import List
import re

# 链家基础地址
BASE_URL = 'https://sz.lianjia.com/chengjiao/'
# 登录后从浏览器接口中获取
COOKIE = 'lianjia_uuid=9d3aecff-1983-4cfa-ac17-8e77c5ef87ee; _ga=GA1.2.1352918855.1739785054; crosSdkDT2019DeviceId=fqfasp-vtswrp-ps90z8qjo9sauje-dndnjulqt; ftkrc_=763a75e0-0fc6-4b73-88f4-e1c19ca995f4; lfrc_=6936621a-316e-4474-81e9-3a212c9dddea; _ga_QJN1VP0CMS=GS1.2.1739785054.1.1.1739785120.0.0.0; _ga_KJTRWRHDL1=GS1.2.1739785054.1.1.1739785120.0.0.0; _ga_XLL3Z3LPTW=GS1.2.1740123937.1.0.1740123937.0.0.0; _ga_NKBFZ7NGRV=GS1.2.1740123937.1.0.1740123937.0.0.0; beikeBaseData=%7B%22parentSceneId%22%3A%22415745271043591937%22%7D; _ga_XRDEC2G0T9=GS1.2.1741855873.2.1.1741855900.0.0.0; _ga_XGP5EDPZTV=GS1.2.1741855872.2.1.1741855900.0.0.0; _ga_SNG6R1B3VY=GS1.2.1741855872.2.1.1741855900.0.0.0; _jzqc=1; HMACCOUNT=8D2748791BA67437; lianjia_ssid=e8d3da4c-bbe5-430a-8157-6ff3a426df0b; select_city=440300; _jzqckmp=1; _gid=GA1.2.304418285.1742355297; sensorsdata2015jssdkcross=%7B%22distinct_id%22%3A%221951344fc8b3e-0af4ecdea37a67-26011b51-3686400-1951344fc8cfa9%22%2C%22%24device_id%22%3A%221951344fc8b3e-0af4ecdea37a67-26011b51-3686400-1951344fc8cfa9%22%2C%22props%22%3A%7B%22%24latest_traffic_source_type%22%3A%22%E7%9B%B4%E6%8E%A5%E6%B5%81%E9%87%8F%22%2C%22%24latest_referrer%22%3A%22%22%2C%22%24latest_referrer_host%22%3A%22%22%2C%22%24latest_search_keyword%22%3A%22%E6%9C%AA%E5%8F%96%E5%88%B0%E5%80%BC_%E7%9B%B4%E6%8E%A5%E6%89%93%E5%BC%80%22%7D%7D; _jzqa=1.3386205429234372600.1739785042.1742372894.1742381028.9; _jzqx=1.1739785042.1742381028.7.jzqsr=google%2Ecom|jzqct=/.jzqsr=sz%2Elianjia%2Ecom|jzqct=/chengjiao/futianqu/; Hm_lvt_46bf127ac9b856df503ec2dbf942b67e=1741855953; hip=8QCFtxqpGnmqXyK5YVmWcC9tSFeX7olDQNxd0q1G6HlgQ5KR9CYpkDlQwz12UXO49v-DGN16OzkjYsLH6ACC2-QjJE4BJHPZZNNckKa-UhtSO3H0yGqFwEzVcwYEvSXdVDd_dhcgtJSz17mmVgEOk2kgTscZjAmbHL6WxlX657_r837NDMttYGRU0w%3D%3D; login_ucid=2000000467299247; lianjia_token=2.0013facebb458bc8f80257e78a7efe3e03; lianjia_token_secure=2.0013facebb458bc8f80257e78a7efe3e03; security_ticket=ootc7cLbPptRt8w+6ZyWUO5bJpb9PfHpQrW01XYE6q8TrLhir39d1c91ZJikU9e4JtoOFD0X4bx6sbxBBR4rzFpJA+DWuey5gQP8F7vTF3oHZNqxtFHhx8pmsXqpE2BrN/HAxoyRVqNqoZN7BMq/WAR5mR1KcoiYlIfuTJKU/zY=; Hm_lpvt_46bf127ac9b856df503ec2dbf942b67e=1742384842; _jzqb=1.16.10.1742381028.1; _gat=1; _gat_global=1; _gat_new_global=1; _gat_dianpu_agent=1; _ga_C4R21H79WC=GS1.2.1742381039.10.1.1742384844.0.0.0'
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
            transprice = house.find("div", class_="totalPrice").find("span", class_="number").text.strip()
            direction = house.find("div", class_="houseInfo").get_text(strip=True)
            floor = house.find("div", class_="positionInfo").get_text(strip=True)
            match = re.search(r'(.+?$共?\d+层?$)', floor) #匹配到第一个括号前的内容
            if match:
                floor_level = match.group(1).strip()  
            else:
                floor_level = floor.split()[0]  # 容错处理
            unitprice = house.find("div", class_="unitPrice").find("span", class_="number").text.strip()

            # 挂牌+成交周期
            listTOM = house.find("div", class_="dealCycleeInfo").find("span", class_="dealCycleTxt")
            listTOMall = listTOM.find_all("span", recursive=False)  # 仅查找直接子集
            list_text = listTOMall[0].get_text(strip=True)
            tom_text = listTOMall[1].get_text(strip=True)
            listprice = re.search(r'\d+', list_text).group()  
            tom = re.search(r'\d+', tom_text).group()  

            row = [id, title, estate_name, area, dealDate, transprice, listprice, tom, unitprice, direction, floor_level, bedroom_num, living_room_num, link]
            #########################################################
            data.append(row)
        except Exception as e:
            print(f"爬取 {url} 失败, 需重新登录, 错误：{e}")
    return data

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

"""保存文件到csv"""


def save_as_csv(data: List[List[str]], columns: List[str], file_name: str) -> None:
    df = pd.DataFrame(data, columns=columns)
    file_path = f'{OUT_DIR}/{file_name}.csv'
    df.to_csv(file_path, index=False, encoding="utf-8-sig")
    print(f"爬取完成，数据已保存到{file_path}")


# 程序主入口
if __name__ == "__main__":
    house_info = get_chengjiao_info_by_page(1, 1)
    # TODO: 把字段对应的表头顺序一一对应补充到这里
    info_columns = ['id','title','estate_name','area','trans_date','transprice', 'listprice','TOM','unitprice', 'direction', 'floor', 'bedroom', 'living_room','link']
    save_as_csv(house_info, info_columns, '成交列表信息_P1')