from django.db import models
from django.contrib.auth.models import User
# Create your models here.


class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    price = models.FloatField()
    thumbnail = models.CharField(max_length=200)
    discountPercentage = models.IntegerField()
    active = models.BooleanField()
    stock = models.IntegerField()
    updatedAt = models.DateTimeField(auto_now=True)
    createdAt = models.DateTimeField(auto_now_add=True)
    deleteAt = models.DateTimeField(auto_now=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return self.name


class Cart(models.Model):
    cart_id = models.CharField(
        max_length=255, unique=True)  # Trường cho Cart ID
    products = models.ManyToManyField(
        'Product', blank=True)  # Trường cho các sản phẩm
    # Trường cho người dùng
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)  # Thời gian tạo
    updated_at = models.DateTimeField(auto_now=True)  # Thời gian cập nhật

    def __str__(self):
        return self.cart_id  # Hiển thị Cart ID khi in ra


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name='items',
                             on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)


class Order(models.Model):
    name = models.CharField(max_length=200)  # Tên người đặt hàng
    phone = models.CharField(max_length=15)  # Số điện thoại
    address = models.CharField(max_length=255)  # Địa chỉ giao hàng
    user = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True)  # Người dùng (nếu có)
    pricePayment = models.FloatField()  # Tổng số tiền thanh toán
    # Liên kết với giỏ hàng
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)  # Ngày tạo đơn hàng
    updated_at = models.DateTimeField(auto_now=True)  # Ngày cập nhật đơn hàng

    def __str__(self):
        return f"Order {self.id} by {self.name}"


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order, related_name='order_items', on_delete=models.CASCADE)
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE)  # Sản phẩm đã đặt
    quantity = models.PositiveIntegerField(
        default=1)  # Số lượng sản phẩm trong đơn hàng

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"
