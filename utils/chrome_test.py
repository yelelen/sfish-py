from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import os

# display = Display(visible=False, size=(800, 600))
# display.start()
#
# browser = webdriver.Chrome(executable_path='/home/yelelen/Software/chromedriver')
# browser.get('http://www.365yg.com/group/6465272642801762830/')

# browser = webdriver.Firefox(executable_path='/home/yelelen/Software/geckodriver')
# browser.get('http://www.365yg.com/group/6465272642801762830/')
#
dcap = dict(DesiredCapabilities.PHANTOMJS)
dcap["phantomjs.page.settings.userAgent"] = (
    "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.221 Safari/537.36 SE 2.X MetaSr 1.0")  # 设置user-agent请求头
dcap["phantomjs.page.settings.loadImages"] = False  # 禁止加载图片
browser = webdriver.PhantomJS(executable_path='/home/yelelen/Software/phantomjs-2.1.1-linux-x86_64/bin/phantomjs',
                              desired_capabilities=dcap)
browser.set_page_load_timeout(20)  # 设置页面最长加载时间为40s
try:
    browser.get('http://www.bilibili.com/video/av11250249/')
except:
    pass

print(browser.page_source)
browser.quit()
