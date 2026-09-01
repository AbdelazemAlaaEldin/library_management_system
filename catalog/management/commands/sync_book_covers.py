from django.core.management.base import BaseCommand, CommandError
from catalog.book_api import get_api_key, refresh_cover, BookAPIError
from catalog.models import Book


class Command(BaseCommand):
    help = 'Fetch covers for existing books by exact ISBN or linked Google volume. Never changes stock counts.'

    def add_arguments(self, parser):
        parser.add_argument('--missing-only', action='store_true')
        parser.add_argument('--book-id', type=int)
        parser.add_argument('--limit', type=int, default=50)

    def handle(self, *args, **options):
        try:
            if not get_api_key():
                raise CommandError('Configure a Google Books API key in the librarian admin first.')
        except BookAPIError as exc:
            raise CommandError(str(exc)) from None
        if not 1 <= options['limit'] <= 500:
            raise CommandError('--limit must be between 1 and 500.')
        books = Book.objects.order_by('pk')
        if options['missing_only']:
            books = books.filter(cover_url='')
        if options['book_id'] is not None:
            books = books.filter(pk=options['book_id'])
        updated, skipped = 0, 0
        for book in books[:options['limit']]:
            try:
                refresh_cover(book)
                updated += 1
                self.stdout.write(f'Updated: {book.title}')
            except BookAPIError as exc:
                skipped += 1
                self.stdout.write(self.style.WARNING(f'Kept existing cover: {book.title}. {exc}'))
        self.stdout.write(f'Finished: {updated} updated; {skipped} unchanged.')
