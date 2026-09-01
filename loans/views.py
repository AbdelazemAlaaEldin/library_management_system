from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import F
from django.utils import timezone
from django.views.decorators.http import require_POST
from .models import Loan
from catalog.models import Book


@login_required
@require_POST
@transaction.atomic
def borrow_book(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    if Loan.objects.filter(member=request.user, book=book, status='borrowed').exists():
        messages.info(request, 'This book is already on your borrowing shelf.')
    elif Book.objects.filter(pk=book.pk, available_copies__gt=0).update(available_copies=F('available_copies') - 1):
        Loan.objects.create(member=request.user, book=book)
        messages.success(request, f'“{book.title}” is now on your borrowing shelf. Happy reading!')
    else:
        messages.warning(request, 'All copies are currently borrowed. Please check back soon.')
    return redirect('home')


@login_required
@require_POST
@transaction.atomic
def return_book(request, loan_id):
    loan = get_object_or_404(Loan, id=loan_id, member=request.user)
    updated = Loan.objects.filter(pk=loan.pk, status='borrowed').update(status='returned', return_date=timezone.localdate())
    if updated:
        Book.objects.filter(pk=loan.book_id).update(available_copies=F('available_copies') + 1)
        messages.success(request, 'Book returned. There is always another story waiting.')
    return redirect('/?section=loans')
