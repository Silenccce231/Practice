import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
import re

# 设置请求头，模拟浏览器访问
headers = {
    "Cookie": "SECKEY_ABVK=PneWGxjnQ5vUuABNY0tjhvL+HebNvQt0P7XMHFz4ZVk%3D; BMAP_SECKEY=PneWGxjnQ5vUuABNY0tjhoBncaUz4KhJ4qvr7ocpkU3su1vPYfAfiuVMuy8rxsleLdVoan1yXhhPGfdcE5E9XsPemU0SXmJsUWb508lWi16y6BtCx4envlzxTkc7nU8DHhZoisY5WhJUfi2jWFTqiucT2EJYxHtfM2Zmx251cR7PuREKEEpKBbHghQVmNB3I; lianjia_uuid=547d3d52-a643-4087-9a67-e88845388c4a; _ga=GA1.2.1452629490.1740069522; crosSdkDT2019DeviceId=ev0z9w--hqoi59-6ao2hzdtadf7adw-iu6q0rpu7; ftkrc_=37fb9819-ebcd-42e4-b73f-085e8421596f; lfrc_=ec9ecc62-7a9d-4d46-9627-e6ca90b10b46; sensorsdata2015jssdkcross=%7B%22distinct_id%22%3A%221952439a73b3f0-08d9f9bbee6103-1d525636-1764000-1952439a73c8ce%22%2C%22%24device_id%22%3A%221952439a73b3f0-08d9f9bbee6103-1d525636-1764000-1952439a73c8ce%22%2C%22props%22%3A%7B%22%24latest_traffic_source_type%22%3A%22%E7%9B%B4%E6%8E%A5%E6%B5%81%E9%87%8F%22%2C%22%24latest_referrer%22%3A%22%22%2C%22%24latest_referrer_host%22%3A%22%22%2C%22%24latest_search_keyword%22%3A%22%E6%9C%AA%E5%8F%96%E5%88%B0%E5%80%BC_%E7%9B%B4%E6%8E%A5%E6%89%93%E5%BC%80%22%7D%7D; _ga_XGP5EDPZTV=GS1.2.1740324896.2.1.1740325531.0.0.0; _ga_XRDEC2G0T9=GS1.2.1740324896.2.1.1740325532.0.0.0; _ga_SNG6R1B3VY=GS1.2.1740324896.2.1.1740325534.0.0.0; select_city=440300; login_ucid=2000000467299247; lianjia_token=2.0012bd483944cc4e7a03106108be117f86; lianjia_token_secure=2.0012bd483944cc4e7a03106108be117f86; security_ticket=l8PXovPnkoIjz75RIkNpTx/2Iq6N/BmYmlchCXtJO/EnYp4WYcVDy4zmbzSortgzw94LuTb6FFBsOIeN0xekLu6PUsHG8fP9qIo0hyI4PkbdwxdeGWtREUjhY0YdmwiL4uI2pVHQGr+qt1mOLbytF0EE1A3F1VAqRvnuBjKiclo=; _jzqckmp=1; _gid=GA1.2.1275099360.1740998238; _jzqx=1.1740998231.1741001952.2.jzqsr=clogin%2Elianjia%2Ecom|jzqct=/.jzqsr=sz%2Elianjia%2Ecom|jzqct=/chengjiao/105116305030%2Ehtml; lianjia_ssid=a07c43e1-bd6c-feb3-77bd-c662b8c278d2; Hm_lvt_46bf127ac9b856df503ec2dbf942b67e=1740325246,1741012099; HMACCOUNT=F26A4887B55DF921; _qzjc=1; _jzqa=1.493861098530465800.1740325246.1741001952.1741012100.4; _jzqc=1; _jzqb=1.6.10.1741012100.1; _qzja=1.1760960081.1740325246456.1741001952445.1741012100239.1741013635888.1741013852534.0.0.0.14.4; _qzjb=1.1741012100239.6.0.0.0; _qzjto=12.3.0; srcid=eyJ0Ijoie1wiZGF0YVwiOlwiZDZlZTBmMTc2MDBkYjBmMmQ4ZWNlYzRhNGNkM2VhMGEyNjM3YTg1ZDI1NTkwYzM2MzNiYzMyNWY4MjE3YjhhZTAyNzRhYTk2MGMxZDYwNjJmZmM0ZmEwYThhYzhiNGQyM2QzYzkzM2Q5NjE1NTY4ZWI3ZDczZDJjMmMxMDM2NWEyNTU1NTQyYmY4MGY5ZjczMDczODFhZDRkYTU2MjdhN2RkMTE2MDczYzAzYmUzN2VlNGE4NTQ2NmU2NThlZWUwOTY1NmFjNjlhYmRkYjE3MTQyZTY5OWZkYTkwZGJkYTI3NmI0NDFlOWNkYzE5OTY4YjhmMzA0ZDg0ZmM1MzNjN1wiLFwia2V5X2lkXCI6XCIxXCIsXCJzaWduXCI6XCIxYTM3OWQwYVwifSIsInIiOiJodHRwczovL3N6LmxpYW5qaWEuY29tL2NoZW5namlhby8xMDUxMTk1NTQ4NDYuaHRtbCIsIm9zIjoid2ViIiwidiI6IjAuMSJ9; Hm_lpvt_46bf127ac9b856df503ec2dbf942b67e=1741013857; _ga_C4R21H79WC=GS1.2.1741012115.4.1.1741013869.0.0.0",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36"
}

