from datetime import date
from django.core.management.base import BaseCommand
from django.db import transaction
from catalog.models import Book, LibraryAmbience


class Command(BaseCommand):
    help = 'Add an optional sample collection to an EMPTY catalog. Never changes existing books.'

    @transaction.atomic
    def handle(self, *args, **options):
        if Book.objects.exists():
            self.stdout.write('Catalog already contains books; no sample data added.')
            return
        # Demonstration catalog only. SAMPLE IDs are intentionally not real ISBNs.
        books = [
            ('A Room of One\'s Own', 'Virginia Woolf', 'Literature', 1929),
            ('Alice in Wonderland', 'Lewis Carroll', 'Fantasy', 1865),
            ('Anne of Green Gables', 'L. M. Montgomery', 'Fiction', 1908),
            ('Around the World in Eighty Days', 'Jules Verne', 'Adventure', 1873),
            ('Little Women', 'Louisa May Alcott', 'Classics', 1868),
            ('Pride and Prejudice', 'Jane Austen', 'Classics', 1813),
            ('Sherlock Holmes', 'Arthur Conan Doyle', 'Mystery', 1892),
            ('The Great Gatsby', 'F. Scott Fitzgerald', 'Fiction', 1925),
            ('The Secret Garden', 'Frances Hodgson Burnett', 'Fiction', 1911),
            ('The Time Machine', 'H. G. Wells', 'Science Fiction', 1895),
            ('The Wind in the Willows', 'Kenneth Grahame', 'Fantasy', 1908),
            ('Treasure Island', 'Robert Louis Stevenson', 'Adventure', 1883),
        ]
        for index, (title, author, category, year) in enumerate(books, 1):
            Book.objects.create(title=title, author=author, category=category,
                publication_date=date(year, 1, 1), isbn=f'SAMPLE{index:07d}',
                total_copies=4, available_copies=4)
        LibraryAmbience.objects.get_or_create(pk=1)
        self.stdout.write(self.style.SUCCESS('Added 12 sample books. Replace sample records with your real inventory in the admin.'))
