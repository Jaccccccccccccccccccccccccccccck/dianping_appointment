from selenium import webdriver
def reg():
    browser=webdriver.Chrome()
    # 点评注册主页
    reg_url = 'https://www.dianping.com/reg'
    browser.get(reg_url)

reg()