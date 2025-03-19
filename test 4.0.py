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


def get_chengjiao_detail(url: str) -> List[str]:
    soup = get_html_soup(url)
    if soup == None:
        return []
    # 返回结果为一维数组
    data = []
    try:
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
        base_labels = ['房屋户型', '房屋朝向','建成年代', '装修情况', '梯户比例', '配备电梯','建筑类型','建筑结构']
        base_data = [''] * len(base_labels)
        # 新增厨卫存储位置（追加到数据末尾）
        kitchen_idx = len(base_labels)
        bathroom_idx = kitchen_idx + 1
        base_data += ['', '']  # 扩展存储空间
        #新增户梯比字段
        ratio_idx = len(base_labels)
        base_data += [''] ``
        for li in li_tags:
            # 获得标签名
            name = li.find('span').get_text(strip=True)
            # 获得标签值
            value = li.get_text(strip=True).replace(name, '')
            # 处理房屋户型特殊字段
            if name == '房屋户型':
                # 使用正则表达式分离厨卫信息
                kitchen = re.search(r'(\d+)厨', value).group(1) 
                bathroom = re.search(r'(\d+)卫', value).group(1) 
        
                # 存储到扩展字段
                base_data[kitchen_idx] = f"{kitchen}厨"
                base_data[bathroom_idx] = f"{bathroom}卫"
            
            #处理户梯比特殊字段
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

# 程序主入口
if __name__ == "__main__":
    # 拿到所有详情url
    detail_urls = 'https://sz.lianjia.com/chengjiao/105117332004.html'
    house_details = get_chengjiao_detail(detail_urls)
    detail_columns = ['id', '调价（次）', '带看（次）',
                      '关注（人）', '浏览（次）', '房屋户型', '房屋朝向','建成年代', '装修情况', '梯户比例', '配备电梯','建筑类型','建筑结构','厨房数目','卫生间数目','户梯比']
    save_as_csv(house_details, detail_columns, '成交房屋详情_P1')