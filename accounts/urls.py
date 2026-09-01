from django.urls import path
from .views import register, user_login, home, user_logout, continue_as_guest


urlpatterns = [
    path('guest/', continue_as_guest, name='continue_as_guest'),
    path('register/', register, name='register'),
    path('login/', user_login, name='login'),
    path('logout/', user_logout, name='logout'),
    path('', home, name='home'),
]
