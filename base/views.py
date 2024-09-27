from django.shortcuts import render, redirect
from .models import Product, Category, Cart, CartItem, Order, OrderItem
from helper.getProductPage import getProductPage
from helper.generateString import generateString
from helper.getProductCart import getProductCart
from helper.getOrder import getOrder
from django.db.models import Q
from django.http import HttpResponse
import locale
# Create your views here.


def home(request):
    # Lấy cookies từ request
    cookies = request.COOKIES
    cartId = cookies.get("cartId")

    # Nếu không có cartId, tạo một giá trị mới và thiết lập cookie
    if not cartId:
        cartId = generateString(10)
    cart, created = Cart.objects.get_or_create(
        user=request.user, cart_id=cartId)
    # Các biến GET
    keyword = request.GET.get('keyword', '')
    currentPage = request.GET.get('page', '1')  # Giá trị mặc định là 1
    sortKey = request.GET.get('sortKey', '')
    sortValue = request.GET.get('sortValue', '')
    sort_order = '' if sortValue == 'asc' else '-'
    priceOrder = request.GET.get('priceOrder', '')

    quantityProducts = getProductCart(request)
    quantityOrder = getOrder(request)
    # Xử lý giá cả
    if priceOrder:
        if priceOrder == '<6':
            min_price, max_price = 0, 6 * 1e6 - 1
        elif priceOrder == '6-10':
            min_price, max_price = 6 * 1e6, 10 * 1e6
        elif priceOrder == '11-15':
            min_price, max_price = 11 * 1e6, 15 * 1e6
        elif priceOrder == '>15':
            min_price, max_price = 15 * 1e6 + 1, float('inf')
    else:
        priceOrder = ""
        min_price, max_price = 0, float('inf')

    # Lọc sản phẩm
    products = Product.objects.filter(
        Q(name__icontains=keyword) &
        Q(price__gte=min_price) &
        Q(price__lte=max_price)
    )
    if sortKey:
        products = products.order_by(f"{sort_order}{sortKey}")

    # Kiểm tra sản phẩm
    if not products.exists():
        notification = "Không tìm thấy sản phẩm nào."
    else:
        notification = ""
    # Xử lý phân trang
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
    # Cập nhật context
    context = {
        'products': products,
        'countPage': range(1, countPage + 1),
        'firstPage': 1,
        'lastPage': countPage,
        'currentPage': currentPage,
        'notification': notification,
        'keyword': keyword,
        'sortOrder': f"{sortKey}-{sortValue}" if sortKey and sortValue else "All",
        'priceOrder': priceOrder,
        'quantityProducts': quantityProducts,
        'cartId': cartId,
        'quantityOrders': quantityOrder
    }
    # Render template và thiết lập cookie
    response = render(request, 'base/home.html', context)
    response.set_cookie('cartId', cartId, max_age=7 *
                        24*60*60)  # Thiết lập cookie
    return response


def detailProduct(request, pk):
    quantityOrder = getOrder(request)
    quantityProducts = getProductCart(request)
    product = Product.objects.get(id=pk)
    priceNew = int(product.price*(100-product.discountPercentage)/100)
    product.price = "{:,.0f}".format(int(product.price)).replace(',', '.')
    product.priceNew = "{:,.0f}".format(int(priceNew)).replace(',', '.')
    context = {'product': product, 'quantityProducts': quantityProducts,
               'quantityOrders': quantityOrder}
    return render(request, 'base/detail.html', context)


def buyProduct(request, pk):
    product = Product.objects.get(id=pk)
    cookies = request.COOKIES
    cartId = cookies.get("cartId")
    cart = Cart.objects.get(cart_id=cartId)
    cart_items, created = CartItem.objects.get_or_create(
        cart=cart, product=product)
    cart.products.add(product)
    if not created:
        cart_items.quantity += 1
    cart_items.save()
    return redirect('home')


def detailCart(request):
    quantityOrder = getOrder(request)
    quantityProducts = getProductCart(request)
    cart_id = request.COOKIES.get('cartId')
    cart = Cart.objects.get(cart_id=cart_id)
    cart_items = CartItem.objects.filter(cart=cart)
    products = []
    totalPayment = 0
    for item in cart_items:
        priceNew = int(item.product.price *
                       (100-item.product.discountPercentage)/100)
        totalPrice = priceNew*item.quantity
        objectProducts = {
            'product': item.product,
            'quantity': item.quantity,
            'totalPrice': totalPrice,
            'quantityOrders': quantityOrder

        }
        objectProducts['product'].price = "{:,.0f}".format(
            objectProducts['product'].price)
        objectProducts['product'].priceNew = "{:,.0f}".format(priceNew)
        totalPayment += objectProducts['totalPrice']
        objectProducts['totalPrice'] = "{:,.0f}".format(
            objectProducts['totalPrice'])
        products.append(objectProducts)
    totalPayment = "{:,.0f}".format(totalPayment)
    context = {'products': products, 'totalPayment': totalPayment,
               'quantityProducts': quantityProducts, 'quantityOrders': quantityOrder}
    return render(request, 'base/detail-cart.html', context)


