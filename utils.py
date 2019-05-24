import requests
from requests.sessions import cookiejar_from_dict
import json
import time
import datetime

DEFAULT_HEADERS = {
    "User-Agent":"Mozilla/5.0 (iPhone; CPU iPhone OS 12_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148/sa-sdk-ios/gtmcapp/3.9.0",
    "Accept":"application/json, text/plain, */*",
    "Accept-Encoding":"br, gzip, deflate",
    "Accept-Language":"zh-cn",
    "Content-Type":"application/x-www-form-urlencoded",
    "Origin":"https://www.adstech-x.com",
    "Referer":"https://www.adstech-x.com/snapup",
    "Host":"www.adstech-x.com",
    "Connection":"keep-alive",
    #"Content-Length":"22"
}
DEFAULT_COOKIES = [
    {
        "channel": "appstore",
        "iclubToken": "Name",
        "UM_distinctid": "16a8186ecd2453-020b58d39320b9-284c6904-4a574-16a8186ecd3153",
        "acw_tc": "2bf984d915569512644113268e9bf73292ba155c75e3bcaa1e78054a6b",
        "CNZZDATA1276897708":"1992542334-1556948431-%7C1558069384",
        "ARToken":"Asc+LYUCO3wgINWzpPzgFw=="
    }

]

datas = [
    {
        "userId": "",
        "userName": "",
        "phone": 00000000000
    },
    {
        "userId": "",
        "userName": "",
        "phone": 00000000000
    }
]

class Gtmc(object):
    def __init__(self,num):
        self.num = num
        self.session = requests.session()
        self.session.cookies = cookiejar_from_dict(DEFAULT_COOKIES[0])
        self.headers = DEFAULT_HEADERS
        self.tel = datas[num].get("phone",0)

    def checkLogin(self):
        url = "https://www.adstech-x.com/fyx/web/order/checkLogin"
        data = datas[self.num]
        response = self.session.post(url, headers=self.headers, data=data, verify=False)
        json_dict = json.loads(response.text)
        if str(json_dict.get("code")) != "0":
            return None
        return json_dict["data"]["token"]

    def checkActivity(self, token):
        url = "https://www.adstech-x.com/fyx/web/order/checkActivity"
        self.headers.update({"token":token})
        response = self.session.post(url, headers=self.headers, verify=False)
        return json.loads(response.text)

    def searchNotice(self, token):
        url = "https://www.adstech-x.com/fyx/web/notice/searchNotice"
        self.headers.update({"token":token})
        response = self.session.post(url, headers=self.headers, verify=False)
        return json.loads(response.text)

    def myOrder(self, token):
        url = "https://www.adstech-x.com/fyx/web/order/myOrder"
        self.headers.update({"token": token})
        response = self.session.post(url, headers=self.headers, verify=False)
        return json.loads(response.text)

    def rushToBuy(self, token, type, imageCode):
        url = "https://www.adstech-x.com/fyx/web/order/rushToBuy"
        cookie = "CNZZDATA1276897708=1864909576-1558512149-%7C1558512149; ARToken=hES2bxd6DTSiyTLkImbG2Q==; channel=appstore; iclubToken=Name; tel="+str(self.tel)+"; UM_distinctid=16adeba81c43ce-0464e1318ef54e-4f132103-5b200-16adeba81c5290; acw_tc=2bf984e815585149271947011e93d89df1a1f4e317330b7e7398850cf7"
        print(cookie)
        self.headers.update({"token": token,"Content-Length":"22","Cookie":cookie})
        data = {
            "type":type,
            "imageCode":imageCode
        }
        response = requests.post(url, headers=self.headers, data=data, verify=False)
        print(response)
        return json.loads(response.content.decode())

    def rushToBuyResult(self, token, orderId):
        url = "https://www.adstech-x.com/fyx/web/order/rushToBuyResult"
        Accept = "application/json, text/plain, */*"
        self.headers.update({"token": token,"Accept":Accept,"Content-Type":"application/x-www-form-urlencoded"})
        data = "orderId=" + str(orderId)
        response = self.session.post(url, headers=self.headers, data=data, verify=False)
        return json.loads(response.text)

    def getOrderImgCode(self, token):
        url = "https://www.adstech-x.com/fyx/web/order/getImageCode"
        params = {
            "token":token
        }
        response = requests.get(url, headers=self.headers, verify=False, params=params)
        print(response.status_code)
        if response.status_code == 200:
            with open("./imgs/orderimgcode.png","wb") as f:
                #print(response.content)
                f.write(response.content)

if __name__ == "__main__":
    user1 = Gtmc(0)
    token = user1.checkLogin()
    # print(user1.myOrder(token))
    # exit(0)
    start_time = round(datetime.datetime(2019,5,23,9,59,50).timestamp())
    now = round(time.time())
    while now < start_time:
        print("Not the time now")
        print("current time:{}".format(now))
        print("start time:{}".format(start_time))
        print("-"*50)
        now = round(time.time())
        time.sleep(1)

    user1.getOrderImgCode(token)
    code = input("请输入验证码：")
    if len(code) < 5:
        code = input("请输入验证码：")
    else:
        print(code)
    start_time = round(datetime.datetime(2019,5,23,10,00,00).timestamp())
    now = round(time.time())
    while now < start_time:
        time.sleep(0.1)
        print("sleep")
        now = round(time.time())
    while True:
        dict = user1.rushToBuy(token, 3, code)
        print(dict)
        ret_code = dict["data"]["code"]
        token = dict["data"]["token"]
        if str(ret_code) == "0" or str(ret_code) == "-3" or str(ret_code) == "-2":
            break

