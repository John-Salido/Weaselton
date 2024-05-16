from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from store.models.customer import Customer
from store.models.product import Products

class Cart(View):
    def get(self, request):
        ids = list(request.session.get('cart', {}).keys())
        products = Products.get_products_by_id(ids)
        return render(request, 'cart.html', {'products': products})

def delete_from_cart(request, product_id):
    if 'cart' in request.session:
        cart = request.session['cart']
        if str(product_id) in cart:
            del cart[str(product_id)]
            request.session['cart'] = cart
            messages.success(request, 'Product removed from the cart.')
    
    return redirect('cart')
    
