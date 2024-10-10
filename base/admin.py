from django.contrib import admin

# Register your models here
from .models import Product,CartUser,Category,Comment,Cart,CartItem,Order,OrderItem,User
admin.site.register(Product)
admin.site.register(Category)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(User)
admin.site.register(Comment)
admin.site.register(CartUser)
