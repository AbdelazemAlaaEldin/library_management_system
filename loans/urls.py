from django.urls import path
from .views import borrow_book, return_book


urlpatterns = [
    path('borrow/<int:book_id>/', borrow_book, name='borrow_book'),
    path('return/<int:loan_id>/', return_book, name='return_book'),
]