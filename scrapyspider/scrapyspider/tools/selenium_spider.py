from selenium import webdriver

browser = webdriver.Chrome(executable_path="/home/chandler/github/Spider/chromedriver")
browser.get("http://sh.lianjia.com/zufang/shz4064502.html")

print(browser.page_source)
browser.quit()

