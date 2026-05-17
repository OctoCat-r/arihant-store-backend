from django.urls import path
from . import views

urlpatterns = [
    path('', views.list_sales),
    path('create/', views.create_sale),
]
