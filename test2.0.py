import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
from typing import List
from pathlib import Path
import re

# 链家基础地址
BASE_URL = 'https://sz.lianjia.com/chengjiao/'
# 登录后从浏览器接口中获取
COOKIE = 'SECKEY_ABVK=3+tpEAlMaaDOuAX5EvKexjLRZTTVh0yDEEMDc/mN7LY%3D; BMAP_SECKEY=yfRdNQ-akxeyGdklD3LygLE_n_iuuunvFwUr9_BlGpyOxPeSZ7V7_eQbWHtFl5JIhlLAwAyIzDGVkPvZ2FCrZo2JCG2ODzEMe4YRt8tiAU7xGfKyD2GvYtZuz6S6-uS278KmidZx8wv9NSIS93NLtjB1QYlXeI_uyaMkmJJxItpLtZq8rmmMntoCeZnYYg6w; lianjia_uuid=9d3aecff-1983-4cfa-ac17-8e77c5ef87ee; sensorsdata2015jssdkcross=%7B%22distinct_id%22%3A%221951344fc8b3e-0af4ecdea37a67-26011b51-3686400-1951344fc8cfa9%22%2C%22%24device_id%22%3A%221951344fc8b3e-0af4ecdea37a67-26011b51-3686400-1951344fc8cfa9%22%2C%22props%22%3A%7B%22%24latest_traffic_source_type%22%3A%22%E8%87%AA%E7%84%B6%E6%90%9C%E7%B4%A2%E6%B5%81%E9%87%8F%22%2C%22%24latest_referrer%22%3A%22https%3A%2F%2Fwww.google.com%2F%22%2C%22%24latest_referrer_host%22%3A%22www.google.com%22%2C%22%24latest_search_keyword%22%3A%22%E6%9C%AA%E5%8F%96%E5%88%B0%E5%80%BC%22%7D%7D; _ga=GA1.2.1352918855.1739785054; crosSdkDT2019DeviceId=fqfasp-vtswrp-ps90z8qjo9sauje-dndnjulqt; ftkrc_=763a75e0-0fc6-4b73-88f4-e1c19ca995f4; lfrc_=6936621a-316e-4474-81e9-3a212c9dddea; _ga_QJN1VP0CMS=GS1.2.1739785054.1.1.1739785120.0.0.0; _ga_KJTRWRHDL1=GS1.2.1739785054.1.1.1739785120.0.0.0; _ga_XLL3Z3LPTW=GS1.2.1740123937.1.0.1740123937.0.0.0; _ga_NKBFZ7NGRV=GS1.2.1740123937.1.0.1740123937.0.0.0; select_city=440300; lianjia_ssid=07f444a0-bd29-4cad-ab1d-2ea4f44ab007; _gid=GA1.2.329068500.1741855873; session_id=8858dc99-0053-e0ac-a41d-6febc854ac56; beikeBaseData=%7B%22parentSceneId%22%3A%22415745271043591937%22%7D; _ga_XRDEC2G0T9=GS1.2.1741855873.2.1.1741855900.0.0.0; _ga_XGP5EDPZTV=GS1.2.1741855872.2.1.1741855900.0.0.0; _ga_SNG6R1B3VY=GS1.2.1741855872.2.1.1741855900.0.0.0; login_ucid=2000000467299247; lianjia_token=2.00156fd99b431edfd804c2f0aae20b45da; lianjia_token_secure=2.00156fd99b431edfd804c2f0aae20b45da; security_ticket=bPxpKMZ63O2+U1y9x7TxujLwV93vYDpjiaf4+fkHx0xjvlxEG1AkFsG1Ve2znz6OcNFeUqMmKO4x/J4f5G7J5FQdOqEz1Tq7s+unkLxOcw2++d3xqgMFqgOSjpBxdkgWTVO2Ayr48FojzGeLgOAetcfs8pvTLUD7MEpg12Wi8Ew=; _jzqc=1; _jzqckmp=1; Hm_lvt_46bf127ac9b856df503ec2dbf942b67e=1739785042,1741855953; HMACCOUNT=8D2748791BA67437; _qzjc=1; _qzja=1.125872156.1739785141951.1741855953622.1741858559951.1741855953622.1741858559951.0.0.0.33.5; _qzjto=2.2.0; _jzqa=1.3386205429234372600.1739785042.1741855952.1741858560.5; _jzqx=1.1739785042.1741858560.4.jzqsr=google%2Ecom|jzqct=/.jzqsr=sz%2Elianjia%2Ecom|jzqct=/chengjiao/; Hm_lpvt_46bf127ac9b856df503ec2dbf942b67e=1741858560; _ga_C4R21H79WC=GS1.2.1741858571.5.0.1741858571.0.0.0; srcid=eyJ0Ijoie1wiZGF0YVwiOlwiZTlhNjY4OTUwYTY0MWJlOTQ4ZGNlZGIyMzg2OTg1NDNiNTc1YmYxNTdjZTQ5ODgxZDcyZTU2OTFlNzYwOTZkNzQ3YmJlMDY1Y2FhZjI2Y2EyOTA3OWJjOGM5ZDNmODBmNTk2NzAzYTAwNTI0MTQ5NGM4MDc2Y2I3MDFhMjAzNGI4YTViZDhiZDdmMjg1MWQxYmUyYjQzZDUwMTU1OWYwYWY3ZmJiNDhkNzQzOWU4YzJhZDFiMmRmZDYxMzU5ZTgwOGE0OTUxNGYzZTc0MmNiNWExNjQ1YmE2YmQ0Mjk2OWJmMDg5YThkODcyMzBlOTA5NjExNDhjNWU5OWY1MWY2M1wiLFwia2V5X2lkXCI6XCIxXCIsXCJzaWduXCI6XCIyYzJmMDgzYVwifSIsInIiOiJodHRwczovL3N6LmxpYW5qaWEuY29tL2NoZW5namlhby8xMDUxMTczMjc1ODIuaHRtbCIsIm9zIjoid2ViIiwidiI6IjAuMSJ9'
# 结果储存位置
OUT_DIR =  Path("output")
file_path = OUT_DIR/ "data.csv"
OUT_DIR.mkdir(parents=True, exist_ok=True)


