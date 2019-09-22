import os

from django.db.models import Count
from django.shortcuts import render,HttpResponseRedirect
from django.core.mail import EmailMultiAlternatives
from django.http import JsonResponse, HttpResponse
import random,datetime,time,hashlib

from rest_framework.response import Response
from rest_framework.views import APIView

from Buyers.models import *
from Shop.models import Goods, Types
from Shop.tools.uploads import FileUpload
from ds import settings
from ds.settings import EMAIL_HOST_USER, MEDIA_ROOT


# Create your views here.


def cookieVerify(fun):
    def inner(request,*args,**kwargs):
        username = request.COOKIES.get('username')
        session = request.session.get('username')
        user = Buyer.objects.filter(username=username).first()
        if user and session == username:
            return fun(request,*args,**kwargs)
        else:
            return HttpResponseRedirect('/buyers/login/')
    return inner





def index(request):
    userid = request.COOKIES.get('user_id')
    user = Buyer.objects.filter(id=userid).first()
    count = BuyCar.objects.filter(user_id=userid).aggregate(num=Count('user_id'))
    allcart = count['num']
    user = Buyer.objects.filter(id = userid).first()
    return render(request,'buyers/index.html',locals())


def products(request,id):
    userid = request.COOKIES.get('user_id')
    user = Buyer.objects.filter(id=userid).first()


    id = int(id)
    if id == 0:
        type = {'label':'全部耳机','description':'所有商品，尽情挑选'}
        goods = Goods.objects.all()
    else:
        type = Types.objects.get(id=id) #取出这个类型的详情
        goods = Goods.objects.filter(types=id) # 去除这个类型的全部商品
    data = []
    for i in goods:
        img = i.image_set.first().img_path #取这个商品的第一张图片路径
        data.append({'img':img,'goods':i}) # 将每个商品的信息与图片写入字典data中
    return render(request,'buyers/products.html', {'data':data,'type':type,'user':user})

def product_details(request,id):

    id = int(id)
    goods = Goods.objects.get(id=id)
    imgs = goods.image_set.all()
    showGoods = Goods.objects.all().order_by('-goods_now_price')[0:3]
    data = []
    for i in showGoods:
        img = i.image_set.first().img_path #取出商品的第一张图片路径
        data.append({'img':img,'goods':i}) #取出每个商品的信息与图片写入字典
    userid = request.COOKIES.get('user_id')
    user = Buyer.objects.filter(id=userid).first()

    return render(request,'buyers/product-details.html',locals())


def blogin(request):
    result = {"status": "error", "data": ""}
    if request.POST and request.method == 'POST':
            email = request.POST.get('email')
            print(email)
            user = Buyer.objects.filter(email=email).first()
            if user.isactive <5:
                if user:
                    pwd = lockpw(request.POST.get('password'))
                    if pwd == user.password:
                        user = Buyer.objects.filter(email=email).first()
                        response = HttpResponseRedirect('/buyers/',locals())
                        response.set_cookie('user_id',user.id,max_age=3600)
                        response.set_cookie('username',user.username,max_age=3600)
                        request.session['username']=user.username
                        return response
                    else:
                        user.isactive+=1
                        user.save()
                        result['data'] = '密码错误'
                else:
                    result['data'] = '用户名不存在'
            else:
                result['data'] = '用户被冻结，请先去 <a href="/buyers/findpassword/" class="text-success">修改密码</a>'


    return render(request,'buyers/login.html',locals())

def getRandomData():
    result = str(random.randint(1000,9999))
    return result

def lockpw(pw):
    md5 = hashlib.md5()
    md5.update(pw.encode())
    result = md5.hexdigest()
    return result

def sendMessage(request):
    result = {"status": "error", "data": ""}
    if request.method == 'GET' and request.GET:
        receiver = request.GET.get('email')
        print(receiver)
        try:
            subject = "耳机商城的邮件"
            text_content = ""
            value = getRandomData()
            html_content = """
                <div>
                    <p>
                        尊敬的耳机商城用户，您的用户验证码是:%s,打死不要告诉别人。
                    </p>
                </div>
                """ % value
            message = EmailMultiAlternatives(subject, text_content, EMAIL_HOST_USER, [receiver])
            message.attach_alternative(html_content, "text/html")
            message.send()
        except Exception as e:
            result["data"] = str(e)
        else:
            result["status"] = "success"
            result["data"] = "验证码已发送"
            e = EmailValid()
            e.email_address = receiver
            e.value = value
            e.times = datetime.datetime.now()
            e.save()
        finally:
            return JsonResponse(result)

