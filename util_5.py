import mitmproxy.http
from mitmproxy import ctx
import json
import datetime
import calendar
import queue
import threading
import requests

class Rush(object):
    def __init__(self):
        now = datetime.datetime.now()
        if now.hour < 10:
            self.start_time = datetime.datetime(2019, now.month, now.day, 10, 0, 0)
        elif now.hour >= 11 and now.hour < 14:
            self.start_time = datetime.datetime(2019, now.month, now.day, 14, 0, 0)
        else:
            self.start_time = now
        print("初始化抢购时间:{}".format(self.start_time))
        self.Q = queue.LifoQueue(maxsize=0)
        different_time = datetime.timedelta(seconds=1000)
        self.Q.put(different_time.total_seconds())
        P = threading.Thread(target=self.min_different, args=(self.Q,))
        P.start()

    def different(self):
        url = "https://ei.cnzz.com/stat.htm"
        response = requests.get(url)
        local_time = datetime.datetime.now()
        current_time = response.headers["date"].split(" ")
        current_date = current_time[1]
        current_month = current_time[2]
        current_month = list(calendar.month_abbr).index(current_month)
        current_year = current_time[3]
        current_clock = current_time[4]
        current_hour, current_minute, current_second = current_clock.split(":")
        server_time = datetime.datetime(int(current_year), int(current_month), int(current_date), int(current_hour),
                                        int(current_minute), int(current_second)) + datetime.timedelta(hours=8)
        different = (local_time - server_time).total_seconds()
        return different

    def min_different(self,Q):
        count = 0
        while True:
            if Q.empty():
                print("-" * 50)
                print("结束时间校准")
                print("-" * 50)
                break
            diff_time = self.different()
            min_time = Q.get()
            if diff_time < min_time:
                Q.put(diff_time)
                print("-" * 50)
                print("当前最小误差为：{}".format(diff_time))
                print("-" * 50)
            else:
                Q.put(min_time)
            count += 1
            print("第{}次时间校准".format(count))

    def request(self, flow:mitmproxy.http.HTTPFlow):

        if flow.request.path == "/fyx/web/order/rushToBuy":
            diff_time = self.Q.get()
            start = self.start_time + datetime.timedelta(seconds=diff_time) - datetime.timedelta(seconds=1.6)
            print("-" * 50)
            print("开始抢购时间：{}".format(start))
            print("-" * 50)
            now = datetime.datetime.now()
            while now < start:
                now = datetime.datetime.now()
            T = threading.Thread(target=self.rush,args=(flow.request.headers,flow.request.text,))
            T.start()
            T.join()

    def rush(self,curr_headers,content):
        url = "https://www.adstech-x.com/fyx/web/order/rushToBuy"
        parms = content.split("&")
        type = parms[0].split("=")[1]
        data = parms[1].split("=")[1]
        NECaptchaValidate = parms[2].split("=")[1]
        headers = {
            "content-type":"application/x-www-form-urlencoded",
            "accept":"application/json, text/plain, */*",
            "accept-language":"zh-cn",
            "token":curr_headers["token"],
            "accept-encoding":"br, gzip, deflate",
            "origin":"https://www.adstech-x.com",
            "referer":"https://www.adstech-x.com/snapup",
            "user-agent":curr_headers['user-agent'],
            "cookie":curr_headers["cookie"]
        }
        datas = {
            "type":type,
            "data":data,
            "NECaptchaValidate":NECaptchaValidate
        }
        while True:
            print("当前时间：{}".format(datetime.datetime.now()))
            response = requests.post(url, headers=headers,data=datas)
            dict = json.loads(response.content.decode())
            print(dict)
            ret_code = dict["data"]["code"]
            token = dict["data"]["token"]
            if str(ret_code) == "0" or str(ret_code) == "-3" or str(ret_code) == "-2" or str(ret_code) == "92":
                break
            else:
                headers.update({"token": token})


    def response(self, flow:mitmproxy.http.HTTPFlow):
        if flow.request.path == "/fyx/web/order/checkActivity":
            text = flow.response.get_text()
            text_dict = json.loads(text)
            text_dict["data"]["code"] = "0"
            flow.response.set_text(json.dumps(text_dict))

addons = [
    Rush()
]
