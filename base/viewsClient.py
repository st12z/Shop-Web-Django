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
from helper.sendEmail import send_reset_email
from django.http import JsonResponse
import json
import locale
# Create your views here.


def registerPage(request):
    cartId = request.COOKIES.get("cartId")
    if not cartId:
        cartId = generateString(10)
    quantityProducts = getProductCart(cartId)
    if request.method == "POST":
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        # Kiểm tra xem username có rỗng không
        if len(password1) < 8 or len(password2) < 8:
            messages.error(request, 'Mật khẩu phải có ít nhất 8 ký tự.')
            return render(request, 'base/client/registerPage.html')
        if not username:
            messages.error(request, 'Tên đăng nhập không được để trống!')
        # Kiểm tra nếu email đã tồn tại
        elif User.objects.filter(email=email).exists():
            messages.error(request, 'Email đã tồn tại!')
        elif password1!=password2:
            messages.error(request, 'Nhập lại mật khảu!')
        else:
            user = User(username=username, email=email)
            user.set_password(password1)  # Mã hóa mật khẩu
            user.save()  # Lưu tài khoản mới
            messages.success(request, "Đăng kí thành công!")
            # Chuyển hướng đến trang đăng nhập sau khi đăng ký thành công
            return redirect('login')
    context = {'quantityProducts': quantityProducts,
               'pageTitle': 'Trang đăng kí'}
    return render(request, 'base/client/registerPage.html', context)


def loginPage(request):
    cartId = request.COOKIES.get("cartId")
    quantityProducts = 0
    if not cartId:
        cartId = generateString(10)
    else:
        quantityProducts = getProductCart(cartId)
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
                cartUser, created = CartUser.objects.get_or_create(user=user)
                if created:
                    cartUser.cart_id = cartId
                    cartUser.save()
                else:
                    cartId = cartUser.cart_id
                response = redirect("home")
                response.set_cookie('cartId', cartId, max_age=7 *
                                    24*60*60)  # Thiết lập cookie
                login(request, user)
                return response
            else:
                messages.error(request, 'Sai mật khẩu!')
    context = {'quantityProducts': quantityProducts,
               'pageTitle': 'Trang đăng nhập'}

    response = render(request, 'base/client/loginPage.html', context)
    response.set_cookie('cartId', cartId, max_age=7 *
                        24*60*60)  # Thiết lập cookie
    return response


def logoutUser(request):

    # Tạo phản hồi redirect tới trang đăng nhập
    response = redirect("login")
    response.delete_cookie("cartId")
    # Đăng xuất người dùng
    logout(request)

    # Thiết lập lại cookie carId với giá trị rỗng và thời gian hết hạn
    response.set_cookie(
        'carId', '', expires='Thu, 01 Jan 1970 00:00:00 GMT', path='/')

    return response


def home(request):

    cartId = request.COOKIES.get("cartId")
    if not cartId:
        cartId = generateString(10)
    cart, created = Cart.objects.get_or_create(cart_id=cartId)
    # Các biến GET
    keyword = request.GET.get('keyword', '')
    currentPage = request.GET.get('page', '1')  # Giá trị mặc định là 1
    sortKey = request.GET.get('sortKey', '')
    sortValue = request.GET.get('sortValue', '')
    sort_order = '' if sortValue == 'asc' else '-'
    priceOrder = request.GET.get('priceOrder', '')
    category = request.GET.get('category', '')
    quantityProducts = getProductCart(cartId)
    quantityOrder = 0
    if request.user.is_authenticated:
        quantityOrder = getOrder(cartId)
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
        Q(deleted=False) &
        Q(name__icontains=keyword) &
        Q(category__name__icontains=category) &
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
    itemPerPage = 6
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
    # Category
    categories = Category.objects.all()

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
        'quantityOrders': quantityOrder,
        'pageTitle': 'Trang chủ',
        'categories': categories,
        'categoryOption': category,
    }
    # Render template và thiết lập cookie
    response = render(request, 'base/client/home.html', context)
    response.set_cookie('cartId', cartId, max_age=7 *
                        24*60*60)  # Thiết lập cookie

    return response