def register(request):
    result = {"status": "error", "data": ""}

    if request.method == 'POST' and request.POST:
        email = request.POST.get('email')
        user = Buyer.objects.values_list("email")

        print(user)
        username = request.POST.get('username')
        message = request.POST.get('message')
        pwd = request.POST.get('password')
        db_email = EmailValid.objects.filter(email_address=email).latest('id')
        if (email,) in user:
            result['data'] = '该邮箱已经注册'
        else:
            if db_email:
                if message == db_email.value:
                    now = time.mktime(
                        datetime.datetime.now().timetuple()
                    )
                    db_now = time.mktime(db_email.times.timetuple())
                    if now - db_now > 600:
                        result['data'] = '验证码过期'
                        db_email.delete()
                    else:
                        b = Buyer()
                        b.username = username
                        b.email = email
                        b.password = lockpw(pwd)
                        b.save()
                        db_email.delete()
                        return HttpResponseRedirect('/buyers/login/')  # 注册成功跳转到登录页
                else:
                    result['data'] = '验证码错误'
            else:
                result['data'] = '邮箱不匹配'
    return render(request, 'buyers/register.html', locals())



def blogout(request):
    response = HttpResponseRedirect('/buyers/')
    response.delete_cookie('user_id')
    response.delete_cookie('username')
    del request.session['username']
    return response

@cookieVerify
def cart(request):

    userid = request.COOKIES.get('user_id')
    user = Buyer.objects.filter(id=userid).first()
    buycarGoos = BuyCar.objects.filter(user=userid)
    alltotal = 0
    data = []
    for i in buycarGoos:
        goods = Goods.objects.get(id=i.goods_id)
        total = i.goods_num * i.goods_price
        alltotal += total
        data.append({'total':total,'goods':i,'js':goods.goods_id})
    return render(request,'buyers/cart.html',locals())
@cookieVerify
def addcart(request,id):
    user1 = BuyCar()
    userid = request.COOKIES.get('user_id')
    user = Buyer.objects.filter(id=userid).first()
    usergoods = Goods.objects.get(id=int(id))
    user1.goods_id = usergoods.id
    user1.goods_name = usergoods.goods_name
    user1.goods_picture = usergoods.image_set.first().img_path
    user1.goods_price = usergoods.goods_price
    user1.user_id = userid
    user1.goods_num = 1
    user1.save()
    return HttpResponseRedirect('/buyers/cart/')


def delcart(request,id):
    userId = request.COOKIES.get('user_id')
    user = Buyer.objects.filter(id=userId).first()
    goods = BuyCar.objects.get(user=int(userId),id=int(id))
    goods.delete()
    return HttpResponseRedirect('/buyers/cart/')

'''
首先获取商品数量，
传过来的quantity列表中的总数量，代表购物车里有几个商品，
顺序与数据库的顺序是一致的，
通过for循环递增的i，来依次取出数量，存入数据库。
'''
def order(request):
    alltotal = 0
    data = []
    userId = request.COOKIES.get('user_id')
    user = Buyer.objects.filter(id=userId).first()
    address1 = Address.objects.filter(buyer_id=user).filter(num=0)
    print(address1)
    if request.method == 'POST' and request.POST:
        count = request.POST.getlist('quantity')
        for i in range(0,len(count)):
            buycar = BuyCar.objects.filter(user=userId)[i]
            buycar.goods_num = count[i]
            buycar.save()
            total = int(buycar.goods_price)*int(buycar.goods_num)
            data.append({'total':total,'goods':buycar})
            alltotal += total

    return render(request, 'buyers/enterorder.html', locals())