def decreaseProduct(request, pk):
    cart_id = request.COOKIES.get('cartId')
    cart = Cart.objects.get(cart_id=cart_id)
    product = Product.objects.get(id=pk)
    cart_items = CartItem.objects.get(cart=cart, product=product)
    if cart_items.quantity > 1:
        cart_items.quantity -= 1
        cart_items.save()
    else:
        cart_items.delete()

    return redirect('detail-cart')


def increaseProduct(request, pk):
    cart_id = request.COOKIES.get('cartId')
    cart = Cart.objects.get(cart_id=cart_id)
    product = Product.objects.get(id=pk)
    cart_items = CartItem.objects.get(cart=cart, product=product)

    cart_items.quantity += 1
    cart_items.save()

    return redirect('detail-cart')


def deleteCart(request, pk):
    cart_id = request.COOKIES.get('cartId')
    cart = Cart.objects.get(cart_id=cart_id)
    product = Product.objects.get(id=pk)
    cart_items = CartItem.objects.get(cart=cart, product=product)
    cart_items.delete()
    return redirect('detail-cart')


def checkOut(request):
    quantityOrder = getOrder(request)
    quantityProducts = getProductCart(request)
    cart_id = request.COOKIES.get('cartId')
    cart = Cart.objects.get(cart_id=cart_id)
    cart_items = CartItem.objects.filter(cart=cart)
    products = []
    totalPayment = 0
    for item in cart_items:
        priceNew = int(item.product.price *
                       (100-item.product.discountPercentage)/100)
        totalPrice = priceNew*item.quantity
        objectProducts = {
            'product': item.product,
            'quantity': item.quantity,
            'totalPrice': totalPrice,

        }
        objectProducts['product'].price = "{:,.0f}".format(
            objectProducts['product'].price)
        objectProducts['product'].priceNew = "{:,.0f}".format(priceNew)
        totalPayment += objectProducts['totalPrice']
        objectProducts['totalPrice'] = "{:,.0f}".format(
            objectProducts['totalPrice'])
        products.append(objectProducts)
    pricePayment = totalPayment
    totalPayment = "{:,.0f}".format(totalPayment)
    context = {'products': products, 'totalPayment': totalPayment,
               'quantityProducts': quantityProducts, 'quantityOrders': quantityOrder}
    if request.method == "POST":
        cart_id = request.COOKIES.get('cartId')
        cart = Cart.objects.get(cart_id=cart_id)
        orderObject = Order.objects.create(
            user=request.user,
            cart=cart,
            name=request.POST.get('name'),
            phone=request.POST.get('phone'),
            address=request.POST.get('address'),
            pricePayment=pricePayment,
        )
        for item in cart_items:
            orderItem, created = OrderItem.objects.get_or_create(
                order=orderObject, product=item.product)
            orderItem.quantity = item.quantity
            orderItem.save()
        cart_items.delete()
        return redirect("check-out")
    return render(request, 'base/check-out.html', context)


def detailOrder(request):
    quantityOrder = getOrder(request)
    cart_id = request.COOKIES.get('cartId')
    quantityProducts = getProductCart(request)
    cart = Cart.objects.get(cart_id=cart_id)
    orders = Order.objects.filter(cart=cart)
    infoOrders = []
    for order in orders:
        infoItem = []
        infoObject = {
            'name': order.name,
            'phone': order.phone,
            'address': order.address,
        }
        orderItems = OrderItem.objects.filter(order=order)
        totalPayment = 0
        for item in orderItems:
            priceNew = int(item.product.price *
                           (100-item.product.discountPercentage)/100)
            totalPrice = priceNew*item.quantity
            objectProducts = {
                'product': item.product,
                'quantity': item.quantity,
                'totalPrice': totalPrice,

            }
            objectProducts['product'].price = "{:,.0f}".format(
                objectProducts['product'].price)
            objectProducts['product'].priceNew = "{:,.0f}".format(priceNew)
            totalPayment += objectProducts['totalPrice']
            objectProducts['totalPrice'] = "{:,.0f}".format(
                objectProducts['totalPrice'])
            infoItem.append(objectProducts)
        totalPayment = "{:,.0f}".format(totalPayment)
        infoOrder = {
            'infoCustomer': infoObject,
            'infoItems': infoItem,
            'totalPayment': totalPayment
        }
        infoOrders.append(infoOrder)
    context = {
        'quantityProducts': quantityProducts,
        'infoOrders': infoOrders,
        'quantityOrders': quantityOrder}
    return render(request, 'base/detail-order.html', context)
