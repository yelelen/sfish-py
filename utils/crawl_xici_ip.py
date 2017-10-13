import pymongo
import requests
from scrapy.selector import Selector

conn = pymongo.MongoClient(host="localhost", port=10001)
db = conn.get_database("xici_ip")
coll = db.get_collection("proxy_ip")


def craw_xici_ip():
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.101 Safari/537.36"}

    for i in range(2371):
        re = requests.get("http://www.xicidaili.com/nn/{0}".format(i + 1), headers=headers)
        selector = Selector(re)
        all_trs = selector.css("#ip_list tr ")

        ip_list = []
        for tr in all_trs[1:]:
            speed = tr.css(".bar::attr(title)").extract()[0]
            if speed:
                speed = float(speed.split("秒")[0])
            all_texts = tr.css("td::text").extract()
            ip = all_texts[0]
            port = int(all_texts[1])
            http_type = all_texts[5]
            if speed <= 0.2:
                ip_list.append((ip, http_type, port, speed))
            else:
                continue

        for ip_info in ip_list:
            ip_dict = {"ip": ip_info[0], "http_type": ip_info[1], "port": ip_info[2], "speed": ip_info[3]}
            if coll.find({"ip": ip_dict.get("ip")}).count():
                coll.replace_one({"ip": ip_dict.get("ip")}, ip_dict)
            else:
                coll.insert_one(ip_dict)
            print(ip_dict)


class GetIp(object):
    def get_ip(self):
        ips = coll.find({"speed": {"$lt": 0.2}}).limit(1)
        for ip_info in ips:
            ip = ip_info["ip"]
            http_type = ip_info.get("http_type")
            port = ip_info.get("port")
            if self.test_ip(ip, port, http_type):
                proxy_url = http_type.lower() + "://" + ip + ":" + str(port)
                return proxy_url
            else:
                return self.get_ip()

    def test_ip(self, ip, port, http_type):
        dest_url = "http://www.baidu.com"
        proxy_url = http_type.lower() + "://" + str(ip) + ":" + str(port)
        proxy_dict = {"http": proxy_url, "https": proxy_url}

        try:
            response = requests.get(dest_url, proxies=proxy_dict, timeout=6)
        except Exception as e:
            print("bad ip address")
            self.delete_ip(ip)
            return False
        else:
            code = response.status_code
            if 200 <= code < 300:
                print("effective ip")
                return True
            else:
                print("bad ip address")
                self.delete_ip(ip)
                return False

    def delete_ip(self, ip):
        coll.delete_one({"ip": ip})

if __name__ == "__main__":
    # r = GetIp().get_ip()
    # print(r)
    craw_xici_ip()