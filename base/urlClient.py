from django.urls import path
from . import viewsClient
urlpatterns = [
    # start url client
    path('', viewsClient.home, name='home'),
    path('detail-product/<str:pk>/',viewsClient.detailProduct,name='detail-product'),
    path('detail-cart',viewsClient.detailCart,name='detail-cart'),
    path('delete-cart/<str:pk>/',viewsClient.deleteCart,name='delete-cart'),
    path('buy-product/<str:pk>/',viewsClient.buyProduct,name='buy-product'),
    path('decrease-product/<str:pk>/',viewsClient.decreaseProduct,name='decrease-product'),
    path('increase-product/<str:pk>/',viewsClient.increaseProduct,name='increase-product'),
    path('check-out',viewsClient.checkOut,name='check-out'),
    path('detail-order',viewsClient.detailOrder,name='detail-order'),
    path('register',viewsClient.registerPage,name='register'),
    path('login',viewsClient.loginPage,name='login'),
    path('logout',viewsClient.logoutUser,name='logout'),
    path('delete-comment/<str:pk>/',viewsClient.deleteComment,name='delete-comment')
    
    # end url client

]
