from django.contrib import admin
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseNotAllowed
from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse
from django.urls import path, reverse
from django.utils.decorators import method_decorator
from django.views.decorators.debug import sensitive_post_parameters
from . import book_api
from .api_forms import APIKeyForm, VolumeImportForm, CoverSelectionForm
from .models import Book, LibraryAmbience


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'category', 'available_copies', 'total_copies')
    list_filter = ('category',)
    search_fields = ('title', 'author', 'isbn')
    readonly_fields = ('google_books_id', 'cover_updated_at')
    change_list_template = 'admin/catalog/book/change_list.html'
    change_form_template = 'admin/catalog/book/change_form.html'
    actions = ('refresh_selected_covers',)

    def get_urls(self):
        return [
            path('api-settings/', self.admin_site.admin_view(self.api_settings), name='catalog_book_api_settings'),
            path('import/', self.admin_site.admin_view(self.search_api), name='catalog_book_import'),
            path('<int:book_id>/choose-cover/', self.admin_site.admin_view(self.search_api), name='catalog_book_choose_cover'),
            path('<int:book_id>/refresh-cover/', self.admin_site.admin_view(self.refresh_one), name='catalog_book_refresh_cover'),
        ] + super().get_urls()

    def context(self, request, **extra):
        return {**self.admin_site.each_context(request), 'opts': self.model._meta, **extra}

    @method_decorator(sensitive_post_parameters('api_key'))
    def api_settings(self, request):
        if not request.user.is_superuser:
            raise PermissionDenied
        if request.method not in ('GET', 'POST'):
            return HttpResponseNotAllowed(['GET', 'POST'])
        configured, error = False, ''
        try:
            configured = bool(book_api.get_api_key())
        except book_api.BookAPIError as exc:
            error = str(exc)
        form = APIKeyForm(request.POST if request.method == 'POST' else None)
        if request.method == 'POST':
            try:
                if request.POST.get('action') == 'test':
                    book_api.search_books('isbn:9780141439518')
                    messages.success(request, 'Google Books is connected. You can now search for books and covers.')
                    return redirect('admin:catalog_book_api_settings')
                if form.is_valid():
                    if form.cleaned_data['clear_key']:
                        book_api.save_api_key('')
                        messages.success(request, 'The local key was removed. Your catalog and stored covers were kept.')
                    elif form.cleaned_data['api_key']:
                        book_api.save_api_key(form.cleaned_data['api_key'])
                        messages.success(request, 'The key was saved on this server. Use Test saved key to check the connection.')
                    else:
                        messages.info(request, 'The existing key was kept.')
                    return redirect('admin:catalog_book_api_settings')
            except book_api.BookAPIError as exc:
                error = str(exc)
        return TemplateResponse(request, 'admin/catalog/book/api_settings.html', self.context(request,
            title='Book API settings', form=form, configured=configured, error=error))

    def search_api(self, request, book_id=None):
        if request.method not in ('GET', 'POST'):
            return HttpResponseNotAllowed(['GET', 'POST'])
        book = get_object_or_404(Book, pk=book_id) if book_id else None
        if book and not self.has_change_permission(request, book):
            raise PermissionDenied
        if not book and not (self.has_add_permission(request) or self.has_change_permission(request)):
            raise PermissionDenied
        query = request.GET.get('q', '').strip()[:200]
        if book and not query:
            query = f'{book.title} {book.author}'[:200]
        error, results, configured = '', [], False
        try:
            configured = bool(book_api.get_api_key())
            if request.method == 'POST':
                if book:
                    form = CoverSelectionForm(request.POST)
                else:
                    if not self.has_add_permission(request):
                        raise PermissionDenied
                    form = VolumeImportForm(request.POST)
                if not form.is_valid():
                    raise book_api.BookAPIError('Choose a valid result and a whole copy count between 0 and 10,000.')
                # Fetch the chosen ID again; do not trust submitted titles, URLs, or inventory.
                volume = book_api.get_volume(form.cleaned_data['volume_id'])
                if book:
                    book_api.apply_cover(book, volume)
                    messages.success(request, f'The cover for {book.title} was updated. ISBN, loans, and copy counts were unchanged.')
                else:
                    book, created = book_api.import_volume(volume, form.cleaned_data['copies'])
                    messages.success(request, f'{book.title} was imported.' if created else f'{book.title} is already in the catalog. No stock counts were changed.')
                return redirect('admin:catalog_book_change', book.pk)
            if query and configured:
                results = book_api.search_books(query)
        except book_api.BookAPIError as exc:
            error = str(exc)
        return TemplateResponse(request, 'admin/catalog/book/search_api.html', self.context(request,
            title=f'Choose a cover for {book.title}' if book else 'Search Google Books',
            query=query, results=results, error=error, configured=configured,
            target_book=book, can_import=self.has_add_permission(request)))

    def refresh_one(self, request, book_id):
        if request.method != 'POST':
            return HttpResponseNotAllowed(['POST'])
        book = get_object_or_404(Book, pk=book_id)
        if not self.has_change_permission(request, book):
            raise PermissionDenied
        try:
            book_api.refresh_cover(book)
            messages.success(request, 'Cover refreshed. Book details and stock counts were kept.')
        except book_api.BookAPIError as exc:
            messages.warning(request, str(exc))
        return redirect('admin:catalog_book_change', book.pk)

    @admin.action(description='Refresh selected covers from Google Books (up to 5)', permissions=['change'])
    def refresh_selected_covers(self, request, queryset):
        if queryset.count() > 5:
            self.message_user(request, 'Select up to 5 books at once, or use the sync_book_covers command for a larger collection.', level=messages.WARNING)
            return
        for book in queryset:
            try:
                book_api.refresh_cover(book)
                self.message_user(request, f'Updated cover: {book.title}', level=messages.SUCCESS)
            except book_api.BookAPIError as exc:
                self.message_user(request, f'{book.title}: {exc}', level=messages.WARNING)


@admin.register(LibraryAmbience)
class LibraryAmbienceAdmin(admin.ModelAdmin):
    fields = ('enabled', 'title', 'artist', 'audio_file', 'audio_url')

    def has_add_permission(self, request):
        return super().has_add_permission(request) and not LibraryAmbience.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


admin.site.site_header = 'The Reading Room · Librarian desk'
admin.site.site_title = 'The Reading Room'
admin.site.index_title = 'Care for your collection'
