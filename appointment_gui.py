import re
import tkinter as tk
from datetime import datetime
from tkinter import scrolledtext

import requests


class appointmentApp():
    def __init__(self):

        self.token = None
        root = tk.Tk()
        root.title('易码平台工具')
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

        tk.Label(root, text='获取手机号项目编号（数字）:').grid(row=10, column=0)
        self.entry_item_id = tk.Entry(root)
        self.entry_item_id.grid(row=10, column=1)
        self.entry_item_id.insert(0, '9603')

        self.button_get_phone_num = tk.Button(root, text='获取手机号')
        self.button_get_phone_num.grid(row=10, column=2)

        tk.Label(root, text='获取到的手机号:').grid(row=11, column=0)
        self.phone_num_entry = tk.Entry(root)
        self.phone_num_entry.grid(row=11, column=1)
        self.phone_num_entry.insert(0, '')

        self.button_get_text = tk.Button(root, text='获取短信')
        self.button_get_text.grid(row=11, column=2)

        # tk.Label(root, text='超时时间(s):').grid(row=11, column=3)
        # self.time_out_entry = tk.Entry(root)
        # self.time_out_entry.grid(row=11, column=4)
        # self.time_out_entry.insert(0, '300')

        tk.Label(root, text='获取到的验证码:').grid(row=12, column=0)
        self.verification_code_entry = tk.Entry(root)
        self.verification_code_entry.grid(row=12, column=1)
        self.verification_code_entry.insert(0, '')

        self.text_log = scrolledtext.ScrolledText(root)
        self.text_log_vertical_bar = tk.Scrollbar(root)
        self.text_log.grid(row=17, column=0, columnspan=3, )

        self.button_login.config(command=self.click_login)
        self.button_get_base_info.config(command=self.click_get_base_info)
        self.button_get_phone_num.config(command=self.click_get_phone_num)
        self.button_get_text.config(command=self.click_get_text)

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

    def get_phone_num(self, token, item_id):
        response = requests.get(
            url='http://api.fxhyd.cn/UserInterface.aspx?action=getmobile&token={token}&itemid={item_id}&excludeno='.format(
                token=token, item_id=item_id))
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

    '''
    http://api.fxhyd.cn/UserInterface.aspx?action=getsms&token=TOKEN&itemid=项目编号&mobile=手机号码&release=1
    收到短信：success|短信内容
    短信尚未到达：3001，应继续调用取短信接口，直到超时为止。
    请求失败：错误代码，请根据不同错误代码进行不同的处理。
    '''

    def get_phone_text(self, token, phone_num, item_id):
        response = requests.get(
            url='http://api.fxhyd.cn/UserInterface.aspx?action=getsms&token={token}&itemid={item_id}&mobile={phone_num}'.format(
                token=token, phone_num=phone_num, item_id=item_id))
        if '3001' in response.text:
            self.log('验证码未接受到！')
            return None
        else:
            tatus, text = response.text.split('|')
            identifying_code = re.sub('\D', '', text)
            self.log('验证码获取成功，验证码：%s' % (identifying_code))
            return identifying_code

    def click_login(self):
        token = self.get_token_by_login_yima(self.entry_username.get(), self.entry_password.get())
        if token:
            self.label_login_status.config(text="登陆成功，token值为：{token}".format(token=token))
            self.log('登录成功')
            self.token = token
            self.click_get_base_info()
        else:
            self.log('登录失败')
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

    def click_get_phone_num(self):
        if not self.token:
            print('请先登陆！')
            self.log('请先登陆')
            return
        item_id = self.entry_item_id.get()
        if not item_id:
            print('没有项目编号，请先输入项目编号')
            self.log('没有项目编号，请先输入项目编号')
            return
        phone_num = self.get_phone_num(self.token, item_id)
        self.phone_num_entry.insert(0, phone_num)

    def click_get_text(self):
        if not self.token:
            print('请先登陆！')
            self.log('请先登陆')
            return
        phone_num = self.phone_num_entry.get()
        if not phone_num:
            print('没有手机号，请先获取手机号')
            self.log('没有手机号，请先获取手机号')
            return
        item_id = self.entry_item_id.get()
        if not item_id:
            print('没有项目编号，请先输入项目编号')
            self.log('没有项目编号，请先输入项目编号')
            return
        # time_out = self.time_out_entry.get()
        # if not time_out:
        #     print('没有设置超时时间')
        #     self.log('没有设置超时时间')
        #     return
        verification_code = ''
        self.get_phone_text(self.token, phone_num, item_id)
        if verification_code:
            self.verification_code_entry.insert(0, verification_code)


appointmentApp()