def detailProduct(request, pk):
    cookies = request.COOKIES
    cartId = cookies.get("cartId")
    if request.user.is_authenticated:
        quantityOrder = getOrder(cartId)
    else:
        quantityOrder = 0

    quantityProducts = getProductCart(cartId)

    product = Product.objects.get(id=pk)
    priceNew = int(product.price*(100-product.discountPercentage)/100)
    product.price = "{:,.0f}".format(int(product.price)).replace(',', '.')
    product.priceNew = "{:,.0f}".format(int(priceNew)).replace(',', '.')
    try:
        comments = Comment.objects.filter(product=product)
    except:
        comments = []
    context = {'product': product, 'quantityProducts': quantityProducts,
               'quantityOrders': quantityOrder, 'comments': comments, 'pageTitle': 'Trang chi tiết sản phẩm'}
    if request.method == "POST":
        if not request.user.is_authenticated:
            return redirect('login')
        objectComment = Comment.objects.create(
            user=request.user,
            content=request.POST.get("content"),
            product=product
        )
        return redirect('detail-product', pk)
    return render(request, 'base/client/detail.html', context)


def addProductToCart(request):
    if request.method == 'POST':
        try:
            # Kiểm tra dữ liệu POST nhận được
            data = json.loads(request.body)
            print("Data received:", data)

            product_id = data.get('productId')
            print("Product ID:", product_id)

            # Kiểm tra nếu product_id có tồn tại và hợp lệ
            if not product_id:
                return JsonResponse({'error': 'Product ID is missing'}, status=400)

            # Lấy sản phẩm từ cơ sở dữ liệu
            product = Product.objects.get(id=product_id)
            print("Product:", product)

            # Lấy cart từ cookie
            cookies = request.COOKIES
            cartId = cookies.get("cartId")
            if not cartId:
                return JsonResponse({'error': 'Cart ID is missing'}, status=400)

            # Lấy giỏ hàng
            cart = Cart.objects.get(cart_id=cartId)
            print("Cart:", cart)

            # Tạo hoặc lấy CartItem
            cart_item, created = CartItem.objects.get_or_create(
                cart=cart, product=product)
            if not created:
                cart_item.quantity += 1
            cart_item.save()

            # Tính tổng số lượng sản phẩm trong giỏ hàng
            total_quantity = sum(
                item.quantity for item in CartItem.objects.filter(cart=cart))
            print("Total quantity in cart:", total_quantity)

            # Trả về JSON response
            return JsonResponse({'total_quantity': total_quantity})

        except Product.DoesNotExist:
            return JsonResponse({'error': 'Product does not exist'}, status=404)
        except Exception as e:
            print("Error:", e)
            return JsonResponse({'error': 'Something went wrong'}, status=500)

    return JsonResponse({'error': 'Invalid request method'}, status=400)


def detailCart(request):
    cookies = request.COOKIES
    cartId = cookies.get("cartId")

    if request.user.is_authenticated:
        quantityOrder = getOrder(cartId)
    else:
        quantityOrder = 0
    quantityProducts = getProductCart(cartId)
    cart_id = request.COOKIES.get('cartId')
    try:
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
        totalPayment = "{:,.0f}".format(totalPayment)
        context = {'products': products, 'totalPayment': totalPayment,
                   'quantityProducts': quantityProducts, 'quantityOrders': quantityOrder, 'pageTitle': 'Trang giỏ hàng'}
    except:
        notification = "Giỏ hàng trống!"
        context = {'notification': notification,
                   'pageTitle': 'Trang giỏ hàng '}
    return render(request, 'base/client/detail-cart.html', context)


