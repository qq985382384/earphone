
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


def product_details(request):
    return render(request,'buyers/product-details.html')

def products(request,id):
    id = int(id)
    if id == 0:
        type = {'label':'全部耳机','description':'所有商品，尽情挑选'}
        goods = Goods.objects.all()
    else:
        type = Types.objects.get(id=id)
        goods = Goods.objects.filter(types=id)
    data = []
    for i in goods:
        img = i.image_set.first().img_path
        data.append({'img':img,'goods':i})
    return render(request,'buyers/products.html',{'data':data,'type':type})

@cookieVerify
def cart(request):
    return render(request,'buyers/cart.html',locals())


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
