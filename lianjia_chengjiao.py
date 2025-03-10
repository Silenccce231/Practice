import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
from typing import List
import re

# 链家基础地址
BASE_URL = 'https://sz.lianjia.com/chengjiao/'
# 登录后从浏览器接口中获取
COOKIE = 'SECKEY_ABVK=PneWGxjnQ5vUuABNY0tjhvL+HebNvQt0P7XMHFz4ZVk%3D; BMAP_SECKEY=PneWGxjnQ5vUuABNY0tjhoBncaUz4KhJ4qvr7ocpkU3su1vPYfAfiuVMuy8rxsleLdVoan1yXhhPGfdcE5E9XsPemU0SXmJsUWb508lWi16y6BtCx4envlzxTkc7nU8DHhZoisY5WhJUfi2jWFTqiucT2EJYxHtfM2Zmx251cR7PuREKEEpKBbHghQVmNB3I; lianjia_uuid=547d3d52-a643-4087-9a67-e88845388c4a; _ga=GA1.2.1452629490.1740069522; crosSdkDT2019DeviceId=ev0z9w--hqoi59-6ao2hzdtadf7adw-iu6q0rpu7; ftkrc_=37fb9819-ebcd-42e4-b73f-085e8421596f; lfrc_=ec9ecc62-7a9d-4d46-9627-e6ca90b10b46; sensorsdata2015jssdkcross=%7B%22distinct_id%22%3A%221952439a73b3f0-08d9f9bbee6103-1d525636-1764000-1952439a73c8ce%22%2C%22%24device_id%22%3A%221952439a73b3f0-08d9f9bbee6103-1d525636-1764000-1952439a73c8ce%22%2C%22props%22%3A%7B%22%24latest_traffic_source_type%22%3A%22%E7%9B%B4%E6%8E%A5%E6%B5%81%E9%87%8F%22%2C%22%24latest_referrer%22%3A%22%22%2C%22%24latest_referrer_host%22%3A%22%22%2C%22%24latest_search_keyword%22%3A%22%E6%9C%AA%E5%8F%96%E5%88%B0%E5%80%BC_%E7%9B%B4%E6%8E%A5%E6%89%93%E5%BC%80%22%7D%7D; _ga_XGP5EDPZTV=GS1.2.1740324896.2.1.1740325531.0.0.0; _ga_XRDEC2G0T9=GS1.2.1740324896.2.1.1740325532.0.0.0; _ga_SNG6R1B3VY=GS1.2.1740324896.2.1.1740325534.0.0.0; select_city=440300; login_ucid=2000000467299247; lianjia_token=2.0012bd483944cc4e7a03106108be117f86; lianjia_token_secure=2.0012bd483944cc4e7a03106108be117f86; security_ticket=l8PXovPnkoIjz75RIkNpTx/2Iq6N/BmYmlchCXtJO/EnYp4WYcVDy4zmbzSortgzw94LuTb6FFBsOIeN0xekLu6PUsHG8fP9qIo0hyI4PkbdwxdeGWtREUjhY0YdmwiL4uI2pVHQGr+qt1mOLbytF0EE1A3F1VAqRvnuBjKiclo=; _jzqckmp=1; _gid=GA1.2.1275099360.1740998238; _jzqx=1.1740998231.1741001952.2.jzqsr=clogin%2Elianjia%2Ecom|jzqct=/.jzqsr=sz%2Elianjia%2Ecom|jzqct=/chengjiao/105116305030%2Ehtml; lianjia_ssid=a07c43e1-bd6c-feb3-77bd-c662b8c278d2; Hm_lvt_46bf127ac9b856df503ec2dbf942b67e=1740325246,1741012099; HMACCOUNT=F26A4887B55DF921; _qzjc=1; _jzqa=1.493861098530465800.1740325246.1741001952.1741012100.4; _jzqc=1; _jzqb=1.6.10.1741012100.1; _qzja=1.1760960081.1740325246456.1741001952445.1741012100239.1741013635888.1741013852534.0.0.0.14.4; _qzjb=1.1741012100239.6.0.0.0; _qzjto=12.3.0; srcid=eyJ0Ijoie1wiZGF0YVwiOlwiZDZlZTBmMTc2MDBkYjBmMmQ4ZWNlYzRhNGNkM2VhMGEyNjM3YTg1ZDI1NTkwYzM2MzNiYzMyNWY4MjE3YjhhZTAyNzRhYTk2MGMxZDYwNjJmZmM0ZmEwYThhYzhiNGQyM2QzYzkzM2Q5NjE1NTY4ZWI3ZDczZDJjMmMxMDM2NWEyNTU1NTQyYmY4MGY5ZjczMDczODFhZDRkYTU2MjdhN2RkMTE2MDczYzAzYmUzN2VlNGE4NTQ2NmU2NThlZWUwOTY1NmFjNjlhYmRkYjE3MTQyZTY5OWZkYTkwZGJkYTI3NmI0NDFlOWNkYzE5OTY4YjhmMzA0ZDg0ZmM1MzNjN1wiLFwia2V5X2lkXCI6XCIxXCIsXCJzaWduXCI6XCIxYTM3OWQwYVwifSIsInIiOiJodHRwczovL3N6LmxpYW5qaWEuY29tL2NoZW5namlhby8xMDUxMTk1NTQ4NDYuaHRtbCIsIm9zIjoid2ViIiwidiI6IjAuMSJ9; Hm_lpvt_46bf127ac9b856df503ec2dbf942b67e=1741013857; _ga_C4R21H79WC=GS1.2.1741012115.4.1.1741013869.0.0.0'
# 结果储存位置
OUT_DIR = './output'


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
            title_div = house.find('div', class_='title')
            title = title_div.text.strip()
            link = title_div.find('a').get('href')
            id = parse_house_id(link)
            dealDate = house.find("div", class_="dealDate").text.strip()
            # TODO:把上面所有的变量都按字段顺序放进来
            row = [id, title, dealDate, link] 
            #########################################################
            data.append(row)
        except Exception as e:
            print(f"爬取 {title} 失败，错误：{e}")
    return data


"""保存文件到csv"""
def save_as_csv(data:List[List[str]], columns:List[str], file_name:str) -> None:
    df = pd.DataFrame(data, columns=columns)
    file_path = f'{OUT_DIR}/{file_name}.csv'
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
    house_info = get_chengjiao_info_by_page(1, 5)
    # TODO: 把字段对应的表头顺序一一对应补充到这里
    info_columns = ['id', '标题', '成交日期', '链接']
    save_as_csv(house_info, info_columns, '成交列表信息_P1-P5')