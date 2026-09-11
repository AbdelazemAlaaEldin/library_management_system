from django.urls import path
from .views import add_book_view, edit_book_view

urlpatterns = [
    path('add/', add_book_view, name='add_book'),
    path('<int:book_id>/edit/', edit_book_view, name='edit_book'),
]