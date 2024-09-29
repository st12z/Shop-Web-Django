from base.models import Product, Category, Cart, CartItem


def getProductCart(cartId):
    quantity = 0
    try:
      cart = Cart.objects.get(cart_id=cartId)
      cart_items = CartItem.objects.filter(cart=cart)
      if cart_items:
          for item in cart_items:
              quantity += item.quantity
    except:
      quantity=0
    return quantity
