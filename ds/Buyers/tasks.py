import time

from celery import shared_task

# 注册任务
from celery.signals import task_success


@shared_task
def hello(num):
    for i in range(num):
        print("Hello")
        time.sleep(1)

@shared_task
def add(a,b):
    return a + b

#获取返回结果
@task_success.connect(sender=add)
def lxd_task(sender,result,**kwargs):
    print("李欣东")
    print(sender,sender.name)
    print(result)