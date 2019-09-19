
from django.shortcuts import render,HttpResponseRedirect
from django.core.mail import EmailMultiAlternatives
from django.http import JsonResponse
import random,datetime,time,hashlib
from Buyers.models import *
from Shop.models import Goods, Types
from ds.settings import EMAIL_HOST_USER
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
    return render(request,'buyers/index.html')


def products(request,id):
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
    return render(request,'buyers/products.html',{'data':data,'type':type})

def product_details(request,id):
    id = int(id)
    goods = Goods.objects.get(id=id)
    imgs = goods.image_set.all()
    showGoods = Goods.objects.all().order_by('-goods_now_price')[0:3]
    data = []
    for i in showGoods:
        img = i.image_set.first().img_path #取出商品的第一张图片路径
        data.append({'img':img,'goods':i}) #取出每个商品的信息与图片写入字典
    return render(request,'buyers/product-details.html',locals())


def blogin(request):
    result = {"status": "error", "data": ""}
    if request.POST and request.method == 'POST':
        email = request.POST.get('email')
        print(email)
        user = Buyer.objects.filter(email=email).first()
        if user:
            pwd = lockpw(request.POST.get('password'))
            if pwd == user.password:
                response = HttpResponseRedirect('/buyers/')
                response.set_cookie('user_id',user.id,max_age=3600)
                response.set_cookie('username',user.username,max_age=3600)
                request.session['username']=user.username
                return response
            else:
                result['data'] = '密码错误'
        else:
            result['data'] = '用户名不存在'

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
        print(email)
        print(user)
        username = request.POST.get('username')
        message = request.POST.get('message')
        pwd = request.POST.get('password')
        db_email = EmailValid.objects.filter(email_address=email).latest('id')
        print(db_email.value)
        if (email,) in user:
            result['data'] = '该邮箱已经注册'
        elif db_email:
            if message == db_email.value:
                now = time.mktime(
                    datetime.datetime.now().timetuple()
                )
                db_now = time.mktime(db_email.times.timetuple())
                if now - db_now > 60:
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
    buycarGoos = BuyCar.objects.filter(user=userid)
    alltotal = 0
    data = []
    for i in buycarGoos:
        goods = Goods.objects.filter(id=i.goods_id)
        total = i.goods_num * i.goods_price
        alltotal += total
        data.append({'total':total,'goods':i,'js':goods.goods_id})
    return render(request,'buyers/cart.html',locals())

def addcart(request,id):

    return None


def delcart(request,id):
    userId = request.COOKIES.get('user_id')
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
    return render(request,'buyers/enterpay.html',locals())

