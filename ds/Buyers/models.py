from django.db import models

# Create your models here.
class Buyer(models.Model):
    username = models.CharField(max_length = 32)
    email = models.EmailField(blank=True, null=True)
    password = models.CharField(max_length = 32)
    signature = models.CharField(max_length=200, blank=True, null=True)
    portrait = models.CharField(max_length=100, blank=True, null=True)
    isactive = models.IntegerField(blank=True, null=True,default=0)

class Address(models.Model):
    address = models.TextField()
    phone = models.CharField(max_length = 32)
    username = models.CharField(max_length = 32)
    buyer = models.ForeignKey('Buyer',on_delete = models.DO_NOTHING)
    num = models.IntegerField(default=0)

class EmailValid(models.Model):
    value = models.CharField(max_length = 32)
    email_address = models.EmailField()
    times = models.DateTimeField()

class BuyCar(models.Model):
    goods_id = models.CharField(max_length=32)
    goods_name = models.CharField(max_length=32)
    goods_price = models.FloatField()
    goods_picture = models.ImageField(upload_to="image")
    goods_num = models.IntegerField()
    user = models.ForeignKey('Buyer', on_delete=models.DO_NOTHING)


class Order(models.Model):
    order_num = models.CharField(max_length=32)
    order_time = models.DateTimeField(auto_now=True)
    order_statue = models.CharField(max_length=32)
    total = models.FloatField()
    user = models.ForeignKey('Buyer',on_delete=models.CASCADE)
    order_address = models.ForeignKey('Address',on_delete=models.CASCADE)


class OrderGoods(models.Model):
    good_id = models.IntegerField()
    good_name = models.CharField(max_length=32)
    good_price = models.FloatField()
    good_num = models.IntegerField()
    goods_picture = models.ImageField()
    order = models.ForeignKey('Order',on_delete=models.CASCADE)