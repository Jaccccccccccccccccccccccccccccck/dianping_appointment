from selenium import webdriver
import requests,logging
import time,re
from selenium.webdriver.support.wait import WebDriverWait
from datetime import datetime


# 大众点评项目名称160
def get_token_by_login_yima(username,password):
    response = requests.get(url='http://api.fxhyd.cn/UserInterface.aspx?action=login&username={username}&password={password}'.format(username=username,password=password))
    if 'success' in response.text:
        status, token = response.text.split('|')
        return token
    else:
        print('Error getting token by login')
        return None


def get_base_info(token):
    response = requests.get(url = 'http://api.fxhyd.cn/UserInterface.aspx?action=getaccountinfo&token={token}'.format(token=token))
    if 'success' in response.text:
        status,username,account_status,account_level,account_balance,account_freezing_balance,account_discount,account_get_phone_max_limit = response.text.split('|')
        return username,account_status,account_level,account_balance,account_freezing_balance,account_discount,account_get_phone_max_limit
    else:
        print('获取用户基本信息出错！')
        return None


def get_phone_num(token):
    response = requests.get(url='http://api.fxhyd.cn/UserInterface.aspx?action=getmobile&token={token}&itemid=160&excludeno='.format(token=token))
    if 'success' in response.text:
        status, phone_num = response.text.split('|')
        return phone_num
    else:
        print('Error getting phone')
        return None


def get_phone_text(token,phone_num,retry_time_zone):
    '''
    http://api.fxhyd.cn/UserInterface.aspx?action=getsms&token=TOKEN&itemid=项目编号&mobile=手机号码&release=1
    收到短信：success|短信内容
    短信尚未到达：3001，应继续调用取短信接口，直到超时为止。
    请求失败：错误代码，请根据不同错误代码进行不同的处理。
    '''
    def get_phone_text(token, phone_num):
        response = requests.get(
            url='http://api.fxhyd.cn/UserInterface.aspx?action=getsms&token={token}&itemid=160&mobile={phone_num}'.format(
                token=token, phone_num=phone_num))
        print('获取验证码中···')
        return response.text
    start_time = datetime.now()
    while True:
        end_time = datetime.now()
        if (end_time - start_time).total_seconds() > retry_time_zone:
            print('验证码超时！%s秒'% (str(retry_time_zone)))
            return None
        time.sleep(3)
        response_text = get_phone_text(token,phone_num)
        if '3001' in response_text:
            print('验证码未接受到！')
            continue
        else:
            status, text = response_text.split('|')
            identifying_code = re.sub('\D','',text)
            print('验证码获取成功，验证码：%s'%(identifying_code))
            break

    return identifying_code


def reg(token,phone_num,url_list):
    browser=webdriver.Chrome()
    # 点评注册主页
    reg_url = 'https://www.dianping.com/reg'
    browser.get(reg_url)
    WebDriverWait(browser, 15).until(lambda x: x.find_element_by_xpath('//*[@id="easy-login-container"]/div/iframe'))
    # browser.switch_to.frame(src ='https://www.dianping.com/account/iframeRegister?callback=EasyLogin_frame_callback0&wide=false&protocol=https:&redir=https%3A%2F%2Fwww.dianping.com')
    browser.switch_to.frame(browser.find_element_by_xpath('//*[@id="easy-login-container"]/div/iframe'))
    time.sleep(1)
    browser.find_element_by_id('mobile-number-textbox').send_keys(phone_num)
    browser.find_element_by_id('send-number-button').click()
    time.sleep(3)
    alert_text = browser.find_element_by_class_name('alert-content').text
    if "动态码已发送，请查看手机" in alert_text:
        browser.find_element_by_id('password-textbox').send_keys('zidonghuazhucE!1')
        browser.find_element_by_id('agreePolicy').click()
        # 点击注册用户
        while True:

            identifying_code = get_phone_text(token,phone_num,65)
            if identifying_code:
                break
            browser.find_element_by_id('send-number-button').click()

        browser.find_element_by_id('number-textbox').send_keys(identifying_code)
        browser.find_element_by_id('register-button').click()
        print('号码：%s，注册成功！'%(phone_num))
        time.sleep(1)
        appointment(browser,url_list)
    else:
        print('号码：%s，已经被注册！'%(phone_num))
        login_and_appointment(token,phone_num,url_list)
    browser.close()


def login_and_appointment(token,phone_num,url_list):
    print('手机验证码登陆中···')
    browser = webdriver.Chrome()
    # 点评注册主页
    login_url = 'https://account.dianping.com/login'
    browser.get(login_url)

    # browser.switch_to.frame(src ='https://www.dianping.com/account/iframeRegister?callback=EasyLogin_frame_callback0&wide=false&protocol=https:&redir=https%3A%2F%2Fwww.dianping.com')
    browser.switch_to.frame(browser.find_element_by_xpath('//*[@id="J_login_container"]/div/iframe'))
    browser.find_element_by_class_name('bottom-password-login').click()
    browser.find_element_by_id('mobile-number-textbox').send_keys(phone_num)
    while True:
        browser.find_element_by_id('send-number-button').click()
        identifying_code = get_phone_text(token,phone_num,65)
        if identifying_code:
            break
    browser.find_element_by_id('number-textbox').send_keys(identifying_code)
    browser.find_element_by_id('login-button-mobile').click()
    time.sleep(4)
    appointment(browser,url_list)
    browser.close()


def appointment(browser, url_list):
    for url in url_list:
        print('预约中：%s' % url)
        browser.get(url)
        time.sleep(5)
        browser.find_element_by_css_selector('.btn.J-rs-btn').click()
        time.sleep(3)
        browser.find_element_by_css_selector('.medi-btn.stress-btn.J_btnSubmit').click()
        time.sleep(2)
        browser.find_element_by_css_selector('.medi-btn.stress-btn.J_btnCancel').click()
        print('预约成功：%s'% url)


def full_func():
    token = get_token_by_login_yima('','')
    print('获取登陆token :%s' % token)
    phone_num = get_phone_num(token)
    print('获取手机号码:%s' % phone_num)
    url_list =['http://www.dianping.com/shop/23123189']
    reg(token,phone_num,url_list)