#支付跳转函数
from alipay import AliPay
def paydata(order_num,count):
    alipay_public_key_string = '''-----BEGIN PUBLIC KEY-----
   MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAlHEg4KZ9r0o4Wg8Qb6rbYL2sOJ6DfMUYgoj07GCeeXqUUPgeR8CkWHuoB5fyCcOQ8OXDmJBu6kUijjsGK/94vqvW4SPuzgvsCkZv98/ajh/YB8jYrf40NhHoalJ6jUcT6Id9y/BYX4773rVOvR0Eq7r1EFYg8LUch2j/Y6q4HHcolz2La1wHLUxaI16pFj+QGbmb6EK8qE3KJy/A/lBNRhNMJeSTVdkyk42rqsRp0fy74AnEt/xRh7fyr61N/jN7j0/oGSTI/vvtzDib+ezt+JXUJMa6rP1c5pclRyWRQn+ZS5N1IadpgE8m88UR8RTUaZCXsIP0/c4t7KNVgudOAwIDAQAB
    -----END PUBLIC KEY-----'''

    app_private_key_string = '''-----BEGIN RSA PRIVATE KEY-----
    MIIEvwIBADANBgkqhkiG9w0BAQEFAASCBKkwggSlAgEAAoIBAQCUcSDgpn2vSjhaDxBvqttgvaw4noN8xRiCiPTsYJ55epRQ+B5HwKRYe6gHl/IJw5Dw5cOYkG7qRSKOOwYr/3i+q9bhI+7OC+wKRm/3z9qOH9gHyNit/jQ2EehqUnqNRxPoh33L8FhfjvvetU69HQSruvUQViDwtRyHaP9jqrgcdyiXPYtrXActTFojXqkWP5AZuZvoQryoTconL8D+UE1GE0wl5JNV2TKTjauqxGnR/LvgCcS3/FGHt/KvrU3+M3uPT+gZJMj+++3MOJv57O34ldQkxrqs/VzmlyVHJZFCf5lLk3Uhp2mATybzxRHxFNRpkJewg/T9zi3so1WC504DAgMBAAECggEAIkh+b2QEYxehLCuOgDvVruIfhHQXqhlbL8qxxmYKM8Q7vPeRBsFXM5hblmVhYR/publXE0VIWJLfCDpZko/OMzs8xYKnBK98NGNQOMuojmqMWj/oy0aKiHJaWzPxWe+wiWPBifhYcLl1MlptdP/etErZjoxVz0IE9MErOrmTC/+dF/qTcvCgZEWwVYex9z9vMBmAo7ndbzcHqBAzISQMkMrkToelY9+1EgfWU7oserayly0mu9QhnH6pdOAl9/N8rbb5Bka2eZ1nc/UtvVrf7CpKNLbjMabPZixpynqGyE8MUDMqkBzQ2qpZulaijmQXG5sLrY9ZqLFLdnvV9d4MAQKBgQDx/I8OMgJpMmQpXM65qdrOD3vM82vNJ7FEf7ObMhfAKeNMICWSWx/6GKThZDtusAc/ZuwvY9dZw4u3Izplw56FuI/U2OhE+QOlFKoBH425IAe3KaF4XMAp+n3n1UZp1m4XD1+ZM0ZpddecbW37Eg6Z0iluMNCMr0oUc5q2fxEVMQKBgQCdCcYcHa24sB1sZDGillCfrhYECx9ws66JdUnlGTlm3yxlV89x5pynrDaV2gLA3kB93LSe6zu+HXhx4czWgILAPLWtjAMzYAS21WGnh2so0eM/oug8wbo0U4srMnmnGoPmX+6rtOJWPWxfJbmlIPEHLhkaMu5HbS4+r5L273kZcwKBgQDh6PWou/lSOlAV6WW5ISB7ZSsfsFUAx0CQAWQsy/wuUyy3Af/xfY8BzgYHwapWcJGjmDOBHoWKcKs7wvCe1pxknGPywrk8wvirIfqAZ/PIU2XAkmYDVxuzVP478/jzj9NhReHqxVrD09cBW4vka/wjkHdLPtlDrdXL+A0EuOW60QKBgQCCbbu9XmkLHDtT62PORkpwVYazlQln8dTlFiVpwqmKZ5HYGjaRw5gZK0+q5oei6PVnlAfwdjAIlzGSZJhdEB+IyuOaYM/Hu9gugsu4+SBnpuu3zvZUgBLHoxvTpPilccBbdxIkSvgx6JI59HtcSx/ldsQinmqJqITgS7MkpYFPQQKBgQCxUi2yh8r0Y9RSDgfmghF4S2XxivGwsn6HZNekCNDbgGg+GUj5YLn1KuKvCvGbWhAReo4lYDg+6NQjy94qF7JB682xZsS8MHsJXTv9objT99BvRXH6TEn35vZu+FCc7B8Ag6qDJaQJGW83sW4blN/QhE54O68DhO9ibo1vXZ8ooA==
    -----END RSA PRIVATE KEY-----'''

    alipay = AliPay(
        appid="2016101300676110",  # 支付宝app的id
        app_notify_url=None,  # 回调视图
        app_private_key_string=app_private_key_string,  # 私钥字符
        alipay_public_key_string=alipay_public_key_string,  # 公钥字符
        sign_type="RSA2",  # 加密方法
    )

    order_string = alipay.api_alipay_trade_page_pay(
        out_trade_no=str(order_num),
        total_amount=str(count),  #将Decimal类型转换为字符串交给支付宝
        subject="耳机商城",
        return_url=None,
        notify_url=None  # 可选, 不填则使用默认notify url
    )
    return  "https://openapi.alipaydev.com/gateway.do?" + order_string


def payverify(request,id):
    return 