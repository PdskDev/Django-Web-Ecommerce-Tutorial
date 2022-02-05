from pyexpat import model
from django.contrib import admin
from .models import Category, Products, Reviews

class OrderReviewInline(admin.TabularInline):
    model=Reviews

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display=('name', 'slug')
    prepopulated_fields={'slug':('name',)}

@admin.register(Products)  
class ProductsAdmin(admin.ModelAdmin):
    list_display=('name', 'category', 'slug', 'price', 'available')  
    list_filter=('category', 'available')
    list_editable=('price', 'available')
    prepopulated_fields={'slug':('name',)}

    inlines=[OrderReviewInline]






