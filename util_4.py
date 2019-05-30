import mitmproxy.http
from mitmproxy import ctx
import json
import datetime
import calendar

class Rush(object):
    def __init__(self):
        self.different = datetime.timedelta(seconds=2)
        now = datetime.datetime.now()
        if now.hour < 10:
            self.start_time = datetime.datetime(2019, now.month, now.day, 10, 0, 0)
        elif now.hour > 11 and now.hour < 14:
            self.start_time = datetime.datetime(2019, now.month, now.day, 14, 0, 0)
        else:
            self.start_time = now
        print("初始化误差:{}".format(self.different))
        print("初始化抢购时间:{}".format(self.start_time))


    def request(self, flow:mitmproxy.http.HTTPFlow):

        if flow.request.path == "/fyx/web/order/rushToBuy":
            start = self.start_time + self.different
            now = datetime.datetime.now()
            while now < start:
                now = datetime.datetime.now()

    def response(self, flow:mitmproxy.http.HTTPFlow):
        # date = "Wed, 29 May 2019 02:01:11 GMT"
        # timestamp = round(datetime.datetime(2019,5,29,10,1,11).timestamp())

        if flow.request.host == "ei.cnzz.com" or flow.request.host == "z2.cnzz.com":
            local_time = datetime.datetime.now()
            current_time = flow.response.headers["date"].split(" ")
            current_date = current_time[1]
            current_month = current_time[2]
            current_month = list(calendar.month_abbr).index(current_month)
            current_year = current_time[3]
            current_clock = current_time[4]
            current_hour, current_minute, current_second = current_clock.split(":")
            server_time = datetime.datetime(int(current_year),int(current_month),int(current_date),int(current_hour),int(current_minute),int(current_second)) + datetime.timedelta(hours=8)
            if self.different > (local_time - server_time):
                self.different = local_time - server_time
                print("当前误差:{}".format(self.different))

        if flow.request.path == "/fyx/web/order/checkActivity":
            text = flow.response.get_text()
            text_dict = json.loads(text)
            text_dict["data"]["code"] = "0"
            flow.response.set_text(json.dumps(text_dict))

addons = [
    Rush()
]