def pay(request):


    if request.POST and request.method == 'POST':
        alltotal = 0
        goods_list = []
        userId = request.COOKIES.get('user_id')

        #取出购物车可购买的商品
        buycar = BuyCar.objects.filter(user=userId)
        for goods in buycar:
            total = int(goods.goods_price) * int(goods.goods_num)
            goods_list.append({'total':total,'goods':goods})
            alltotal+=total

        address = Address()
        address.address = request.POST.get('address')
        address.username = request.POST.get('username')
        address.phone = request.POST.get('phone')
        address.buyer = Buyer.objects.get(id=userId)
        address.save()

        #在订单表中生成订单
        order = Order()
        #订单编号 日期年月日 + 随机 + 用户 id
        now = datetime.datetime.now()
        order.order_num = now.strftime('%Y%m%d%H%M%S')+str(random.randint(10000,99999))+userId
        #状态 未支付1 支付成功2 配送中3 交易完成4 取消 0
        order.order_time = now
        order.order_statue=1
        order.total=alltotal
        order.user = Buyer.objects.get(id=userId)
        order.order_address = address
        order.save()
        #订单商品
        for good in goods_list:  #循环保存订单中的商品
            g = good["goods"]
            goods = OrderGoods()
            goods.good_id = g.goods_id
            goods.good_name = g.goods_name
            goods.good_price = g.goods_price
            goods.good_num = g.goods_num
            goods.goods_picture=g.goods_picture
            goods.order = order
            goods.save()
        cargoods = BuyCar.objects.get(user=int(userId))
        cargoods.delete()
    return render(request,'buyers/enterpay.html',locals())

#支付跳转函数

from alipay import AliPay


def paydata(order_num,count):

    alipay = AliPay(
        appid=settings.APPID,  # 支付宝app的id
        app_notify_url=None,  # 回调视图
        app_private_key_string=settings.APP_PRIVATE_KEY,  # 私钥字符
        alipay_public_key_string=settings.ALIPAY_PUBLIC_KEY,  # 公钥字符
        sign_type="RSA2",  # 加密方法
    )

    order_string = alipay.api_alipay_trade_page_pay(
        out_trade_no=str(order_num),
        total_amount=str(count),  #将Decimal类型转换为字符串交给支付宝
        subject="耳机商城",
        return_url='http://127.0.0.1:8000/buyers/checkpay',
        notify_url=None  # 可选, 不填则使用默认notify url
    )

    return  "https://openapi.alipaydev.com/gateway.do?" + order_string

def checkpay(request):
    orderid = request.GET.get('out_trade_no')
    order = Order.objects.get(order_num=orderid)
    order.order_statue=2
    order.save()
    return HttpResponseRedirect('/buyers/person_order2/')


def payverify(request,id):
    order = Order.objects.get(id=int(id))
    order_num = order.order_num
    order_count = order.total
    url = paydata(order_num,order_count)
    return HttpResponseRedirect(url)



@cookieVerify
def person(request):
    time = datetime.datetime.now()
    username = request.session['username']
    print(username)
    user = Buyer.objects.filter(username=username).first()

    if request.method =="POST":
        user_name = request.POST.get("user_name")
        user_email = request.POST.get("email")
        user_signature = request.POST.get("user_qianming")
        user_photo = request.POST.get("photo")
        user.username = user_name
        user.email = user_email
        user.signature = user_signature
        file_obj = request.FILES.get('photo')
        obj = FileUpload(file_obj, is_randomname=False)
        path = MEDIA_ROOT
        if obj.upload(path) > 0:
            tupath = os.path.join(obj.file.name)
            user.portrait = tupath
            user.save()
    return render(request, 'buyers/person.html', locals())
@cookieVerify
def upload(request):
    if request.method =="POST":
        file_obj = request.FILES.get('photo')
        obj = FileUpload(file_obj,is_randomname=True)
        path = MEDIA_ROOT
        if obj.upload(path)  >0:
            return HttpResponse("chenggong")
        else:
            return HttpResponse("shibai")
    return render(request,"fileupload.html")

@cookieVerify
def address(request,id):
    buyer = Buyer.objects.filter(id=id).first()
    address = Address.objects.filter(buyer_id=id).filter(num=0)
    if request.method=="POST":
        address_add(request,id=id)

    return render(request,"buyers/person_address.html",locals())