# response = requests.get("https://sz.lianjia.com/chengjiao/", headers=headers)

# 存储数据
data_list = []

base_url = "https://sz.lianjia.com/chengjiao"

# 爬取前 5 页数据
for page in range(1, 2):
    url = ""
    if page == 1:
        url = base_url
    else:
        url = f"{base_url}/pg{page}/"
    print(f"正在爬取：{url}")

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"页面请求失败，状态码：{response.status_code}")
        break

    soup = BeautifulSoup(response.text, "html.parser")
    house_list = soup.find_all('div', class_='info')

#     html = """
# <li><a class="img" href="https://sz.lianjia.com/chengjiao/105119554846.html" target="_blank"><img class="lj-lazy" src="https://s1.ljcdn.com/feroot/pc/asset/img/new-version/default_block.png?_v=20250224152124" data-original="https://image1.ljcdn.com/x-se/hdic-frame/standard_771267ca-65f0-4c75-b908-d648d15795f6.png.280x210.jpg" alt="友邻公寓 1室0厅 30平米-深圳友邻公寓二手房成交"></a><div class="info"><div class="title"><a href="https://sz.lianjia.com/chengjiao/105119554846.html" target="_blank">友邻公寓 1室0厅 30平米</a></div><div class="address"><div class="houseInfo"><span class="houseIcon"></span>北 | 简装</div><div class="dealDate">2025.01.31</div><div class="totalPrice"><span class='number'>182</span>万</div></div><div class="flood"><div class="positionInfo"><span class="positionIcon"></span>低楼层(共30层) 2006年板塔结合</div><div class="source"></div><div class="unitPrice"><span class="number">60667</span>元/平</div></div><div class="dealHouseInfo"><span class="dealHouseIcon"></span><span class="dealHouseTxt"><span>近地铁</span></span></div><div class="dealCycleeInfo"><span class="dealCycleIcon"></span><span class="dealCycleTxt"><span>挂牌200万</span><span>成交周期6天</span></span></div><div class="agentInfoList"><span class="agentIcon"></span><a href="https://dianpu.lianjia.com/1000000030994672/" class="agent_name">雷红枝</a><div class="agent_chat_btn im-talk LOGCLICKDATA" data-lj_evtid="12952" data-lj_action_event="WebClick" data-lj_action_pid="lianjiaweb" data-lj_action_house_code="105119554846" data-lj_action_agent_name="雷红枝" data-lj_action_agent_id="1000000030994672" data-lj_action_source_type="pc_chengjiao_liebiao" data_lj_action_e_plan='{"u":1000000030994672,"v":"V1","s":"NATURAL","adId":100000169,"flow":"natural","b":"HouseSoldAgentBuilder","p":"","g":"","sid":"1000000030994672_2411063310043","rid":"7586319236680381185"}' data-ucid="1000000030994672" data-source-extends={ "house_code": "105119554846"} data-msg-payload="Hi，您好，我正在看友邻公寓小区已成交的二手房：友邻公寓 1室0厅 30平米" data-source-port="pc_lianjia_ershou_chachengjiao_liebiao"><i class="chatIcon"></i><span>免费咨询</span></div></div></div></li><li><a class="img" href="https://sz.lianjia.com/chengjiao/105119531835.html" target="_blank"><img class="lj-lazy" src="https://s1.ljcdn.com/feroot/pc/asset/img/new-version/default_block.png?_v=20250224152124" data-original="https://image1.ljcdn.com/x-se/hdic-frame/standard_24fa7ef9-3e8a-4a79-b5f5-8724f933853a.png.280x210.jpg" alt="桃源村一期 3室2厅 71.44平米-深圳桃源村一期二手房成交"></a><div class="info"><div class="title"><a href="https://sz.lianjia.com/chengjiao/105119531835.html" target="_blank">桃源村一期 3室2厅 71.44平米</a></div><div class="address"><div class="houseInfo"><span class="houseIcon"></span>北 | 简装</div><div class="dealDate">2025.01.31</div><div class="totalPrice"><span class='number'>353</span>万</div></div><div class="flood"><div class="positionInfo"><span class="positionIcon"></span>中楼层(共7层) 1997年板楼</div><div class="source"></div><div class="unitPrice"><span class="number">49413</span>元/平</div></div><div class="dealHouseInfo"><span class="dealHouseIcon"></span><span class="dealHouseTxt"><span>房屋满五年</span><span>近地铁</span></span></div><div class="dealCycleeInfo"><span class="dealCycleIcon"></span><span class="dealCycleTxt"><span>挂牌388万</span><span>成交周期12天</span></span></div><div class="agentInfoList"><span class="agentIcon"></span><a href="https://dianpu.lianjia.com/1000000020336940/" class="agent_name">马伟松</a><div class="agent_chat_btn im-talk LOGCLICKDATA" data-lj_evtid="12952" data-lj_action_event="WebClick" data-lj_action_pid="lianjiaweb" data-lj_action_house_code="105119531835" data-lj_action_agent_name="马伟松" data-lj_action_agent_id="1000000020336940" data-lj_action_source_type="pc_chengjiao_liebiao" data_lj_action_e_plan='{"u":1000000020336940,"v":"V1","s":"NATURAL","adId":100000169,"flow":"natural","b":"HouseSoldAgentBuilder","p":"","g":"","sid":"1000000020336940_2411051982787","rid":"7586319236697158400"}' data-ucid="1000000020336940" data-source-extends={ "house_code": "105119531835"} data-msg-payload="Hi，您好，我正在看桃源村一期小区已成交的二手房：桃源村一期 3室2厅 71.44平米" data-source-port="pc_lianjia_ershou_chachengjiao_liebiao"><i class="chatIcon"></i><span>免费咨询</span></div></div></div></li>
#         """
#     soup_test = BeautifulSoup(html, 'html.parser')
#     house_list = soup_test.find_all('div', class_='info')

    for house in house_list:
        row = []
        try:
            # 标题
            title = house.find("div", class_="title").text.strip()
            row.append(title)
            data_list.append(row)
        except Exception as e:
            print(f"爬取 {title} 失败，错误：{e}")

# 存储数据到 CSV
df = pd.DataFrame(data_list, columns=[
    "标题"
])

df.to_csv("shenzhen_lianjia_chengjiao.csv", index=False, encoding="utf-8-sig")
print("爬取完成，数据已保存到 shenzhen_lianjia_chengjiao.csv")
