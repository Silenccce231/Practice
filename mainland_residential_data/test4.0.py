import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
from typing import List
import re

# 链家基础地址
BASE_URL = 'https://sz.lianjia.com/chengjiao/'
# 登录后从浏览器接口中获取
COOKIE = 'lianjia_uuid=547d3d52-a643-4087-9a67-e88845388c4a; _ga=GA1.2.1452629490.1740069522; crosSdkDT2019DeviceId=ev0z9w--hqoi59-6ao2hzdtadf7adw-iu6q0rpu7; ftkrc_=37fb9819-ebcd-42e4-b73f-085e8421596f; lfrc_=ec9ecc62-7a9d-4d46-9627-e6ca90b10b46; sensorsdata2015jssdkcross=%7B%22distinct_id%22%3A%221952439a73b3f0-08d9f9bbee6103-1d525636-1764000-1952439a73c8ce%22%2C%22%24device_id%22%3A%221952439a73b3f0-08d9f9bbee6103-1d525636-1764000-1952439a73c8ce%22%2C%22props%22%3A%7B%22%24latest_traffic_source_type%22%3A%22%E7%9B%B4%E6%8E%A5%E6%B5%81%E9%87%8F%22%2C%22%24latest_referrer%22%3A%22%22%2C%22%24latest_referrer_host%22%3A%22%22%2C%22%24latest_search_keyword%22%3A%22%E6%9C%AA%E5%8F%96%E5%88%B0%E5%80%BC_%E7%9B%B4%E6%8E%A5%E6%89%93%E5%BC%80%22%7D%7D; Hm_lvt_46bf127ac9b856df503ec2dbf942b67e=1740325246,1741012099; HMACCOUNT=F26A4887B55DF921; _jzqc=1; _ga_XRDEC2G0T9=GS1.2.1742294321.3.1.1742294465.0.0.0; _ga_XGP5EDPZTV=GS1.2.1742294321.3.1.1742294465.0.0.0; _ga_SNG6R1B3VY=GS1.2.1742294321.3.1.1742294465.0.0.0; select_city=440300; session_id=e97ae020-9b84-ef33-aec5-b973cd4408c0; beikeBaseData=%7B%22parentSceneId%22%3A%22452182030296064513%22%7D; jiaxin_token=2.001213e13c4462e77f03bec80d61b28ca3; _jzqckmp=1; _gid=GA1.2.1275773507.1742398916; lianjia_ssid=d5858f16-406d-4304-ad5b-73289c2e5a9b; hip=P1pfALPfLUYg9Opl00x1vVlZjbeprkxevhGKJrfqAW8ld33H9c4rzPtPUCTtRxDPrsADB3f9LJY9ng8EZ6VtEbafmU8RF_CtGvY2ekr_y6zceFKf4ASEABS9zPfAXN7mk9ta83xgmKzpKfB0PXWwQoJVX29L2kwMQJSM6zgvhQ3e163bq11QdmPoRw%3D%3D; _jzqa=1.493861098530465800.1740325246.1742398906.1742440410.6; _jzqx=1.1740998231.1742440410.3.jzqsr=clogin%2Elianjia%2Ecom|jzqct=/.jzqsr=hip%2Elianjia%2Ecom|jzqct=/; Hm_lvt_efa595b768cc9dc7d7f9823368e795f1=1742441193; Hm_lpvt_efa595b768cc9dc7d7f9823368e795f1=1742441193; _gat=1; _gat_dianpu_agent=1; login_ucid=2000000467299247; lianjia_token=2.00129dd7d244ecd1910330fee3b9ffdcff; lianjia_token_secure=2.00129dd7d244ecd1910330fee3b9ffdcff; security_ticket=Epyo0M7wblYt/l9GVNMdwcJIGAQ+sKjAstVsgdOT4lJO2u6Gcq34ELChNi+H5y1Q991VII9kCaMMcAzWnm1E2P0vjoGSEJWfFQU/tlklAT/jeK7zwLHcsm4TuqX2vETyGtSPBt/R1Ss/25xHwfZbIiXbKwf44JEtpVEG2VZ2D4s=; Hm_lpvt_46bf127ac9b856df503ec2dbf942b67e=1742441267; _jzqb=1.7.10.1742440410.1; _gat_global=1; _gat_new_global=1; _ga_C4R21H79WC=GS1.2.1742440422.6.1.1742441273.0.0.0'
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
                base_data[kitchen_idx] = f"{kitchen}"
                base_data[bathroom_idx] = f"{bathroom}"

            # 处理户梯比特殊字段
            def chinese_to_num(chinese_str):
                num_map = {'零': 0, '一': 1, '二': 2, '两': 2, '三': 3,
                           '四': 4, '五': 5, '六': 6, '七': 7, '八': 8, '九': 9, '十': 10}
                temp = 0

                for char in chinese_str:
                    val = num_map.get(char, 0)
                    # 处理十的特殊情况
                    if char == '十':
                        # 当十出现在开头(如"十二")，或前无累计值时视为10
                        if temp == 0:
                            temp = 10
                        # 当十出现在中间(如"二十")，前值乘以10
                        else:
                            temp = temp * 10
                    else:
                        temp += val

                  # 处理纯"十"结尾的情况（如"二十"）
                if '十' in chinese_str and temp < 10:
                    temp *= 10
                return temp

            if name == '梯户比例':
                # match = re.search(r'(\d+)梯(\d+)户', value)
                # if match:
                #     elevators = int(match.group(1))
                #     households = int(match.group(2))
                match = re.search(
                    r'([零一二两三四五六七八九十]+)梯([零一二两三四五六七八九十]+)户', value)
                if match:
                    elevators = chinese_to_num(match.group(1))
                    households = chinese_to_num(match.group(2))
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
    # print(house_details)
    detail_columns = ['调价（次）', '带看（次）',
                      '关注（人）', '浏览（次）', '房屋户型', '房屋朝向', '建成年代', '装修情况', '梯户比例', '配备电梯', '建筑类型', '建筑结构', '厨房数目', '卫生间数目', '户梯比']
    save_as_csv([house_details], detail_columns, '成交房屋详情_P1')
