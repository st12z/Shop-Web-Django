from base.models import Product, Category,Cart,CartItem
def getProductCart(request):
  quantity=0
  cookies = request.COOKIES
  cartId = cookies.get("cartId")
  cart=Cart.objects.get(cart_id=cartId)
  cart_items=CartItem.objects.filter(cart=cart)
  if cart_items:
    for item in cart_items:
      quantity+=item.quantity
  return quantity