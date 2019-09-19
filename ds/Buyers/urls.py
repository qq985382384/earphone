from django.conf.urls import url

from Buyers import views

urlpatterns = [
    url(r'^$',views.index,name='bindex'),
    url(r'^login/$',views.blogin,name='blogin'),
    url(r'^register/$',views.register,name='register'),
    url(r'^cart/$',views.cart,name='cart'),
    url(r'^products/(\d+)$',views.products,name='products'),
    url(r'^details/$',views.product_details,name='detail'),
    url(r'^logout/$',views.blogout,name='blogout'),
]