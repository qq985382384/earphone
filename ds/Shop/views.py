import datetime
import hashlib
import os

from django.db.models import Count
from django.http import HttpResponseRedirect, HttpResponse

# Create your views here.

from django.shortcuts import render

from Buyers.models import *
from Shop.models import Seller, Goods, Types, Image
from ds.settings import MEDIA_ROOT
from Shop.tools.uploads import FileUpload


def cookieVerify(fun):
    def inner(request, *args, **kwargs):
        username = request.COOKIES.get("username")  # 获取cookies中的username
        session = request.session.get("nickname")  # 获取session中的nickname
        db_user = Seller.objects.filter(username=username).first()
        if db_user and db_user.nickname == session:  # 校验session和cookies
            return fun(request, *args, **kwargs)  # 通过按照原函数返回
        else:
            return HttpResponseRedirect("/shops/login/")  # 校验失败跳转至登录页

    return inner


@cookieVerify
def index(request):
    goods_num = Goods.objects.aggregate(num = Count('id'))
    num1=goods_num['num']
    buyers_num = Buyer.objects.aggregate(num=Count('id'))
    num2=buyers_num['num']
    order_num = Order.objects.aggregate(num=Count('id'))
    num3 = order_num['num']



    time = datetime.datetime.now()
    if request.POST:
        name =request.session.get('username')
        print("132")
        print(name.id)
        user = Seller.objects.filter(username=name).first()
    return render(request,'shops/index.html',locals())

def login(request):
    result = {'status': 'error', 'data': ''}  # 状态标记，用来返回给前端页面登陆不成功的原因
    if request.POST and request.method == 'POST':  # 如果请求方式为POST且有请求内容
        username = request.POST.get('username')  # username是前台页面input标签中name属性所写内容
        user = Seller.objects.first()
        print(user)
        db_user = Seller.objects.filter(username=username).first()  # 使用filter的方法取出数据库中字段与前台输入相符的人
        if db_user:  # 如果在数据库中取到了，说明有此用户
            db_password = db_user.password  # 取该用户储存在数据库的密码
            password = lockpw(request.POST.get('password'))  # 取该用户页面输入的密码并加密
            if db_password == password:
                # 这里要给返回值设置cookie和session，所以需要把返回值先赋值
                response = HttpResponseRedirect('/shops/')  # 登陆成功跳转至首页
                response.set_cookie('username', db_user.username, max_age=3600)  # 设置寿命为1小时的cookie
                request.session['nickname'] = db_user.nickname  # 设置session
                return response
            else:  # 如果密码不一致
                result['data'] = '密码错误'
        else:  # 如果取出的用户为空
            result['data'] = '该商家不存在！！！'


    return render(request, 'shops/login.html', locals())




@cookieVerify
def goodsAdd(request):
    dotype = ""
    types = Types.objects.all()
    if request.method =="POST" and request.POST:
        g = Goods()
        g.goods_name = request.POST.get("goods_name")
        g.goods_id = request.POST.get("goods_num")
        g.goods_price = request.POST.get("goods_oprice")
        g.goods_now_price = request.POST.get("goods_xprice")
        g.goods_num = request.POST.get("goods_count")
        g.goods_description = request.POST.get("goods_method")
        g.goods_content = request.POST.get("goods_infro")
        g.taobao = request.POST.get("taobao")
        g.types_id = Types.objects.filter(id =request.POST.get('goods_type')).first().id
        g.seller_id = Seller.objects.filter(id=int(request.POST.get('goods_seller'))).first().id
        g.save()

        for i in request.FILES.getlist("goodsimages"):
            obj = FileUpload(i, is_randomname=False)
            path = MEDIA_ROOT
            if obj.upload(path) > 0:
                tupath = os.path.join("/upload", obj.file.name)
                img = Image()
                img.img_path = i.name
                img.img_label = request.POST.get('goods_name')
                img.goods = g
                img.save()

    return render(request, 'shops/goods_add.html', locals())
@cookieVerify
def goodsList(request):
    goods = Goods.objects.filter()
    return render(request, 'shops/goods_list.html', locals())


def lockpw(pw):
    md5 = hashlib.md5()
    md5.update(pw.encode())
    result = md5.hexdigest()
    return result


def loginout(request):
    response = HttpResponseRedirect('/shops/login/')
    response.delete_cookie('username')
    del request.session['nickname']
    return response

@cookieVerify
def goodstypeAdd(request):
    if request.method == 'POST' and request.POST:
        print(request.POST.get('typelable'))
        types = Types()
        types.label = request.POST.get('typelable')
        types.description = request.POST.get('typedescription')
        types.save()

    return render(request, 'shops/goods_typeadd.html', locals())

@cookieVerify
def goodchange(request,id):
    dotype = "change"
    type = Types.objects.all()
    g = Goods.objects.get(id=int(id))
    if request.method =="POST" and request.POST:
        g= Goods.objects.get(id=int(id))
        g.goods_name=request.POST.get("goods_name")
        g.goods_id = request.POST.get("goods_num")
        g.goods_price = request.POST.get("goods_oprice")
        g.goods_now_price = request.POST.get("goods_xprice")
        g.goods_num = request.POST.get("goods_count")
        g.goods_description = request.POST.get("goods_method")
        g.goods_content = request.POST.get("goods_infro")
        g.taobao  = request.POST.get("taobao")
        g.types_id = Types.objects.filter(id =request.POST.get('goods_type')).first().id
        g.seller_id = Seller.objects.filter(id=int(request.POST.get('goods_seller'))).first().id
        g.save()
        # for i in request.FILES.getlist("goodsimages"):
        #     img = Image.objects.get(goods=g)
        #     print()
        #     img.img_path = 'shops/images/goods/'+i.name
        #     img.img_label = request.POST.get('goodsname')
        #     img.goods = g
        #     img.save()
        #     path = os.path.join(MEDIA_ROOT,'shop/images/goods/{}'.format(i.name)).replace('\\','/')
        #     with open(path,"wb") as f:
        #         for j in i.chunks():
        #             f.write(j)
    return render(request,"shops/goods_add.html",locals())

@cookieVerify
def goodsDel(request,id):
    goods = Goods.objects.get(id=int(id))
    imgs = goods.image_set.filter(goods_id=int(id))  #获取商品的所有照片
    # for i in imgs:  #删除存在静态文件夹中的图片
    #     # os.remove(os.path.join(MEDIA_ROOT,str(i.img_path).replace('\\','/')))

    imgs.delete() #先删除外键表
    goods.delete()  # 再删除主键表数据
    return HttpResponseRedirect("/shops/goodsList/") #跳转到商品列表页



@cookieVerify
def goodsDetails(request,id):
    goods = Goods.objects.get(id=int(id)) #获取商品信息
    goodsImage = Image.objects.filter(goods=int(id)) #获取商品图片
    return render(request,'shops/goods_details.html',locals())


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