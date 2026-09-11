from django.core.exceptions import PermissionDenied
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import ManualBookForm
from .models import Book


def require_librarian(user):
    if not user.is_staff:
        raise PermissionDenied


@login_required
def add_book_view(request):
    require_librarian(request.user)

    form = ManualBookForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        book = form.save()
        messages.success(request, f'“{book.title}” was added to the collection.')
        return redirect('add_book')

    books = Book.objects.all().order_by('-pk')

    return render(request, 'catalog/add_book.html', {'form': form, 'books': books})


@login_required
def edit_book_view(request, book_id):
    require_librarian(request.user)

    book = get_object_or_404(Book, pk=book_id)
    form = ManualBookForm(request.POST or None, instance=book)

    if request.method == 'POST':
        if 'delete' in request.POST:
            title = book.title
            book.delete()
            messages.success(request, f'“{title}” was removed from the collection.')
            return redirect('add_book')

        if form.is_valid():
            form.save()
            messages.success(request, f'“{book.title}” was updated.')
            return redirect('add_book')

    return render(request, 'catalog/edit_book.html', {'form': form, 'book': book})