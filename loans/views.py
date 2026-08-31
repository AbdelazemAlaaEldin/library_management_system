from django.shortcuts import render
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import Loan
from catalog.models import Book

# Create your views here.
@login_required
def borrow_book(request, book_id):

    book = get_object_or_404(Book, id=book_id)

    # Check if there are available copies
    if book.available_copies <= 0:
        return redirect('home')

    # Check if the user already borrowed this book
    existing_loan = Loan.objects.filter(
        member=request.user,
        book=book,
        status='borrowed'
    ).exists()

    if existing_loan:
        return redirect('home')

    # Create new loan
    Loan.objects.create(
        member=request.user,
        book=book,
        status='borrowed'
    )

    # Decrease available copies
    book.available_copies -= 1
    book.save()

    return redirect('home')


@login_required
def return_book(request, loan_id):

    loan = get_object_or_404(
        Loan,
        id=loan_id,
        member=request.user,
        status='borrowed'
    )

    # Change loan status
    loan.status = 'returned'
    loan.return_date = timezone.now().date()
    loan.save()

    # Increase available copies
    book = loan.book
    book.available_copies += 1
    book.save()

    return redirect('home')