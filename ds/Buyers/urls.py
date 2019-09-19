from django.conf.urls import url

from Buyers import views

urlpatterns = [
    url(r'^$',views.index,name='bindex'),
    url(r'^login/$',views.blogin,name='blogin'),
    url(r'^register/$',views.register,name='register'),
    url(r'^cart/$',views.cart,name='cart'),
    url(r'^addcart/(\d+)/$',views.addcart,name='addcart'),
    url(r'^delcart/(\d+)/$',views.delcart,name='delcart'),
    url(r'^products/(\d+)/$',views.products,name='products'),
    url(r'^order/$',views.order,name='order'),
    url(r'^pay/$',views.pay,name='pay'),
    url(r'^payverify/(\d+)/$',views.payverify,name='payverify'),
    url(r'^details/(\d+)/$',views.product_details,name='details'),
    url(r'^logout/$',views.blogout,name='blogout'),
]