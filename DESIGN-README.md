# The Reading Room

A warm, wooden redesign of your existing Django Library Management System.

## Open the app

Local preview: http://127.0.0.1:8000/

Project directory:
`C:\Users\Pikaa\pikagraphics\library_management_system-main\library_management_system-main`

The app is running locally. To start it again, open PowerShell in the project directory and run:

```powershell
.\Start-Library.ps1
```

Or use the existing Python environment directly:

```powershell
..\.venv\Scripts\python.exe manage.py migrate
..\.venv\Scripts\python.exe manage.py runserver 127.0.0.1:8000
```

## What's included

- Three entrance choices: Continue as guest, Register, and Login. The double wooden doors open after the guest choice or successful registration/login. Invalid forms stay open. Reduced-motion support is preserved.
- Walnut navigation, parchment backgrounds, brass details, and original library-room imagery with tables, chairs, and warm reading lamps.
- Book-style covers, search by title/author/ISBN, category filtering, availability filtering, sorting, and grid/list views.
- Book detail dialogs, working membership/sign-in, borrowing and returns, and a private borrowing shelf.
- Guests can browse and search the collection and see availability, but cannot borrow or save books. Members have a browser-local saved-for-later shelf; bookmarks do not sync between devices or accounts.
- A vintage record player with play/pause, volume, mute, and an original 40-second ambient piano loop.
- Music starts only when the visitor clicks play. Page navigation pauses playback; the volume preference is remembered.
- A matching design for login and registration.

## Change the music as admin

No admin account existed in the original database. Create your own administrator once, from the project directory:

```powershell
..\.venv\Scripts\python.exe manage.py createsuperuser
```

Choose your own username and secure password when prompted. No default admin password has been added.

Then open http://127.0.0.1:8000/admin/ and choose **Library soundtrack**.
Change the track title and artist, upload an MP3/WAV/OGG/M4A file (up to 20 MB), or provide a direct HTTPS audio URL. Choose a file OR a URL, not both. Turn off **Enabled** for silence. Save changes; visitors get the updated soundtrack on their next page load. Only staff with the appropriate Django permissions can change it.

Use music you own or have permission to play. Streaming-service webpage links are not direct audio files. Hosted audio must be accessible to visitors' browsers.

## Books and sample data

The original catalog was empty. The preview includes 12 clearly identified sample records to demonstrate the design. Sample IDs start with `SAMPLE`; they are not real ISBNs, and dates/copy counts are demonstration values. Replace them with your actual inventory in **Librarian's desk → Books**. Covers are original typographic UI designs, not official publisher covers.

The optional `manage.py seed_demo` command only fills an empty catalog and never overwrites existing records. No existing accounts or loans were changed. A pre-edit backup was saved in the task's `work/original-app` folder.

## Implementation and verification

Uses the existing Django 6.1 project, SQLite, Django templates, plain CSS, and JavaScript. No frontend build service is required. The existing requirements were preserved.

```powershell
..\.venv\Scripts\python.exe manage.py check
..\.venv\Scripts\python.exe manage.py test
```

23 tests pass, including entrance choices, successful/failed login and registration, guest permissions, one-time door animation, and catalog filtering, registration/sign-in, safe redirects, private loan visibility, POST-only borrowing/returns/logout, CSRF, inventory accounting, admin-only soundtrack editing, and audio validation. The entrance, book details, category filter, player, and bookmark flow were checked in the browser. The updated three-choice entrance, links to both authentication forms, and guest door-opening flow were also verified.

This is a local development app, not a production deployment. Existing development settings remain enabled. Before hosting, configure a private secret key, DEBUG=False, allowed hosts, HTTPS, and proper static/media serving. Uploaded audio should be served from a separate media origin in production. Google Fonts requires an internet connection; system serif/sans fonts are fallbacks. Library art and the default music are stored locally.

## Artwork and audio provenance

The original library image was created using the built-in imagegen tool. Its project path is:
`accounts/static/library/images/reading-room.png`

Prompt:
"Use case: photorealistic-natural. Asset type: wide background photograph for a literary library management web app named The Reading Room. Create a cinematic warmly lit old English library interior, dark walnut floor-to-ceiling bookshelves with richly colored antique books, a long polished wooden reading table and elegant wooden chairs in the foreground, brass and green shaded banker lamps, tall arched windows at the right with soft late afternoon light, a comfortable forest green leather armchair, intricate wooden paneling, cozy timeless scholarly atmosphere. Wide landscape 3:2 composition, strong room depth, right two thirds hold the most interesting furniture and window detail, left third darker shelving with uncluttered shadow for a text overlay. Photoreal editorial architectural photography, walnut brown, deep olive green, amber and parchment, rich details, tasteful, natural. No people, no text, no letters, no watermark, no logos. This is a real-looking room background, not a UI mockup."

The default ambient track was synthesized specifically for this app using an original piano-like chord pattern. It uses no third-party recording or music service.


## Book-cover API update

Google Books integration is now available in Librarian's desk → Books. Superusers can configure a key in Book API settings; librarians can search/import books and choose or refresh real covers. See BOOK-API-README.md in the project, or Book-API-Setup.md in the task outputs, for setup and limitations. Your existing inventory and loan data are preserved. The test suite now has 45 passing tests.
