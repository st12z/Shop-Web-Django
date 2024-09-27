from django.urls import path
from . import views
urlpatterns = [
    path('', views.home, name='home'),
    path('detail-product/<str:pk>/',views.detailProduct,name='detail-product'),
    path('detail-cart',views.detailCart,name='detail-cart'),
    path('delete/<str:pk>/',views.deleteCart,name='delete'),
    path('buy-product/<str:pk>/',views.buyProduct,name='buy-product'),
    path('decrease-product/<str:pk>/',views.decreaseProduct,name='decrease-product'),
    path('increase-product/<str:pk>/',views.increaseProduct,name='increase-product'),
    path('check-out',views.checkOut,name='check-out'),
    path('detail-order',views.detailOrder,name='detail-order')
]
