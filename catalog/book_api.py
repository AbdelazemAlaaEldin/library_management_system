"""Server-side Google Books integration. No API credentials go to the browser."""
import json
import os
import re
import tempfile
import tomllib
from datetime import date
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urlsplit, urlunsplit, parse_qsl
from urllib.request import Request, build_opener, HTTPRedirectHandler

from django.conf import settings
from django.db import transaction, IntegrityError
from django.utils import timezone
from django.utils.html import strip_tags
from django.views.decorators.debug import sensitive_variables


class BookAPIError(Exception):
    """Safe, user-readable errors that never include a credential or request URL."""


def key_file():
    return settings.BASE_DIR / 'book_api.local.toml'


@sensitive_variables()
def get_api_key():
    key = os.environ.get('GOOGLE_BOOKS_API_KEY', '').strip()
    if key:
        return key
    try:
        data = tomllib.loads(key_file().read_text(encoding='utf-8'))
        value = data.get('google_books', {}).get('api_key', '')
        return value.strip() if isinstance(value, str) else ''
    except FileNotFoundError:
        return ''
    except (OSError, ValueError, AttributeError):
        raise BookAPIError('The local book API configuration could not be read. Ask the administrator to replace the key.') from None


@sensitive_variables()
def save_api_key(key):
    """Store outside database/static/media; environment credentials take precedence."""
    if os.environ.get('GOOGLE_BOOKS_API_KEY', '').strip():
        raise BookAPIError('The key is managed by GOOGLE_BOOKS_API_KEY in the server environment. Update it there and restart the app.')
    key = key.strip()
    if key and not re.fullmatch(r'[A-Za-z0-9_-]{20,200}', key):
        raise BookAPIError('Enter a Google Books API key, not a URL or a TMDB credential.')
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', dir=settings.BASE_DIR, prefix='.book-api-', suffix='.tmp', delete=False) as handle:
            temporary = handle.name
            handle.write('[google_books]\napi_key = ' + json.dumps(key) + '\n')
        os.chmod(temporary, 0o600)
        os.replace(temporary, key_file())
    except OSError:
        raise BookAPIError('The server could not save the API key. Check access to the project directory.') from None
    finally:
        if temporary and os.path.exists(temporary):
            os.unlink(temporary)


