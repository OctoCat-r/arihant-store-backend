from django.urls import path
from . import views

urlpatterns = [
    # categories (must come before <prod_id> catch-all)
    path('categories/', views.list_categories),
    path('categories/create/', views.create_category),
    path('categories/<str:cat_id>/', views.category_detail),

    # brands
    path('brands/', views.list_brands),
    path('brands/create/', views.create_brand),

    # products
    path('', views.list_products),
    path('search/', views.search_products),
    path('create/', views.create_product),
    path('<str:prod_id>/', views.product_detail),
]