@cookieVerify
def address_add(request,id):
    username = request.POST.get("username")

    phone = request.POST.get("phone")

    address = request.POST.get("address")

    address_new = Address()
    address_new.buyer_id = id
    address_new.phone=phone
    address_new.username=username
    address_new.address=address
    address_new.save()
    return render(request,"buyers/person_address.html",locals())


def address_del(request,aid):
    address1 = Address.objects.filter(id=aid).first()
    id = address1.buyer_id
    address1.num = 1
    address1.save()
    print(id)
    buyer = Buyer.objects.filter(id=id).first()
    address = Address.objects.filter(buyer_id=id).filter(num=0)
    return render(request,"buyers/person_address.html",locals())


def address_change(request,aid):
    address1 = Address.objects.filter(id=aid).first()
    id = address1.buyer_id
    buyer = Buyer.objects.filter(id=id).first()
    if request.method=="POST":
        username = request.POST.get("user_name")
        phone = request.POST.get("phone")
        adress_1 = request.POST.get("address")

        address1 = Address.objects.filter(id=aid).first()
        address1.address = adress_1
        address1.phone = phone
        address1.username = username
        address1.save()

    return render(request,"buyers/person_change.html",locals())


def person_mima(request,id):
    result = {"status": "error", "data": ""}
    user = Buyer.objects.filter(id=id).first()
    if request.method =="POST":
        old = request.POST.get("old_password")
        new = request.POST.get("new_password")
        re = request.POST.get("re_password")
        if lockpw(old) == user.password:
            if new ==re:
                user.password=lockpw(new)
                result["status"] = "success"
                result["data"] = "密码次改成功！！！"
                return render(request, "buyers/person_mima.html", locals())

            else:
                result['data'] = "两次密码不一致"
                return render(request, "buyers/person_mima.html", locals())
        else:
            result['data'] = "旧密码错误"
    return render(request,"buyers/person_mima.html",locals())


def person_order(request,id):
    orders = Order.objects.filter(user_id=id)
    return render(request,"buyers/myorder.html",locals())


def ordergoods(request,id):
    ordergood = OrderGoods.objects.filter(order_id=id)
    return render(request,"buyers/ordergoods.html",locals())


def shouhuo(request,id):

    order = Order.objects.filter(id=id).first()
    order.order_statue = 4
    order.save()
    uid = order.user_id
    orders = Order.objects.filter(user_id=uid)
    return render(request,"buyers/myorder.html",locals())

import re
def findpassword(request):
    result = {"status": "error", "data": ""}


    if request.method=="POST":
        email = request.POST.get("email")
        message = request.POST.get('message')
        password = request.POST.get("password")
        re_password = request.POST.get("re_password")
        user = Buyer.objects.values_list("email")
        if not (email,) in user:
            result['data'] = '该邮箱未注册，请先注册'
        else:
            db_email = EmailValid.objects.filter(email_address=email).latest('id')
            if db_email:
                if message == db_email.value:
                    now = time.mktime(
                        datetime.datetime.now().timetuple()
                    )
                    db_now = time.mktime(db_email.times.timetuple())
                    if now - db_now > 600:
                        result['data'] = '验证码过期'
                        db_email.delete()
                    else:
                        regex = '^.*(?=.{6,16})(?=.*\d)(?=.*[A-Z])(?=.*[a-z]).*$';
                        bold = re.fullmatch(regex,password)
                        if bold:
                            if password==re_password:
                                user = Buyer.objects.filter(email=email).filter().first()
                                user.password=lockpw(password)
                                user.isactive=0
                                user.save()
                                return HttpResponseRedirect('/buyers/login/')  # 注册成功跳转到登录页
                            else:
                                result['data'] = '验证码错误'
                                return HttpResponseRedirect('/buyers/findpassword/',locals())
                        else:
                            result['data'] = '密码格式错误'
                            return HttpResponseRedirect('/buyers/findpassword/', locals())
                else:
                    result['data'] = '验证码错误'
            else:
                result['data'] = '邮箱不匹配'



    return render(request,"buyers/findpassword.html",locals())


def person_order2(request):
    userid = request.COOKIES.get('user_id')
    user = Buyer.objects.filter(pk=userid).first()
    orders = Order.objects.filter(user_id=int(userid))
    return render(request,'buyers/myorder2.html',locals())