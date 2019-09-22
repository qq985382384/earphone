from django.conf.urls import url

from Buyers import views

urlpatterns = [
    url(r'^$', views.index, name='bindex'),
    url(r'^login/$', views.blogin, name='blogin'),
    url(r'^register/$', views.register, name='register'),
    url(r'^cart/$', views.cart, name='cart'),
    url(r'^addcart/(\d+)/$', views.addcart, name='addcart'),
    url(r'^delcart/(\d+)/$', views.delcart, name='delcart'),
    url(r'^products/(\d+)/$', views.products, name='products'),
    url(r'^order/$', views.order, name='order'),
    url(r'^pay/$', views.pay, name='pay'),
    url(r'^payverify/(\d+)/$', views.payverify, name='payverify'),
    url(r'^checkpay/$', views.checkpay, name='checkpay'),
    url(r'^details/(\d+)/$', views.product_details, name='details'),
    url(r'^logout/$', views.blogout, name='blogout'),
    url(r'^person_order2/$', views.person_order2, name='person_order2'),
    url(r'^ordergoods2/(\d+)/$',views.ordergoods2,name='ordergoods2'),

    url(r'^person/$', views.person, name='person'),
    url(r'^person_address/(\d+)$', views.address, name='person_address'),
    url(r'^address_add/(\d+)$', views.address_add, name='address_add'),
    url(r'^address_del/(\d+)$', views.address_del, name='address_del'),
    url(r'^address_change/(\d+)$', views.address_change, name='address_change'),
    url(r'^person_mima/(\d+)$', views.person_mima, name='person_mima'),
    url(r'^person_order/(\d+)$', views.person_order, name='person_order'),
    url(r'^ordergoods/(\d+)$', views.ordergoods, name='ordergoods'),
    url(r'^shouhuo/(\d+)$', views.shouhuo, name='shouhuo'),
    url(r'^findpassword/$', views.findpassword, name='findpassword'),


]
