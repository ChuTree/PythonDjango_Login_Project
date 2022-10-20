# -*- coding:utf-8 -*-
'''
@Time : 2022/10/20  16:35
@File : send_email.py
@Sofeware : PyCharm 
@author : Chen
'''
import os,django

from django.core.mail import send_mail

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "PythonDjango_Login_Project")
django.setup()


if __name__ == '__main__':
    send_mail(
        '来自chensd的测试邮件',
        'testtest',
        'chenshudong1127@163.com',
        ['2248830979@qq.com'],
    )