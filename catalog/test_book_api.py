import json
import os
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock
from urllib.error import HTTPError, URLError

from django.contrib.auth.models import User, Permission
from django.core.exceptions import ValidationError
from django.test import TestCase, SimpleTestCase, Client
from . import book_api
from .models import Book
from loans.models import Loan


API_KEY = 'test-google-books-key-never-public-1234'
VOLUME = {
    'id': 'PrideEdition01',
    'volumeInfo': {
        'title': 'Pride and Prejudice', 'authors': ['Jane Austen'],
        'industryIdentifiers': [{'type': 'ISBN_13', 'identifier': '9780141439518'}, {'type': 'ISBN_10', 'identifier': '0141439513'}],
        'publishedDate': '2003', 'categories': ['Classics'],
        'description': '<p>A classic <b>novel</b>.</p>',
        'imageLinks': {'thumbnail': 'http://books.google.com/books?id=PrideEdition01&img=1&zoom=1&key=SHOULD-NOT-BE-STORED'},
    },
}


class BookAPIUnitTests(SimpleTestCase):
    def test_key_is_kept_in_private_config_and_environment_wins(self):
        with tempfile.TemporaryDirectory() as folder, self.settings(BASE_DIR=Path(folder)), patch.dict(os.environ, {'GOOGLE_BOOKS_API_KEY': ''}):
            self.assertEqual(book_api.get_api_key(), '')
            book_api.save_api_key(API_KEY)
            self.assertEqual(book_api.get_api_key(), API_KEY)
            with patch.dict(os.environ, {'GOOGLE_BOOKS_API_KEY': 'environment-key'}):
                self.assertEqual(book_api.get_api_key(), 'environment-key')
                with self.assertRaises(book_api.BookAPIError):
                    book_api.save_api_key('')
            book_api.save_api_key('')
            self.assertEqual(book_api.get_api_key(), '')

    def test_unreadable_config_reports_safe_error(self):
        with tempfile.TemporaryDirectory() as folder, self.settings(BASE_DIR=Path(folder)), patch.dict(os.environ, {'GOOGLE_BOOKS_API_KEY': ''}):
            (Path(folder) / 'book_api.local.toml').write_text('invalid TOML [SECRET', encoding='utf-8')
            with self.assertRaises(book_api.BookAPIError) as error:
                book_api.get_api_key()
            self.assertNotIn('SECRET', str(error.exception))

    def test_isbn_checksum_and_equivalent_editions(self):
        self.assertEqual(book_api.normalize_isbn('978-0-14-143951-8'), '9780141439518')
        self.assertEqual(book_api.isbn13('0141439513'), '9780141439518')
        for value in ('SAMPLE0000001', '9780141439519', 'abc'):
            self.assertEqual(book_api.normalize_isbn(value), '')

    def test_provider_links_are_https_and_never_contain_api_key(self):
        volume = book_api.normalize_volume(VOLUME)
        self.assertTrue(volume['cover_url'].startswith('https://books.google.com/'))
        self.assertNotIn('key=', volume['cover_url'])
        self.assertEqual(volume['publication_date'].isoformat(), '2003-01-01')
        self.assertEqual(volume['description'], 'A classic novel.')
        for value in ('javascript:alert(1)', 'https://evil.example/cover.jpg', 'https://books.google.com@evil.example/cover', 'https://books.google.com:1234/cover'):
            self.assertEqual(book_api.safe_cover_url(value), '')

    def test_missing_fields_and_malformed_items_do_not_crash(self):
        for item in (None, [], {}, {'id': '../secret', 'volumeInfo': {'title': 'Bad'}}):
            self.assertIsNone(book_api.normalize_volume(item))
        volume = book_api.normalize_volume({'id': 'abc', 'volumeInfo': {'title': 'Old book', 'publishedDate': 'unknown'}})
        self.assertEqual(volume['cover_url'], '')
        self.assertIsNone(volume['publication_date'])

    @patch('catalog.book_api.get_api_key', return_value='')
    @patch('catalog.book_api.build_opener')
    def test_missing_key_does_not_make_request(self, opener, key):
        with self.assertRaises(book_api.BookAPIError):
            book_api.search_books('Austen')
        opener.assert_not_called()

    @patch('catalog.book_api.get_api_key', return_value=API_KEY)
    @patch('catalog.book_api.build_opener')
    def test_api_key_is_only_sent_to_fixed_google_endpoint(self, opener, key):
        response = MagicMock()
        response.read.return_value = json.dumps({'items': [VOLUME]}).encode()
        opener.return_value.open.return_value.__enter__.return_value = response
        results = book_api.search_books('9780141439518')
        request = opener.return_value.open.call_args.args[0]
        self.assertTrue(request.full_url.startswith('https://www.googleapis.com/books/v1/volumes?'))
        self.assertIn('q=isbn%3A9780141439518', request.full_url)
        self.assertIn('key=' + API_KEY, request.full_url)
        self.assertNotIn(API_KEY, str(results))
        self.assertEqual(opener.return_value.open.call_args.kwargs['timeout'], 10)

    @patch('catalog.book_api.get_api_key', return_value=API_KEY)
    @patch('catalog.book_api.build_opener')
    def test_provider_errors_do_not_leak_credentials(self, opener, key):
        for failure in (HTTPError('https://example.com/?key=' + API_KEY, 403, 'secret ' + API_KEY, {}, None),
                        HTTPError('https://example.com/?key=' + API_KEY, 429, 'quota', {}, None),
                        URLError(API_KEY), TimeoutError(API_KEY)):
            opener.return_value.open.side_effect = failure
            with self.assertRaises(book_api.BookAPIError) as error:
                book_api.search_books('Austen')
            self.assertNotIn(API_KEY, str(error.exception))

    @patch('catalog.book_api.api_request')
    def test_invalid_volume_ids_never_reach_network(self, request):
        for volume_id in ('../settings', 'abc?key=oops', 'http://localhost/'):
            with self.assertRaises(book_api.BookAPIError):
                book_api.get_volume(volume_id)
        request.assert_not_called()


