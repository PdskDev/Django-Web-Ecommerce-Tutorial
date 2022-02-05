from django.urls import path
from . import views

app_name='listings'

urlpatterns=[
    path ('', views.products_list, name='products_list'),
    path ('<slug:category_slug>', views.products_list, name='products_list_by_category'),
    path('<slug:category_slug>/<slug:product_slug>/', views.products_detail, name='products_detail'),
]