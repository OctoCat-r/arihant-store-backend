from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login),
    path('refresh/', views.refresh),
    path('me/', views.me),
    path('me/update/', views.update_me),
]