class BookCoverDatabaseTests(TestCase):
    def setUp(self):
        self.book = Book.objects.create(title='Pride and Prejudice', author='Jane Austen',
            isbn='9780141439518', category='Classics', total_copies=4, available_copies=3,
            publication_date='1813-01-28', cover_url='https://example.com/old-cover.jpg')
        member = User.objects.create_user('borrower')
        self.loan = Loan.objects.create(member=member, book=self.book)

    @patch('catalog.book_api.search_books')
    def test_refresh_preserves_inventory_metadata_and_loans(self, search):
        search.return_value = [book_api.normalize_volume(VOLUME)]
        book_api.refresh_cover(self.book)
        self.book.refresh_from_db()
        self.assertEqual((self.book.total_copies, self.book.available_copies), (4, 3))
        self.assertEqual(self.book.publication_date.isoformat(), '1813-01-28')
        self.assertEqual(self.book.google_books_id, 'PrideEdition01')
        self.assertEqual(Loan.objects.get(pk=self.loan.pk).status, 'borrowed')

    @patch('catalog.book_api.search_books', return_value=[])
    def test_missing_cover_preserves_previous_image(self, search):
        with self.assertRaises(book_api.BookAPIError):
            book_api.refresh_cover(self.book)
        self.book.refresh_from_db()
        self.assertEqual(self.book.cover_url, 'https://example.com/old-cover.jpg')

    @patch('catalog.book_api.search_books')
    def test_different_isbn_and_sample_ids_are_not_auto_matched(self, search):
        wrong = book_api.normalize_volume(VOLUME)
        wrong['isbns'] = ['9780141439976']
        search.return_value = [wrong]
        with self.assertRaises(book_api.BookAPIError):
            book_api.refresh_cover(self.book)
        self.book.isbn = 'SAMPLE0000001'
        search.reset_mock()
        with self.assertRaises(book_api.BookAPIError):
            book_api.refresh_cover(self.book)
        search.assert_not_called()

    def test_import_duplicate_does_not_create_extra_copies(self):
        book, created = book_api.import_volume(book_api.normalize_volume(VOLUME), 100)
        self.assertFalse(created)
        self.assertEqual(book.pk, self.book.pk)
        self.book.refresh_from_db()
        self.assertEqual((self.book.total_copies, self.book.available_copies), (4, 3))

    def test_import_with_zero_inventory_is_not_available(self):
        volume = book_api.normalize_volume(VOLUME)
        volume.update(id='OtherEdition', isbn='9780141439976', isbns=['9780141439976'])
        book, created = book_api.import_volume(volume, 0)
        self.assertTrue(created)
        self.assertEqual(book.available_copies, 0)
        self.assertEqual(book.total_copies, 0)

    def test_manual_cover_must_use_https(self):
        self.book.cover_url = 'http://example.com/cover.jpg'
        with self.assertRaises(ValidationError):
            self.book.full_clean()

    @patch('catalog.book_api.api_request', side_effect=AssertionError('Public pages must not call the API'))
    def test_public_pages_render_stored_covers_with_no_api_request(self, request):
        response = self.client.get('/')
        self.assertContains(response, 'data-cover-image src="https://example.com/old-cover.jpg"')
        self.assertContains(response, 'THE READING ROOM COLLECTION')
        request.assert_not_called()


