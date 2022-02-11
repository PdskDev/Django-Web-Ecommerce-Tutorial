from django.shortcuts import render, get_object_or_404, redirect
from .models import OrderItem, Order, Products
from .forms import OrderCreateForm
from cart.views import get_cart, cart_clear
from decimal import Decimal
from django.conf import settings
import stripe


stripe.api_key = settings.STRIPE_TEST_SECRET_KEY


def order_create(request):
    cart = get_cart(request)
    cart_qty = sum(item['quantity'] for item in cart.values())
    transport_cost = round((3.99 + (cart_qty // 10) * 1.5), 2)

    if request.method == 'POST':
        order_form = OrderCreateForm(request.POST)
        if order_form.is_valid():
            cf = order_form.cleaned_data
            transport = cf['transport']
            
            if transport == 'Recipient pickup':
                transport_cost = 0

            order = order_form.save(commit=False)
            
            order.transport_cost = Decimal(transport_cost) 
            order.save()

            product_ids = cart.keys()
            products = Products.objects.filter(id__in=product_ids)

            for product in products:
                cart_item =cart[str(product.id)]
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    price=cart_item['price'],
                    quantity=cart_item['quantity']
                )

            customer = stripe.Customer.create(
                
                email = cf['email'],
                source = request.POST['stripeToken']
            )

            charge = stripe.Charge.create (
                customer = customer,
                amount = int(order.get_total_cost() * 100),
                currency='usd',
                description = order
            )

            cart_clear(request)
            
            return render(
                request,
                'order_created.html',
                {'order': order}
            )

    else:
        order_form = OrderCreateForm()


    return render(
        request,
        'order_create.html',
        {
            'cart': cart, 
            'order_form': order_form,
            'transport_cost': transport_cost
        }
    )