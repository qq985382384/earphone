# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from __future__ import unicode_literals

from django.db import models


class BuyersAddress(models.Model):
    address = models.TextField()
    phone = models.CharField(max_length=32)
    username = models.CharField(max_length=32)
    buyer = models.ForeignKey('BuyersBuyer', models.DO_NOTHING, blank=True, null=True)
    num = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Buyers_address'


class BuyersBuycar(models.Model):
    goods_id = models.CharField(max_length=32)
    goods_name = models.CharField(max_length=32)
    goods_price = models.FloatField()
    goods_picture = models.CharField(max_length=100)
    goods_num = models.IntegerField()
    user = models.ForeignKey('BuyersBuyer', models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Buyers_buycar'


class BuyersBuyer(models.Model):
    username = models.CharField(max_length=32)
    email = models.CharField(max_length=254, blank=True, null=True)
    password = models.CharField(max_length=32)
    isactive = models.IntegerField(blank=True, null=True)
    portrait = models.CharField(max_length=100, blank=True, null=True)
    signature = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Buyers_buyer'


class BuyersEmailvalid(models.Model):
    value = models.CharField(max_length=32)
    email_address = models.CharField(max_length=254)
    times = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'Buyers_emailvalid'


class BuyersOrder(models.Model):
    order_num = models.CharField(max_length=32)
    order_time = models.DateTimeField()
    order_statue = models.CharField(max_length=32)
    total = models.FloatField()
    order_address_id = models.IntegerField(blank=True, null=True)
    user_id = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Buyers_order'


class BuyersOrdergoods(models.Model):
    good_id = models.IntegerField()
    good_name = models.CharField(max_length=32)
    good_price = models.FloatField()
    good_num = models.IntegerField()
    goods_picture = models.CharField(max_length=100)
    order = models.ForeignKey(BuyersOrder, models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Buyers_ordergoods'


class ShopGoods(models.Model):
    goods_name = models.CharField(max_length=32)
    goods_id = models.CharField(max_length=32)
    goods_price = models.FloatField()
    goods_now_price = models.FloatField()
    goods_num = models.IntegerField()
    goods_description = models.TextField()
    goods_content = models.TextField()
    seller = models.ForeignKey('ShopSeller', models.DO_NOTHING, blank=True, null=True)
    types = models.ForeignKey('ShopTypes', models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Shop_goods'


class ShopImage(models.Model):
    img_path = models.CharField(max_length=100)
    img_label = models.CharField(max_length=32)
    goods = models.ForeignKey(ShopGoods, models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Shop_image'


class ShopSeller(models.Model):
    username = models.CharField(max_length=32)
    phone = models.CharField(max_length=32)
    email = models.CharField(max_length=254)
    password = models.CharField(max_length=32)
    nickname = models.CharField(max_length=32)
    photo = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'Shop_seller'


class ShopTypes(models.Model):
    label = models.CharField(max_length=32)
    description = models.TextField()

    class Meta:
        managed = False
        db_table = 'Shop_types'


class AuthGroup(models.Model):
    name = models.CharField(unique=True, max_length=80)

    class Meta:
        managed = False
        db_table = 'auth_group'


class AuthGroupPermissions(models.Model):
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)
    permission = models.ForeignKey('AuthPermission', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_group_permissions'
        unique_together = (('group', 'permission'),)


class AuthPermission(models.Model):
    name = models.CharField(max_length=255)
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING)
    codename = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'auth_permission'
        unique_together = (('content_type', 'codename'),)


class AuthUser(models.Model):
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.IntegerField()
    username = models.CharField(unique=True, max_length=150)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    email = models.CharField(max_length=254)
    is_staff = models.IntegerField()
    is_active = models.IntegerField()
    date_joined = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'auth_user'


class AuthUserGroups(models.Model):
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_groups'
        unique_together = (('user', 'group'),)


class AuthUserUserPermissions(models.Model):
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    permission = models.ForeignKey(AuthPermission, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_user_permissions'
        unique_together = (('user', 'permission'),)


class DjangoAdminLog(models.Model):
    action_time = models.DateTimeField()
    object_id = models.TextField(blank=True, null=True)
    object_repr = models.CharField(max_length=200)
    action_flag = models.SmallIntegerField()
    change_message = models.TextField()
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING, blank=True, null=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'django_admin_log'


class DjangoContentType(models.Model):
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'django_content_type'
        unique_together = (('app_label', 'model'),)


class DjangoMigrations(models.Model):
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField()
    expire_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_session'