"""
获得页面html解析后的soup对象
"""
def get_html_soup(url:str) -> BeautifulSoup:
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
def get_chengjiao_info_by_page(start_page:int, end_page:int) -> List[List[str]]:
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
        # 阻塞2秒模拟人类分页访问
        time.sleep(2)
    return all_data

"""
获得单个成交页面的信息[[xxx,xxx],[xxx,xxx],...]
"""
def get_chengjiao_info(url:str) -> List[List[str]]:
    soup = get_html_soup(url)
    if soup == None:
        return []
    house_list:List[BeautifulSoup] = soup.find_all('div', class_='info')
    # 遍历house_list找到你需要的信息
    data = [] # 二维数组
    for house in house_list:
        try:
            ############# TODO:根据标签找到你所需要的信息 #############
            ### 从标题中提取地产名+房间信息+面积
            title_div = house.find('div', class_='title')
            title = title_div.text.strip()
            cleaned_text = ' '.join(title.split()) 
            parts = cleaned_text.split(' ')
            estate_name = parts[0]
            room_info = parts[1]
            area = parts[2]

            ###从房间信息分别提取卧室数量+客厅数量
            pattern = r"(\d+)室(\d+)厅"  # 匹配模式：数字+室+数字+厅
            match = re.search(pattern, room_info)
            if match:
                bedroom_num = int(match.group(1))   # 卧室数量：3 → int
                living_room_num = int(match.group(2)) # 客厅数量：1 → int
            else: # 容错处理（如字段缺失或格式不符）
                bedroom_num = 0 
                living_room_num = 0
            row = [estate_name, area, bedroom_num, living_room_num]   
            data.append(row)
        except Exception as e:
            print(f"爬取 {title} 失败，错误：{e}")
    return data

"""保存文件到csv"""
def save_as_csv(data:List[List[str]], columns:List[str], file_name:str) -> None:
    df = pd.DataFrame(data, columns=columns)
    df.to_csv(file_path, index=False, encoding="utf-8-sig")
    print(f"爬取完成，数据已保存到{file_path}")



"""从链接中解析house的id"""
def parse_house_id(url:str) -> str:
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
    house_info = get_chengjiao_info_by_page(1, 2)
    # TODO: 把字段对应的表头顺序一一对应补充到这里
    info_columns = ['estate_name', 'area','bedroom_num', 'living_room_num']
    save_as_csv(house_info, info_columns, '成交列表信息_P1-P2')