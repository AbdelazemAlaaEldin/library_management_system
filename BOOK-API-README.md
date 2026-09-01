# Google Books covers and catalog

The library now has a Google Books integration like the metadata/image integration used by movie apps. Google Books supplies book metadata and cover URLs; your existing SQLite database remains the source of truth for your library's books, copies, and loans.

## Connect your key

1. In [Google Cloud](https://console.cloud.google.com/apis/library/books.googleapis.com), select or create a project and enable **Books API**.
2. Open [Credentials](https://console.cloud.google.com/apis/credentials), create an API key, and restrict it to **Books API**. This integration makes server requests; a browser-referrer-restricted key will not work. For a production server with a stable outbound IP, configure appropriate server IP restrictions as well.
3. Open [Book API settings](http://127.0.0.1:8000/admin/catalog/book/api-settings/), sign in as a superuser, paste the key into the password field, and click **Save key**.
4. Click **Test saved key**. If Google rejects it, check that Books API is enabled and review key restrictions and quota.

Use a Google Books API key, not your TMDB key. Do not paste credentials into chat.

No key existed in the project at implementation time. The integration has been tested with mocked Google responses; fetching live API covers requires your own configured key. No live Google API calls using your account have been made.

If you do not have an administrator account yet, open PowerShell in:

`C:\Users\Pikaa\pikagraphics\library_management_system-main\library_management_system-main`

and run:

```powershell
..\.venv\Scripts\python.exe manage.py createsuperuser
```

Choose your own username and password. No default admin account or password has been created.

## Search and import books

Open **Librarian's desk → Books → Search Google Books**.

- Search by title, author, or ISBN.
- Review the book's cover, author, edition, publication year, and ISBN. The source link opens that edition on Google Books.
- Enter **Copies owned** and click **Import book**. The default is 0: finding a book in an API does not mean your library owns a copy.
- Existing ISBNs or linked Google volume IDs are not duplicated, and importing an existing book does not increase its copy counts.
- Results without a valid ISBN or usable publication date must be added manually, then linked to a cover. For API dates containing only a year or month, the stored date uses January/day 1 for the missing parts; correct it in the editor if exact dates matter.

The title, author, ISBN, category, description, cover URL, and Google Books ID are saved in the database. Availability and borrowing continue to use your local inventory.

## Add covers to existing books

Open **Books → select a book → Choose cover from Google Books**. Search for the right title and author, check the edition, then click **Use this cover**.

This is also the correct way to handle the 12 sample books: their `SAMPLE...` IDs are not ISBNs, so the app intentionally does not guess an edition automatically. Choosing a cover does not replace sample IDs with real ISBNs or change stock counts. Edit the inventory record separately when you replace the sample data with real books.

For an existing book with a real ISBN or a linked Google Books ID, click **Refresh cover from Google Books**. The bulk action supports up to 5 books at once.

For larger collections:

```powershell
..\.venv\Scripts\python.exe manage.py sync_book_covers --missing-only --limit 50
```

Or refresh one record:

```powershell
..\.venv\Scripts\python.exe manage.py sync_book_covers --book-id 1
```

Automatic refresh uses the exact ISBN (including equivalent ISBN-10/13) or an already selected Google volume. It never silently chooses a different edition by title. If no matching cover is found, the old cover stays unchanged.

## Cover display and limitations

- Real images appear in collection cards, book details, and borrowed-book thumbnails.
- Images are served from the provider's servers; the database stores URLs, not the image binaries. Images still require an internet connection.
- Missing, broken, or unavailable images fall back to the original decorative book design.
- Cover selection and refresh do not change book details, availability, or loan records.
- Google Books does not guarantee coverage for every book or edition. You can also enter an HTTPS URL for a cover you have permission to use in the book editor.
- Public catalog browsing never performs Google API searches or exposes the API key. Only authorized librarians can search, import, or refresh; guests remain browse-only.

## Key storage

Admin-entered keys are stored in `book_api.local.toml` in the project directory, outside static/media and excluded from version control. This file is not exposed by a public route. The key is never filled back into the settings form or included in cover links. It is stored as plaintext on disk, like a local environment file; protect project-folder permissions and backups. Only superusers can change it.

Alternatively, configure `GOOGLE_BOOKS_API_KEY` in the server environment before starting the app. That value overrides the local file and cannot be changed through the admin page. `book_api.example.toml` provides a blank file template for manual local setup.

The project is still a local development app. Before deploying, configure the existing Django production settings, HTTPS, secure secret management, and proper static/media serving.

## Verification

45 tests pass, including the original account/entrance/loan tests and new checks for key privacy, permissions, CSRF protection, safe provider URLs, network failures, ISBN matching, duplicate imports, inventory preservation, stored image rendering, and no API requests during public browsing. Database migrations apply cleanly.

Official references:

- [Google Books API usage and key setup](https://developers.google.com/books/docs/v1/using)
- [Google Books volume metadata and image fields](https://developers.google.com/books/docs/v1/reference/volumes)
