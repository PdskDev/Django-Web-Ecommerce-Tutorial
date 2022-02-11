from django.shortcuts import render, get_object_or_404, redirect
from .models import Category, Products, Reviews
from .forms import ReviewForm
from cart.forms import CartAddProductForm

# Create your views here.

def products_list(request, category_slug=None):
    categories = Category.objects.all()
    requested_category=None
    products= Products.objects.all()

    if category_slug:
        requested_category=get_object_or_404(Category, slug=category_slug)
        products=Products.objects.filter(category=requested_category)

    return render(
        request,
        'products/list.html',
        {
            'categories': categories,
            'requested_category': requested_category,
            'products': products
        }
    )

def products_detail(request, category_slug, product_slug):
    
    category=get_object_or_404(Category, slug=category_slug)
    product= get_object_or_404(
        Products,
        category_id=category.id,
        slug=product_slug
    ) 

    if request.method=='POST':
        review_form= ReviewForm(request.POST)

        if review_form.is_valid():
            cf=review_form.cleaned_data

            author_name="Anonymous"
            if request.user.is_authenticated and request.user.first_name!='':
                author_name=request.user.first_name

            Reviews.objects.create(
                product=product,
                author=author_name,
                rating=cf['rating'],
                text=cf['text']
            )
        return redirect(
                'listings:products_detail',
                category_slug=category_slug, product_slug=product_slug
            )
        
    else:
            review_form=ReviewForm()
            cart_product_form=CartAddProductForm()
            
    return render(
        request,
        'products/details.html',
        {
            'product':product,
            'review_form':review_form,
            'cart_product_form':cart_product_form
        }
    ) 


