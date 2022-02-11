from django.shortcuts import render, get_object_or_404, redirect
from .models import Order, OrderItem, Products
from .forms import OrderCreateForm
from cart.views import get_cart, cart_clear
from decimal import Decimal
from django.conf import settings
import stripe
from .tasks import order_created
#from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse
from django.template.loader import render_to_string
import weasyprint
#from finesauces_project.decorators import user_created_order

stripe.api_key=settings.STRIPE_TEST_SECRET_KEY

#@staff_member_required
def invoice_pdf(request, order_id):
    order=get_object_or_404(Order, id=order_id)
    response=HttpResponse(content_type='application/pdf')
    response['Content-Disposition']=f'filename=order_{order.id}.pdf'

    #Generate Pdf
    html=render_to_string('pdf.html', {'order': order})
    stylesheets=[weasyprint.CSS(settings.STATIC_ROOT + 'css/pdf.css')]
    weasyprint.HTML(string=html).write_pdf(response, stylesheets=stylesheets)
    return response

#@user_created_order
#def customer_invoice_pdf(request, order_id):
#    order=get_object_or_404(Order, id=order_id)

    #if request.user==order.user:
#    response=HttpResponse(content_type='application/pdf')
#    response['Content-Disposition']=f'filename=order_{order.id}.pdf'
        
    #Generate Pdf
#    html=render_to_string('pdf.html', {'order': order})
#   stylesheets=[weasyprint.CSS(settings.STATIC_ROOT + 'css/pdf.css')]
#    weasyprint.HTML(string=html).write_pdf(response, stylesheets=stylesheets)
#    return response

    #return redirect('profile')


def order_create(request):
    cart=get_cart(request)
    cart_qty=sum(item['quantity'] for item in cart.values())
    transport_cost=round((3.99+(cart_qty//10)*1.5), 2)

    if request.method=='POST':
        order_form=OrderCreateForm(request.POST)
        if order_form.is_valid():
            cf=order_form.cleaned_data
            transport=cf['transport']
            
            if transport=='Recipient pickup':
                transport_cost=0
                
            order=order_form.save(commit=False)
            if request.user.is_authenticated:
                order.user=request.user
            order.transport_cost=Decimal(transport_cost)
            order.save()
                
            product_ids=cart.keys()
            products=Products.objects.filter(id__in=product_ids)
                
            for product in products:
                cart_item=cart[str(product.id)]
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    price=cart_item['price'],
                    quantity=cart_item['quantity'])
                        
            cart_clear(request)
            order_created.delay(order.id)

            customer=stripe.Customer.create(
                name=cf['last_name']+" "+cf['first_name'],
                email=cf['email'],
                source=request.POST['stripeToken']
            )

            charge = stripe.Charge.create (
                customer = customer,
                amount = int(order.get_total_cost() * 100),
                currency='usd',
                description = order
            )
                
            return render(
                request,
                'order_created.html',
                {'order':order}
            )

    else:
        order_form=OrderCreateForm()
        if request.user.is_authenticated:
            initial_data={
                'first_name':request.user.first_name,
                'last_name':request.user.last_name,
                'email': request.user.email,
                'telephone': request.user.profile.phone_number,
                'address': request.user.profile.address,
                'postal_code': request.user.profile.postal_code,
                'city': request.user.profile.city,
                'country': request.user.profile.country,
            }
            order_form=OrderCreateForm(initial=initial_data)
             
    return render(
        request,
        'order_create.html',
        {
            'cart': cart,
            'order_form': order_form,
            'transport_cost': transport_cost
        })


def order_detail(request, order_id):
    order=Order.objects.get(pk=order_id)
    return render(
        request,
        'order_detail.html',
        {'order':order}
    )



