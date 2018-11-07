import re
import time
import tkinter as tk
from datetime import datetime
from tkinter import scrolledtext

import requests
import validators
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait


class appointmentApp():
    def __init__(self):

        self.token = None
        root = tk.Tk()
        root.title('大众点评自动预约')
        # width x height + x_offset + y_offset:
        root.geometry("1200x900+30+30")

        tk.Label(root, text='易码账号:').grid(row=0, column=0)
        tk.Label(root, text='易码密码:').grid(row=0, column=2)
        self.entry_username = tk.Entry(root)
        self.entry_password = tk.Entry(root)
        self.entry_username.grid(row=0, column=1)
        self.entry_password.grid(row=0, column=3)
        self.entry_username.insert(0, 'user')
        self.entry_password.insert(0, 'password')
        tk.Label(root, text='登陆状态:').grid(row=1, column=0)

        self.button_login = tk.Button(root, text='登陆')
        self.button_login.grid(row=0, column=5)

        self.label_login_status = tk.Label(root, text='未登录')
        self.label_login_status.grid(row=1, column=1, columnspan=3)

        self.button_get_base_info = tk.Button(root, text='刷新用户信息')
        self.button_get_base_info.grid(row=1, column=5)

        tk.Label(root, text='用户名:').grid(row=2, column=0)
        self.label_username = tk.Label(root)
        self.label_username.grid(row=2, column=1)
        tk.Label(root, text='账户状态:').grid(row=3, column=0)
        self.label_account_status = tk.Label(root)
        self.label_account_status.grid(row=3, column=1)
        tk.Label(root, text='账户等级:').grid(row=4, column=0)
        self.label_account_level = tk.Label(root)
        self.label_account_level.grid(row=4, column=1)
        tk.Label(root, text='账户余额:').grid(row=5, column=0)
        self.label_account_balance = tk.Label(root)
        self.label_account_balance.grid(row=5, column=1)
        tk.Label(root, text='冻结金额:').grid(row=6, column=0)
        self.label_account_freezing_balance = tk.Label(root)
        self.label_account_freezing_balance.grid(row=6, column=1)
        tk.Label(root, text='账户折扣:').grid(row=7, column=0)
        self.label_account_discount = tk.Label(root)
        self.label_account_discount.grid(row=7, column=1)
        tk.Label(root, text='获取手机号最大量:').grid(row=8, column=0)
        self.label_account_get_phone_max_limit = tk.Label(root)
        self.label_account_get_phone_max_limit.grid(row=8, column=1)

        tk.Label(root, text='获取手机号数量（数字）:').grid(row=10, column=0)
        self.entry_get_phone_num_count = tk.Entry(root)
        self.entry_get_phone_num_count.grid(row=10, column=1)
        self.entry_get_phone_num_count.insert(0, '1')

        tk.Label(root, text='店铺网址（多个网址多行输入）:').grid(row=10, column=2)
        self.text_shop_list = tk.Text(root, height=10, width=60)
        self.text_shop_list.grid(row=10, column=3)
        self.text_shop_list.insert(0.0, 'http://www.dianping.com/shop/23123189')

        self.button_appointment = tk.Button(root, text='开始预约')
        self.button_appointment.grid(row=15, column=5)

        self.text_log = scrolledtext.ScrolledText(root)
        self.text_log_vertical_bar = tk.Scrollbar(root)
        self.text_log.grid(row=17, column=0, columnspan=3, )

        self.button_login.config(command=self.click_login)
        self.button_get_base_info.config(command=self.click_get_base_info)
        self.button_appointment.config(command=self.click_appointment)

        root.mainloop()

    def log(self, log_str):
        now = str(datetime.now())
        self.text_log.insert(tk.END, ''.join([now, ':', log_str, '\n']))

    # 大众点评项目名称160
    def get_token_by_login_yima(self, username, password):
        response = requests.get(
            url='http://api.fxhyd.cn/UserInterface.aspx?action=login&username={username}&password={password}'.format(
                username=username, password=password))
        if 'success' in response.text:
            status, token = response.text.split('|')
            return token
        else:
            print('Error getting token by login')
            return None

    def get_base_info(self, token):
        response = requests.get(
            url='http://api.fxhyd.cn/UserInterface.aspx?action=getaccountinfo&token={token}'.format(token=token))
        if 'success' in response.text:
            status, username, account_status, account_level, account_balance, account_freezing_balance, account_discount, account_get_phone_max_limit = response.text.split(
                '|')
            return username, account_status, account_level, account_balance, account_freezing_balance, account_discount, account_get_phone_max_limit
        else:
            return None

    def get_phone_num(self, token):
        response = requests.get(
            url='http://api.fxhyd.cn/UserInterface.aspx?action=getmobile&token={token}&itemid=160&excludeno='.format(
                token=token))
        if 'success' in response.text:
            status, phone_num = response.text.split('|')
            self.log('成功获取手机号：%s' % (phone_num))
            return phone_num
        else:
            self.log('获取手机号失败！')
            return None

    def block_phone_num(self, token, phone_num):
        response = requests.get(
            url='http://api.fxhyd.cn/UserInterface.aspx?action=addignore&token={token}&itemid=160&mobile={phone_num}'.format(
                token=token, phone_num=phone_num))
        if 'success' in response.text:
            self.log('拉黑号码成功，手机号码：%s' % (phone_num))
        else:
            self.log('拉黑号码失败，手机号码：%s' % (phone_num))

    def get_phone_text(self, token, phone_num, retry_time_zone):
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
            return response.text

        start_time = datetime.now()
        while True:
            end_time = datetime.now()
            if (end_time - start_time).total_seconds() > retry_time_zone:
                self.log('获取验证码超时！%s秒' % (str(retry_time_zone)))
                return None
            time.sleep(3)
            response_text = get_phone_text(token, phone_num)
            if '3001' in response_text:
                self.log('验证码未接受到！')
                continue
            else:
                status, text = response_text.split('|')
                identifying_code = re.sub('\D', '', text)
                self.log('验证码获取成功，验证码：%s' % (identifying_code))
                break

        return identifying_code

    def reg(self, token, phone_num, url_list):
        browser = webdriver.Chrome()
        # 点评注册主页
        reg_url = 'https://www.dianping.com/reg'
        browser.get(reg_url)
        WebDriverWait(browser, 30).until(
            lambda x: x.find_element_by_xpath('//*[@id="easy-login-container"]/div/iframe'))
        time.sleep(2)
        browser.switch_to.frame(browser.find_element_by_xpath('//*[@id="easy-login-container"]/div/iframe'))
        WebDriverWait(browser, 30).until(
            lambda x: x.find_element_by_id('mobile-number-textbox'))
        time.sleep(2)
        browser.find_element_by_id('mobile-number-textbox').send_keys(phone_num)
        WebDriverWait(browser, 30).until(
            lambda x: x.find_element_by_id('send-number-button'))
        browser.find_element_by_id('send-number-button').click()
        time.sleep(3)
        alert_text = browser.find_element_by_class_name('alert-content').text
        if "动态码已发送，请查看手机" in alert_text:
            browser.find_element_by_id('password-textbox').send_keys('zidonghuazhucE!1')
            browser.find_element_by_id('agreePolicy').click()
            # 点击注册用户
            identifying_code = None
            for times in range(0, 2):
                identifying_code = self.get_phone_text(token, phone_num, 65)
                if identifying_code:
                    break
                browser.find_element_by_id('send-number-button').click()
            if not identifying_code:
                self.log('获取验证码超时，手机号码：%s' % (phone_num))
                browser.close()
                return

            browser.find_element_by_id('number-textbox').send_keys(identifying_code)
            browser.find_element_by_id('register-button').click()
            self.log('号码：%s，注册成功！' % (phone_num))
            time.sleep(1)
            self.appointment(browser, url_list)
        else:
            self.log('号码：%s，已经被注册！' % (phone_num))
            self.login_and_appointment(token, phone_num, url_list)
        browser.close()

    def login_and_appointment(self, token, phone_num, url_list):
        self.log('手机验证码登陆中···')
        browser = webdriver.Chrome()
        # 点评注册主页
        login_url = 'https://account.dianping.com/login'
        browser.get(login_url)
        WebDriverWait(browser, 30).until(
            lambda x: x.find_element_by_xpath('//*[@id="J_login_container"]/div/iframe'))
        time.sleep(2)
        # browser.switch_to.frame(src ='https://www.dianping.com/account/iframeRegister?callback=EasyLogin_frame_callback0&wide=false&protocol=https:&redir=https%3A%2F%2Fwww.dianping.com')
        browser.switch_to.frame(browser.find_element_by_xpath('//*[@id="J_login_container"]/div/iframe'))

        WebDriverWait(browser, 30).until(
            lambda x: x.find_element_by_class_name('bottom-password-login'))
        time.sleep(2)
        browser.find_element_by_class_name('bottom-password-login').click()
        WebDriverWait(browser, 30).until(
            lambda x: x.find_element_by_id('mobile-number-textbox'))
        time.sleep(2)
        browser.find_element_by_id('mobile-number-textbox').send_keys(phone_num)
        identifying_code = None
        for times in range(0,2):
            browser.find_element_by_id('send-number-button').click()
            identifying_code = self.get_phone_text(token, phone_num, 65)
            if identifying_code:
                break
        if not identifying_code:
            self.log('获取验证码超时，手机号码：%s'%(phone_num))
            browser.close()
            return
        browser.find_element_by_id('number-textbox').send_keys(identifying_code)
        browser.find_element_by_id('login-button-mobile').click()
        time.sleep(2)
        self.appointment(browser, url_list)
        self.block_phone_num(token, phone_num)
        browser.close()

    def appointment(self, browser, url_list):
        for url in url_list:
            self.log('预约中：%s' % url)
            browser.get(url)
            WebDriverWait(browser, 30).until(
                lambda x: x.find_element_by_css_selector('.btn.J-rs-btn'))
            time.sleep(2)
            browser.find_element_by_css_selector('.btn.J-rs-btn').click()
            WebDriverWait(browser, 30).until(
                lambda x: x.find_element_by_css_selector('.medi-btn.stress-btn.J_btnSubmit'))
            time.sleep(2)
            browser.find_element_by_css_selector('.medi-btn.stress-btn.J_btnSubmit').click()
            WebDriverWait(browser, 30).until(
                lambda x: x.find_element_by_css_selector('.medi-btn.stress-btn.J_btnCancel'))
            time.sleep(2)
            browser.find_element_by_css_selector('.medi-btn.stress-btn.J_btnCancel').click()
            self.log('预约成功：%s' % url)
            print('预约成功：%s' % url)

    def click_login(self, ):
        token = self.get_token_by_login_yima(self.entry_username.get(), self.entry_password.get())
        if token:
            self.label_login_status.config(text="登陆成功，token值为：{token}".format(token=token))
            self.log('登录成功')
            self.token = token
            self.click_get_base_info()
        else:
            self.log('失败')
            self.label_login_status.config(text="登陆失败")

    def click_get_base_info(self):
        if not self.token:
            print('请先登陆！')
            self.log('请先登陆')
        base_info = self.get_base_info(self.token)
        if base_info:
            self.log('获取用户基本信息成功')
            self.label_username.config(text=base_info[0])
            self.label_account_status.config(text=base_info[1])
            self.label_account_level.config(text=base_info[2])
            self.label_account_balance.config(text=base_info[3])
            self.label_account_freezing_balance.config(text=base_info[4])
            self.label_account_discount.config(text=base_info[5])
            self.label_account_get_phone_max_limit.config(text=base_info[6])
        else:
            self.log('获取用户基本信息失败')
            self.label_username.config(text='获取失败')
            self.label_account_status.config(text='获取失败')
            self.label_account_level.config(text='获取失败')
            self.label_account_balance.config(text='获取失败')
            self.label_account_freezing_balance.config(text='获取失败')
            self.label_account_discount.config(text='获取失败')
            self.label_account_get_phone_max_limit.config(text='获取失败')

    def click_appointment(self):
        try:
            get_phone_num_count = int(self.entry_get_phone_num_count.get())
            url_list = self.text_shop_list.get(0.0, 'end').splitlines()
            for url in url_list:
                if not validators.url(url):
                    self.log('店铺链接必须为真实！')
                    return
        except Exception:
            self.log('输入的手机数量必须为数字！')
            return

        for text_name in range(0, get_phone_num_count):
            phone_num = self.get_phone_num(self.token)
            self.reg(self.token, phone_num, url_list)


appointmentApp()
