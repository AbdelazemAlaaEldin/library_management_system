from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout
from django.db.models import Q, Count
from django.shortcuts import render, redirect
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST
from catalog.models import Book
from loans.models import Loan


def register(request):
    form = UserCreationForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        login(request, user)
        request.session['library_entry_pending'] = True
        request.session.pop('library_guest', None)
        messages.success(request, 'Your library card is ready. Welcome to The Reading Room!')
        return redirect('home')
    return render(request, 'accounts/register.html', {'form': form})


def user_login(request):
    form = AuthenticationForm(request, data=request.POST or None)
    if request.method == 'POST' and form.is_valid():
        login(request, form.get_user())
        request.session['library_entry_pending'] = True
        request.session.pop('library_guest', None)
        target = request.POST.get('next', '')
        if target and url_has_allowed_host_and_scheme(target, allowed_hosts={request.get_host()}, require_https=request.is_secure()):
            return redirect(target)
        return redirect('home')
    return render(request, 'accounts/login.html', {'form': form, 'next': request.GET.get('next', '')})


def home(request):
    if request.session.pop('library_entry_pending', False):
        entrance_mode = 'opening'
    elif request.GET.get('entrance') == '1' or not (request.user.is_authenticated or request.session.get('library_guest')):
        entrance_mode = 'choices'
    else:
        entrance_mode = 'hidden'
    all_books = Book.objects.all()
    books = all_books.order_by('title')
    query = request.GET.get('q', '').strip()[:200]
    category = request.GET.get('category', '')[:100]
    section = request.GET.get('section', 'collection')
    if section not in ('collection', 'loans', 'saved'):
        section = 'collection'
    if not request.user.is_authenticated:
        section = 'collection'
    sort = request.GET.get('sort', 'title')
    if query:
        books = books.filter(Q(title__icontains=query) | Q(author__icontains=query) | Q(isbn__icontains=query))
    if category:
        books = books.filter(category__iexact=category)
    if request.GET.get('available') == '1':
        books = books.filter(available_copies__gt=0)
    if sort == 'newest':
        books = books.order_by('-publication_date', 'title')
    elif sort == 'author':
        books = books.order_by('author', 'title')
    loans = Loan.objects.filter(member=request.user, status='borrowed').select_related('book') if request.user.is_authenticated else Loan.objects.none()
    borrowed_ids = set(loans.values_list('book_id', flat=True))
    return render(request, 'accounts/home.html', {
        'entrance_mode': entrance_mode,
        'books': books, 'loans': loans, 'borrowed_ids': borrowed_ids,
        'categories': all_books.values('category').annotate(count=Count('id')).order_by('category'),
        'book_count': all_books.count(), 'category_count': all_books.values('category').distinct().count(),
        'available_count': all_books.filter(available_copies__gt=0).count(),
        'has_sample_books': all_books.filter(isbn__startswith='SAMPLE').exists(),
        'query': query, 'category': category, 'section': section, 'sort': sort,
        'available_only': request.GET.get('available') == '1',
    })


@require_POST
def continue_as_guest(request):
    # Guest mode never carries an authenticated member's borrowing privileges.
    if request.user.is_authenticated:
        logout(request)
    request.session['library_guest'] = True
    request.session['library_entry_pending'] = True
    return redirect('home')


@require_POST
def user_logout(request):
    logout(request)
    return redirect('home')