class NoAPIRedirects(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        # Never forward a credential-bearing request to another endpoint.
        return None


@sensitive_variables()
def api_request(path='', params=None):
    key = get_api_key()
    if not key:
        raise BookAPIError('Add your Google Books API key in Book API settings before searching or fetching covers.')
    query = dict(params or {})
    query['key'] = key
    url = 'https://www.googleapis.com/books/v1/volumes' + path + '?' + urlencode(query)
    request = Request(url, headers={'Accept': 'application/json', 'User-Agent': 'ReadingRoomLibrary/1.0'})
    try:
        with build_opener(NoAPIRedirects()).open(request, timeout=10) as response:
            body = response.read(2_000_001)
        if len(body) > 2_000_000:
            raise BookAPIError('Google Books returned too much data. Try a narrower search.')
        result = json.loads(body)
        if not isinstance(result, dict) or 'error' in result:
            raise BookAPIError('Google Books returned an unexpected response. Please try again later.')
        return result
    except HTTPError as error:
        if error.code in (400, 401, 403):
            raise BookAPIError('Google Books rejected the request. Check the API key, enable Books API, and check its restrictions and quota.') from None
        if error.code == 429:
            raise BookAPIError('Google Books quota was reached. Please wait before trying again.') from None
        if error.code == 404:
            raise BookAPIError('This volume is no longer available from Google Books.') from None
        raise BookAPIError('Google Books is temporarily unavailable. Your stored books and covers are unchanged.') from None
    except (URLError, TimeoutError, OSError, ValueError):
        raise BookAPIError('Could not reach Google Books or read its response. Please try again later.') from None


def normalize_isbn(value):
    value = re.sub(r'[\s-]', '', str(value or '')).upper()
    if re.fullmatch(r'\d{13}', value):
        return value if sum(int(c) * (1 if i % 2 == 0 else 3) for i, c in enumerate(value)) % 10 == 0 else ''
    if re.fullmatch(r'\d{9}[\dX]', value):
        return value if sum((10 if c == 'X' else int(c)) * (10 - i) for i, c in enumerate(value)) % 11 == 0 else ''
    return ''


def isbn13(value):
    value = normalize_isbn(value)
    if len(value) == 10:
        prefix = '978' + value[:9]
        return prefix + str((-sum(int(c) * (1 if i % 2 == 0 else 3) for i, c in enumerate(prefix))) % 10)
    return value


def safe_cover_url(value):
    if not isinstance(value, str):
        return ''
    try:
        parts = urlsplit(value)
        if parts.scheme not in ('http', 'https') or parts.username or parts.password or parts.port not in (None, 80, 443):
            return ''
        if parts.hostname not in ('books.google.com', 'books.googleusercontent.com', 'images.google.com'):
            return ''
        # Never persist provider credentials, even if an upstream URL includes them.
        query = [(key, val) for key, val in parse_qsl(parts.query) if key.lower() in {'id', 'printsec', 'img', 'zoom', 'edge', 'source', 'vid', 'jscmd', 'sig'}]
        return urlunsplit(('https', parts.hostname, parts.path, urlencode(query), ''))[:1000]
    except ValueError:
        return ''


def normalize_volume(item):
    if not isinstance(item, dict):
        return None
    volume_id = item.get('id', '')
    info = item.get('volumeInfo')
    if not isinstance(volume_id, str) or not re.fullmatch(r'[A-Za-z0-9_-]{1,80}', volume_id) or not isinstance(info, dict):
        return None
    title = info.get('title')
    if not isinstance(title, str) or not title.strip():
        return None
    identifiers = info.get('industryIdentifiers') or []
    isbns = [normalize_isbn(row.get('identifier')) for row in identifiers if isinstance(row, dict) and row.get('type') in ('ISBN_10', 'ISBN_13')] if isinstance(identifiers, list) else []
    isbns = [value for value in isbns if value]
    authors = info.get('authors') or []
    authors = [value for value in authors if isinstance(value, str)] if isinstance(authors, list) else []
    links = info.get('imageLinks') or {}
    cover = next((safe_cover_url(links.get(size)) for size in ('large', 'medium', 'small', 'thumbnail', 'smallThumbnail') if safe_cover_url(links.get(size))), '') if isinstance(links, dict) else ''
    categories = info.get('categories') or []
    category = next((c for c in categories if isinstance(c, str)), 'Uncategorized') if isinstance(categories, list) else 'Uncategorized'
    published = info.get('publishedDate', '')
    publication = None
    if isinstance(published, str) and re.fullmatch(r'\d{4}(-\d{2})?(-\d{2})?', published):
        try:
            parts = [int(part) for part in published.split('-')]
            publication = date(*(parts + [1] * (3 - len(parts))))
        except ValueError:
            pass
    description = info.get('description', '')
    return {
        'id': volume_id, 'title': strip_tags(title).strip()[:200],
        'author': ', '.join(authors)[:100] or 'Unknown author',
        'isbn': next((value for value in isbns if len(value) == 13), next(iter(isbns), '')),
        'isbns': isbns, 'category': category[:100], 'cover_url': cover,
        'publication_date': publication, 'published_label': published if isinstance(published, str) else '',
        'description': strip_tags(description)[:12000] if isinstance(description, str) else '',
        'source_url': 'https://books.google.com/books?' + urlencode({'id': volume_id}),
    }


def search_books(query):
    query = query.strip()[:200]
    if not query:
        return []
    identifier = normalize_isbn(query)
    data = api_request(params={'q': 'isbn:' + identifier if identifier else query, 'maxResults': 12, 'printType': 'books'})
    items = data.get('items') or []
    if not isinstance(items, list):
        raise BookAPIError('Google Books returned an unexpected result list.')
    return [volume for item in items if (volume := normalize_volume(item))]


def get_volume(volume_id):
    if not re.fullmatch(r'[A-Za-z0-9_-]{1,80}', volume_id):
        raise BookAPIError('Choose a valid Google Books result.')
    volume = normalize_volume(api_request('/' + volume_id))
    if not volume or volume['id'] != volume_id:
        raise BookAPIError('Google Books did not return the requested volume.')
    return volume


def refresh_cover(book):
    """Never guess a different edition from its title, or modify inventory."""
    if book.google_books_id:
        volume = get_volume(book.google_books_id)
    else:
        identifier = isbn13(book.isbn)
        if not identifier:
            raise BookAPIError('This book needs a real ISBN. For sample books, search and select the correct edition with Choose cover.')
        results = search_books(book.isbn)
        volume = next((v for v in results if v['cover_url'] and any(isbn13(i) == identifier for i in v['isbns'])), None)
    if not volume or not volume['cover_url']:
        raise BookAPIError('No matching edition with a cover was found. The existing cover was kept.')
    apply_cover(book, volume)


def apply_cover(book, volume):
    from .models import Book
    if not volume['cover_url']:
        raise BookAPIError('This edition has no cover image. Choose another result.')
    if Book.objects.exclude(pk=book.pk).filter(google_books_id=volume['id']).exists():
        raise BookAPIError('This Google Books edition is already linked to another catalog entry.')
    book.cover_url = volume['cover_url']
    book.google_books_id = volume['id']
    book.cover_updated_at = timezone.now()
    try:
        with transaction.atomic():
            book.save(update_fields=['cover_url', 'google_books_id', 'cover_updated_at'])
    except IntegrityError:
        raise BookAPIError('This edition was just linked elsewhere. Refresh the catalog before trying again.') from None


def import_volume(volume, copies):
    from .models import Book
    if not volume['isbn'] or not volume['publication_date']:
        raise BookAPIError('This result lacks a valid ISBN or publication date. Add the book manually, then choose its cover.')
    try:
        with transaction.atomic():
            existing = Book.objects.filter(google_books_id=volume['id']).first()
            existing = existing or Book.objects.filter(isbn__in=volume['isbns']).first()
            if existing:
                return existing, False
            book = Book.objects.create(title=volume['title'], author=volume['author'], isbn=volume['isbn'],
                category=volume['category'], publication_date=volume['publication_date'],
                total_copies=copies, available_copies=copies, google_books_id=volume['id'],
                cover_url=volume['cover_url'], description=volume['description'],
                cover_updated_at=timezone.now() if volume['cover_url'] else None)
            return book, True
    except IntegrityError:
        raise BookAPIError('This book was added by another request. Refresh the catalog; no stock counts were changed.') from None
