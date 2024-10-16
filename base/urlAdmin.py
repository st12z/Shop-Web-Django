from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import viewsAdmin
urlpatterns = [
    path('',viewsAdmin.loginPage,name=""),
    path('home-admin/',viewsAdmin.home,name="home-admin"),
    path('dashboard/',viewsAdmin.dashBoard,name="dashboard"),
    path('register-admin/',viewsAdmin.registerPage,name='register-admin'),
    path('logout-admin/',viewsAdmin.logoutPage,name='logout-admin'),
    path('products/',viewsAdmin.products,name='products'),
    path('categories/',viewsAdmin.categories,name='categories'),
    path('delete-product/<str:pk>/',viewsAdmin.deleteProduct,name='delete-product'),
    path('delete-category/<str:pk>/',viewsAdmin.deleteCategory,name='delete-category'),
    path('edit-product/<str:pk>/',viewsAdmin.editProduct,name='edit-product'),
    path('edit-category/<str:pk>/',viewsAdmin.editCategory,name='edit-category'),
    path('create-product',viewsAdmin.createProduct,name='create-product'),
    path('create-category',viewsAdmin.createCategory,name='create-category'),
    path('orders',viewsAdmin.orders,name='orders'),
    path('edit-order/<str:pk>/',viewsAdmin.editOrder,name='edit-order')

]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)