class BookAPIAdminTests(TestCase):
    def setUp(self):
        self.admin_user = User.objects.create_superuser('admin')
        self.member = User.objects.create_user('reader')
        self.staff = User.objects.create_user('librarian', is_staff=True)
        self.base = '/admin/catalog/book/'

    def test_credentials_and_import_are_admin_only(self):
        for route in ('api-settings/', 'import/'):
            self.assertEqual(self.client.get(self.base + route).status_code, 302)
        self.client.force_login(self.member)
        self.assertEqual(self.client.get(self.base + 'api-settings/').status_code, 302)
        self.client.force_login(self.staff)
        self.assertEqual(self.client.get(self.base + 'api-settings/').status_code, 403)
        self.assertEqual(self.client.get(self.base + 'import/').status_code, 403)

    @patch('catalog.book_api.get_api_key', return_value=API_KEY)
    def test_saved_key_is_not_rendered_even_to_admin(self, key):
        self.client.force_login(self.admin_user)
        response = self.client.get(self.base + 'api-settings/')
        self.assertContains(response, 'A key is saved')
        self.assertNotContains(response, API_KEY)
        self.assertEqual(self.client.get('/book_api.local.toml').status_code, 404)

    @patch('catalog.book_api.get_api_key', return_value='')
    def test_missing_key_setup_is_actionable(self, key):
        self.client.force_login(self.admin_user)
        self.assertContains(self.client.get(self.base + 'import/'), 'Set up the connection')
        self.assertEqual(self.client.get(self.base + 'api-settings/').status_code, 200)

    @patch('catalog.book_api.get_api_key', return_value=API_KEY)
    @patch('catalog.book_api.search_books')
    def test_search_results_and_server_verified_import(self, search, key):
        search.return_value = [book_api.normalize_volume(VOLUME)]
        self.client.force_login(self.admin_user)
        response = self.client.get(self.base + 'import/', {'q': 'Austen'})
        self.assertContains(response, 'Copies owned')
        self.assertContains(response, 'Pride and Prejudice')
        self.assertNotContains(response, API_KEY)
        with patch('catalog.book_api.get_volume', return_value=book_api.normalize_volume(VOLUME)):
            response = self.client.post(self.base + 'import/', {'volume_id': 'PrideEdition01', 'copies': 2,
                'title': 'Untrusted override', 'cover_url': 'https://evil.example/bad.jpg'})
        self.assertEqual(response.status_code, 302)
        book = Book.objects.get()
        self.assertEqual(book.title, 'Pride and Prejudice')
        self.assertEqual(book.available_copies, 2)
        self.assertTrue(book.cover_url.startswith('https://books.google.com/'))

    def test_key_and_import_posts_require_csrf(self):
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.admin_user)
        for route in ('api-settings/', 'import/'):
            self.assertEqual(client.post(self.base + route, {'api_key': API_KEY}).status_code, 403)

    @patch('catalog.book_api.get_api_key', return_value=API_KEY)
    @patch('catalog.book_api.get_volume')
    def test_invalid_copy_count_is_rejected_before_provider_request(self, volume, key):
        self.client.force_login(self.admin_user)
        response = self.client.post(self.base + 'import/', {'volume_id': 'PrideEdition01', 'copies': -3})
        self.assertContains(response, 'whole copy count')
        volume.assert_not_called()
        self.assertFalse(Book.objects.exists())
