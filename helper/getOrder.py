from base.models import Order,OrderItem,Cart
def getOrder(cartId):
  countOrder=0
  cart = Cart.objects.get(cart_id=cartId)
  countOrder = Order.objects.filter(cart=cart).count()
  if not countOrder:
    countOrder=0
  return countOrder