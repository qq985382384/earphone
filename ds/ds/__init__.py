
from __future__ import absolute_import
from .celery import app as celery_app

from django.dispatch import receiver
# from .mysignal import my_signal

#自定义信号
# @receiver(my_signal)
# def process_signal(sender,a,**kwargs):
#     print(sender)
#     print(a)
#     print(kwargs)
#     print("process_signal")
#



import pymysql
pymysql.install_as_MySQLdb()