def decreaseProduct(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        product_id = data.get('productId')
        product = Product.objects.get(id=product_id)
        cookies = request.COOKIES
        cartId = cookies.get("cartId")
        cart = Cart.objects.get(cart_id=cartId)
        cart_items = CartItem.objects.filter(cart=cart)
        cart_item = CartItem.objects.get(cart=cart, product=product)
        print(cart_item)
        quantity = 0
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            quantity = cart_item.quantity
        cart_item.save()
        total_price = "{:,.0f}".format(int(quantity*(cart_item.product.price)*(1-cart_item.product.discountPercentage/100)))
        total_quantity = sum(
        item.quantity for item in CartItem.objects.filter(cart=cart))
        totalPayment=0
        for item in cart_items:
            totalItem=int(quantity*(item.product.price)*(1-item.product.discountPercentage/100))
            totalPayment+=totalItem
        totalPayment = "{:,.0f}".format(totalPayment)
        total_quantity = sum(
            item.quantity for item in CartItem.objects.filter(cart=cart))
        print("Total quantity in cart:", total_quantity)
        # Trả về JSON response
        return JsonResponse({'quantity': quantity, 'total_quantity': total_quantity, 'total_price': total_price,'total_payment':totalPayment})


def increaseProduct(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            product_id = data.get('productId')
            product = Product.objects.get(id=product_id)
            cookies = request.COOKIES
            cartId = cookies.get("cartId")
            cart = Cart.objects.get(cart_id=cartId)
            cart_items = CartItem.objects.filter(cart=cart)
            cart_item, created = CartItem.objects.get_or_create(
                cart=cart, product=product)
            if not created:
                cart_item.quantity += 1
            cart_item.save()
            quantity = cart_item.quantity
            total_price = "{:,.0f}".format(int(quantity*(cart_item.product.price)*(1-cart_item.product.discountPercentage/100)))
            total_quantity = sum(
            item.quantity for item in CartItem.objects.filter(cart=cart))
            totalPayment=0
            for item in cart_items:
                totalItem=int(quantity*(item.product.price)*(1-item.product.discountPercentage/100))
                totalPayment+=totalItem
            totalPayment = "{:,.0f}".format(totalPayment)
            total_quantity = sum(
                item.quantity for item in CartItem.objects.filter(cart=cart))
            print("Total quantity in cart:", total_quantity)
            # Trả về JSON response
            return JsonResponse({'quantity': quantity, 'total_quantity': total_quantity, 'total_price': total_price,'total_payment':totalPayment})

        except Product.DoesNotExist:
            return JsonResponse({'error': 'Product does not exist'}, status=404)
        except Exception as e:
            print("Error:", e)
            return JsonResponse({'error': 'Something went wrong'}, status=500)

    return JsonResponse({'error': 'Invalid request method'}, status=400)


def deleteCart(request, pk):
    cart_id = request.COOKIES.get('cartId')
    cart = Cart.objects.get(cart_id=cart_id)
    product = Product.objects.get(id=pk)
    cart_items = CartItem.objects.get(cart=cart, product=product)
    cart_items.delete()
    return redirect('detail-cart')


def checkOut(request):
    cookies = request.COOKIES
    cartId = cookies.get("cartId")
    quantityOrder = getOrder(cartId)
    quantityProducts = getProductCart(cartId)
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
               'quantityProducts': quantityProducts, 'pageTitle': 'Trang thanh toán', 'quantityOrders': quantityOrder}
    if request.method == "POST":
        if not request.user.is_authenticated:
            messages.error("Bạn cần đăng nhập để thanh toán!")
            return render(request, 'base/client/check-out.html', context)
        cart_id = request.COOKIES.get('cartId')
        cart = Cart.objects.get(cart_id=cart_id)
        orderObject = Order.objects.create(
            user=request.user,
            cart=cart,
            name=request.POST.get('name'),
            phone=request.POST.get('phone'),
            address=request.POST.get('address'),
            pricePayment=pricePayment,
            status="Processed"
        )
        for item in cart_items:
            orderItem, created = OrderItem.objects.get_or_create(
                order=orderObject, product=item.product)
            orderItem.quantity = item.quantity
            orderItem.save()
        cart_items.delete()
        return redirect("check-out")
    return render(request, 'base/client/check-out.html', context)


def detailOrder(request):
    cookies = request.COOKIES
    user=request.user
    cartId = cookies.get("cartId")
    quantityProducts = getProductCart(cartId)
    if request.user.is_authenticated:
        quantityOrder = getOrder(cartId)
        cart = Cart.objects.get(cart_id=cartId)
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
                    'status': order.status,
                    'created_at': order.created_at.strftime('%d/%m/%Y %H:%M:%S')
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
                'totalPayment': totalPayment,
                'status':order.status
            }
            infoOrders.append(infoOrder)
            print(infoOrders)
        context = {
            'quantityProducts': quantityProducts,
            'infoOrders': infoOrders,
            'quantityOrders': quantityOrder,
            'pageTitle': 'Trang chi tiết đơn hàng'}
    else:
        notification = "Giỏ hàng trống!"
        context = {'notification': notification,
                   'quantityProducts': quantityProducts}
    return render(request, 'base/client/detail-order.html', context)


def deleteComment(request, pk):
    comment = Comment.objects.get(id=pk)
    comment.delete()
    previous_url = request.META.get('HTTP_REFERER', '/')
    return redirect(previous_url)

# views.py


def forgotPassword(request):
    if request.method == "POST":
        email = request.POST.get('email')  # Nhận email từ form
        # Tìm kiếm người dùng theo email
        user = User.objects.filter(email=email).first()

        if user is not None:
            send_reset_email(email)   # Gọi hàm gửi email
            # Thông báo thành công
            messages.success(request, 'Mã OTP đã được gửi vào email của bạn!')
        else:
            messages.error(request, 'Không tồn tại email!')  # Thông báo lỗi

    # Trả về template
    return render(request, 'base/client/forgot-password.html')
