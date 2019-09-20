from django.conf.urls import url

from Shop import views


urlpatterns = [
    url(r'^$',views.index,name='index'),
    url(r'^login/$', views.login, name='login'),
    url(r'^goodsAdd/$', views.goodsAdd, name='goodadd'),
    url(r'^goodsList/$', views.goodsList, name='goodlist'),
    url(r'^loginout/$', views.loginout, name='loginout'),
    url(r'^goodstypeAdd/$', views.goodstypeAdd, name='typeadd'),
    url(r'^goodschange/(\d+)$', views.goodchange, name='goodchange'),
    url(r'^goodsdel/(\d+)$', views.goodsDel, name='del'),
    url(r'^goodsDetail/(\d+)$', views.goodsDetails, name='details'),
    url(r'^user/$', views.user, name='user'),
    url(r'^userlock/(\d+)l9$', views.user, name='user'),


]