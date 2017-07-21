import time
from selenium import webdriver
from scrapy import Selector

# browser = webdriver.Chrome(executable_path="/home/chandler/github/Spider/chromedriver")
# browser.get("https://www.zhihu.com/#signin")
#
# browser.find_element_by_css_selector(".view-signin input[name='account']").send_keys("13770955080")
# browser.find_element_by_css_selector(".view-signin input[name='password']").send_keys("iloveyou1314")
#
# browser.find_element_by_css_selector(".view-signin button.sign-button").click()

#selenium 完成微博模拟登陆
# browser.get("http://www.weibo.com/")
# time.sleep(5)
# browser.find_element_by_css_selector("#loginname").send_keys("13770955080")
# browser.find_element_by_css_selector(".info_list.password input[node-type='password']").send_keys("910929xiao!@")
# browser.find_element_by_css_selector(".info_list.login_btn a[node-type='submitBtn']").click()
#自动控制鼠标滚轮下拉
# for i in range(10):
#     browser.execute_script("window.scrollTo(0, document.body.scrollHeight); "
#                            "var lenOfPage=document.body.scrollHeight; return lenOfPage")
#     time.sleep(3)

# print(browser.page_source)
# t_selector = Selector(text=browser.page_source)
#
# browser.quit()

#设置chromedriver不加载图片
chrome_opt = webdriver.ChromeOptions()
prefs = {"profile.managed_default_content_settings.images": 2}
chrome_opt.add_experimental_option("prefs", prefs)
browser = webdriver.Chrome(executable_path="/home/chandler/github/Spider/chromedriver",
                           chrome_options=chrome_opt)
browser.get("http://sh.lianjia.com/zufang/shz4064502.html")
print(browser.page_source)
# t_selector = Selector(text=browser.page_source)
browser.quit()

# phantomjs, 无界面浏览器，多进程情况下phantomjs性能会下降严重

