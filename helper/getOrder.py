from base.models import Order,OrderItem,Cart
def getOrder(request):
  cart_id = request.COOKIES.get('cartId')
  cart = Cart.objects.get(cart_id=cart_id)
  countOrder = Order.objects.filter(cart=cart).count()
  if not countOrder:
    countOrder=0
  return countOrder