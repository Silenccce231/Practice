import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
from typing import List
import re

# 链家基础地址
BASE_URL = 'https://sz.lianjia.com/chengjiao/'
# 登录后从浏览器接口中获取
COOKIE = 'SECKEY_ABVK=3+tpEAlMaaDOuAX5EvKexgbZ8viAZtO/zGNAjeedDNk%3D; BMAP_SECKEY=yfRdNQ-akxeyGdklD3LygNSdMLEFmA4a5sxND8HFG745ytJEp-X-o8cM3aCgKnXUsu0qTju4KL_D00252YIFP5KlWqkvGP90vpZBbKjuoYBl5wnImP7hImS77juHTms9jsLroqVRAm-uFq3mcIgmfBcC_a1AZZDl_42uBXvvtBmxChO6HPUmREdzOp2BLUIQ; lianjia_uuid=9d3aecff-1983-4cfa-ac17-8e77c5ef87ee; _ga=GA1.2.1352918855.1739785054; crosSdkDT2019DeviceId=fqfasp-vtswrp-ps90z8qjo9sauje-dndnjulqt; ftkrc_=763a75e0-0fc6-4b73-88f4-e1c19ca995f4; lfrc_=6936621a-316e-4474-81e9-3a212c9dddea; _ga_QJN1VP0CMS=GS1.2.1739785054.1.1.1739785120.0.0.0; _ga_KJTRWRHDL1=GS1.2.1739785054.1.1.1739785120.0.0.0; _ga_XLL3Z3LPTW=GS1.2.1740123937.1.0.1740123937.0.0.0; _ga_NKBFZ7NGRV=GS1.2.1740123937.1.0.1740123937.0.0.0; beikeBaseData=%7B%22parentSceneId%22%3A%22415745271043591937%22%7D; _ga_XRDEC2G0T9=GS1.2.1741855873.2.1.1741855900.0.0.0; _ga_XGP5EDPZTV=GS1.2.1741855872.2.1.1741855900.0.0.0; _ga_SNG6R1B3VY=GS1.2.1741855872.2.1.1741855900.0.0.0; _jzqc=1; Hm_lvt_46bf127ac9b856df503ec2dbf942b67e=1739785042,1741855953; HMACCOUNT=8D2748791BA67437; _qzjc=1; lianjia_ssid=e8d3da4c-bbe5-430a-8157-6ff3a426df0b; select_city=440300; login_ucid=2000000467299247; lianjia_token=2.0014294c3142584a72058465001e098e6b; lianjia_token_secure=2.0014294c3142584a72058465001e098e6b; security_ticket=WgZoG/9dlJeNBQ4zNgUQbtbDOSfrwnScAcwXSL05VlKTGDgxsb8qJ1NzFulK5SXWESQxAR/jT4CW3XIWQse3aLoBSnjlnq5s5owWJg/F25OQxFU+Ixo3e9kzKeqjYdYCk3e7bSDbsWIj/ERX26RvmjCvtq3i5JXcMWkbCjPhyfI=; _jzqa=1.3386205429234372600.1739785042.1741865488.1742355287.7; _jzqx=1.1739785042.1742355287.5.jzqsr=google%2Ecom|jzqct=/.jzqsr=clogin%2Elianjia%2Ecom|jzqct=/; _jzqckmp=1; _gid=GA1.2.304418285.1742355297; sensorsdata2015jssdkcross=%7B%22distinct_id%22%3A%221951344fc8b3e-0af4ecdea37a67-26011b51-3686400-1951344fc8cfa9%22%2C%22%24device_id%22%3A%221951344fc8b3e-0af4ecdea37a67-26011b51-3686400-1951344fc8cfa9%22%2C%22props%22%3A%7B%22%24latest_traffic_source_type%22%3A%22%E7%9B%B4%E6%8E%A5%E6%B5%81%E9%87%8F%22%2C%22%24latest_referrer%22%3A%22%22%2C%22%24latest_referrer_host%22%3A%22%22%2C%22%24latest_search_keyword%22%3A%22%E6%9C%AA%E5%8F%96%E5%88%B0%E5%80%BC_%E7%9B%B4%E6%8E%A5%E6%89%93%E5%BC%80%22%7D%7D; _qzja=1.125872156.1739785141951.1741865488288.1742355286620.1742361539049.1742361559377.0.0.0.48.7; _qzjb=1.1742355286620.14.0.0.0; _qzjto=14.1.0; _jzqb=1.14.10.1742355287.1; Hm_lpvt_46bf127ac9b856df503ec2dbf942b67e=1742361560; srcid=eyJ0Ijoie1wiZGF0YVwiOlwiZTlhNjY4OTUwYTY0MWJlOTQ4ZGNlZGIyMzg2OTg1NDNiNTc1YmYxNTdjZTQ5ODgxZDcyZTU2OTFlNzYwOTZkNzQ3YmJlMDY1Y2FhZjI2Y2EyOTA3OWJjOGM5ZDNmODBmYWQ1MzA2MWExNDM0YzViOWVjMWVjYTQ4NTZhODllMjkzYWMxYjYwN2Q2MWFmMWNhYjI4NDkwMWM5MjY2ZmI5MjE4ODIyOWRlNTc5OTIxOGJhYTU4NTZhOWM0MDM5YWYyZTY1NDEzMjE0MDdmNzY0ZjQ3NmUzZmI0MTAzODk3ZjEzN2Q5YmFlMGIyZjEzMzliZDI1MmM4NzVlY2M1ZTk0ZVwiLFwia2V5X2lkXCI6XCIxXCIsXCJzaWduXCI6XCIwMDU5MmM3M1wifSIsInIiOiJodHRwczovL3N6LmxpYW5qaWEuY29tL2NoZW5namlhby8iLCJvcyI6IndlYiIsInYiOiIwLjEifQ==; _ga_C4R21H79WC=GS1.2.1742359527.8.1.1742361571.0.0.0'
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