import requests
from scrapy import Selector

base_url = "http://www.feidieshuo.com/media/play/"
index = 3050


def first(url):
    response = requests.get(url)
    if response.status_code == 200:
        print("ok status code is %s" % response.status_code)
        resource = response.text
        ll = Selector(text=resource).css(".notfound").extract()
        if len(ll) > 0:
            return True
        return False


if __name__ == "__main__":
    while True:
        if not first(base_url + str(index)):
            print(index)
            break
        index += 1

