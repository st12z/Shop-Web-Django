from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from .models import Product, Category, Comment, Cart, CartUser, CartItem, Order, OrderItem, User
from django.contrib import messages
from helper.getProductPage import getProductPage
from helper.generateString import generateString
from helper.getProductCart import getProductCart
from helper.getOrder import getOrder
from django.contrib.auth import authenticate, login, logout
from django.db.models import Q
from django.http import HttpResponse
import locale
from django.core.files.storage import FileSystemStorage
import os
# Create your views here.


def registerPage(request):
    if request.method == "POST":
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')

        # Kiểm tra xem username có rỗng không
        if not username:
            messages.error(request, 'Tên đăng nhập không được để trống!')
        # Kiểm tra nếu email đã tồn tại
        elif User.objects.filter(email=email).exists():
            messages.error(request, 'Email đã tồn tại!')
        else:
            user = User(username=username, email=email)
            user.role = True
            user.set_password(password)  # Mã hóa mật khẩu
            user.save()  # Lưu tài khoản mới
            messages.success(request, "Đăng kí thành công!")
            # Chuyển hướng đến trang đăng nhập sau khi đăng ký thành công
            return redirect('')
    return render(request, 'base/admin/register-page.html')


def loginPage(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        # Kiểm tra xem email có tồn tại không
        user = User.objects.filter(email=email).first()
        if user is None:
            messages.error(request, 'Email không tồn tại!')
        else:
            user = authenticate(request, email=email, password=password)
            if user is not None:
                login(request, user)
                return redirect('dashboard')
            else:
                messages.error(request, 'Sai mật khẩu!')
    return render(request, 'base/admin/login-page.html')


def logoutPage(request):
    logout(request)
    return redirect('')


def home(request):
    if not request.user.is_authenticated:
        return redirect('')
    return render(request, 'base/admin/home.html')


def dashBoard(request):
    if not request.user.is_authenticated:
        return redirect('')
    cartList = Cart.objects.all()
    productsSold = {}

    for cart in cartList:
        orders = Order.objects.filter(cart=cart)
        for order in orders:
            orderItems = OrderItem.objects.filter(order=order)
            for item in orderItems:
                priceNew = int(item.product.price *
                               (100-item.product.discountPercentage)/100)
                item.product.price = "{:,.0f}".format(item.product.price)
                item.product.priceNew = "{:,.0f}".format(priceNew)
                # Hoặc sử dụng item.product.name nếu tên sản phẩm là duy nhất
                product_key = item.product.id
                if product_key not in productsSold:
                    # Khởi tạo một từ điển cho sản phẩm mới
                    productsSold[product_key] = {
                        'name': item.product.name,
                        'quantity': item.quantity,
                        'price': item.product.price,  # Đảm bảo đây là số
                        'priceNew': item.product.priceNew,
                        'thumbnail': item.product.thumbnail
                    }
                else:
                    # Cập nhật số lượng nếu sản phẩm đã tồn tại
                    productsSold[product_key]['quantity'] += item.quantity

                # Tính toán giá mới
                # Đảm bảo rằng giá vẫn là số trước khi định dạng
                # Định dạng giá

    sorted_products = sorted(productsSold.items(
    ), key=lambda item: item[1]['quantity'], reverse=True)
    top_5_products = sorted_products[:5]

# Tạo một mảng productsSold mới để chứa thông tin
    productsSold = []

    # Thêm thông tin về 5 sản phẩm vào mảng productsSold
    for item, details in top_5_products:
        productsSold.append({
            'name': details['name'],
            'quantity': details['quantity'],
            'price': details['price'],
            'priceNew': details['priceNew'],
            'thumbnail': details['thumbnail']
        })
    print(productsSold)
    context = {"productsSold": productsSold, 'page': 'dashboard'}
    return render(request, 'base/admin/dashboard.html', context)


def products(request):
    if not request.user.is_authenticated:
        return redirect('')
    page = 'products'
    products = Product.objects.filter(deleted=False).order_by('-createdAt')
    currentPage = request.GET.get('page', '1')
    itemPerPage = 4
    countPage = (len(products) + itemPerPage - 1) // itemPerPage  # Số trang
    currentPage = int(currentPage)
    begin = itemPerPage * (currentPage - 1)
    end = itemPerPage * currentPage if itemPerPage * \
        currentPage < len(products) else len(products)
    products = products[begin:end]  # Lấy sản phẩm theo trang
    for product in products:
        priceNew = int(product.price*(100-product.discountPercentage)/100)
        product.price = "{:,.0f}".format(product.price)
        product.priceNew = "{:,.0f}".format(priceNew)
    context = {'products': products,
               'lastPage': countPage,
               'currentPage': currentPage,
               'countPage': range(1, countPage + 1),
               'firstPage': 1,
               'page': 'products'}
    return render(request, 'base/admin/products.html', context)


def deleteProduct(request, pk):
    if not request.user.is_authenticated:
        redirect('')
    product = Product.objects.get(id=pk)
    product.deleted = True
    product.save()
    return redirect('products')


def editProduct(request, pk):
    if not request.user.is_authenticated:
        return redirect('')
    product = Product.objects.get(id=pk)
    if request.method == "POST":
        price = request.POST.get('price')
        discountPercentage = request.POST.get('discountPercentage')
        stock = request.POST.get('stock')
        print("Price:", price)
        print("Discount:", discountPercentage)
        print("Stock:", stock)
        if price is not None:
            product.price = float(price)
        if discountPercentage is not None:
            product.discountPercentage = int(discountPercentage)
        if stock is not None:
            product.stock = int(stock)
        product.save()
        return redirect('products')
    context = {'product': product}
    return render(request, 'base/admin/edit-product.html', context)


def createProduct(request):
    if not request.user.is_authenticated:
        return redirect('')
    if request.method == 'POST':
        name = request.POST.get('name')
        price = float(request.POST.get('price'))
        discount_percentage = int(request.POST.get('discountPercentage'))
        description = request.POST.get("description")
        stock = int(request.POST.get('stock'))
        category_id = int(request.POST.get('category'))
        uploaded_file = request.FILES.get(
            'file')  # Lấy tệp tin từ request.FILES

        # Kiểm tra xem tệp tin có được tải lên không
        if uploaded_file:
            # Sử dụng FileSystemStorage để lưu tệp
            fs = FileSystemStorage(location='static/client/images')
            # Lưu tệp và lấy tên tệp
            filename = fs.save(uploaded_file.name, uploaded_file)
            # Tạo đường dẫn tương đối cho thumbnail
            thumbnail_path = f"images/{filename}"

            # Lấy đối tượng danh mục
            category = Category.objects.get(id=category_id)

            # Tạo sản phẩm mới
            product = Product(
                name=name,
                price=price,
                discountPercentage=discount_percentage,
                description=description,
                stock=stock,
                category=category,
                thumbnail=thumbnail_path,  # Lưu đường dẫn ảnh vào thumbnail
                active=True,  # Giả sử sản phẩm này sẽ được kích hoạt mặc định
                deleted=False  # Giả sử sản phẩm này chưa bị xoá
            )
            product.save()
            return redirect("products")
    categories = Category.objects.all()
    context = {'categories': categories}
    return render(request, 'base/admin/create-product.html', context)
def categories(request):
    categories=Category.objects.filter(deleted=False)
    context={'categories':categories,'page':'categories'}
    return render(request,'base/admin/category.html',context)

def editCategory(request,pk):
    if not request.user.is_authenticated:
        return redirect('')
    category=Category.objects.get(id=pk)
    if request.method=='POST':
        name=request.POST.get('name')
        description=request.POST.get('description')
        if name is not None:
            category.name=name
        if description is not None:
            category.description=description
        category.save()
        return redirect("categories")
    context={'category':category}
    return render(request,'base/admin/edit-category.html',context)
def deleteCategory(request,pk):
    category=Category.objects.get(id=pk)
    products=Product.objects.filter(category=category)
    for product in products:
        product.deleted=True
        product.save()
    category.deleted=True
    category.save()
    return redirect("categories")
def createCategory(request):
    if not request.user.is_authenticated:
        return redirect('')
    if request.method=='POST':
        name=request.POST.get('name')
        description=request.POST.get('description')
        category=Category.objects.create(
            name=name,
            description=description
        )
        return redirect("categories")
    return render(request,'base/admin/create-category.html')