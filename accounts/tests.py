from django.test import TestCase
from django.contrib.auth.models import User
from catalog.models import Book, LibraryAmbience


class ReadingRoomTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.book = Book.objects.create(title='Pride and Prejudice', author='Jane Austen',
            isbn='9780141439518', category='Classics', total_copies=2,
            available_copies=2, publication_date='1813-01-28')
        cls.other = Book.objects.create(title='The Time Machine', author='H. G. Wells',
            isbn='9780141439976', category='Science Fiction', total_copies=1,
            available_copies=0, publication_date='1895-01-01')
        cls.member = User.objects.create_user('reader', password='Test-only-Password-9371')

    def test_guest_can_browse_but_cannot_borrow(self):
        self.assertContains(self.client.get('/'), 'Pride and Prejudice')
        response = self.client.post(f'/borrow/{self.book.pk}/')
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/login/'))

    def test_initial_entrance_has_three_explicit_choices(self):
        response = self.client.get('/')
        self.assertEqual(response.context['entrance_mode'], 'choices')
        self.assertContains(response, 'Continue as guest')
        self.assertContains(response, '>Register <svg>')
        self.assertContains(response, '>Login <svg>')
        self.assertNotContains(response, 'Skip the entrance')

    def test_guest_choice_opens_once_and_is_browse_only(self):
        self.assertEqual(self.client.get('/guest/').status_code, 405)
        self.client.post('/guest/')
        response = self.client.get('/')
        self.assertEqual(response.context['entrance_mode'], 'opening')
        self.assertNotContains(response, 'class="save-book"')
        self.assertNotContains(response, 'class="dialog-save')
        self.assertNotContains(response, 'My borrowed books')
        self.assertNotIn('_auth_user_id', self.client.session)
        self.assertEqual(self.client.get('/').context['entrance_mode'], 'hidden')
        self.assertEqual(self.client.get('/?section=saved').context['section'], 'collection')
        self.assertEqual(self.client.post(f'/borrow/{self.book.pk}/').status_code, 302)
        self.book.refresh_from_db()
        self.assertEqual(self.book.available_copies, 2)

    def test_guest_choice_removes_existing_member_privileges(self):
        self.client.force_login(self.member)
        self.client.post('/guest/')
        self.assertNotIn('_auth_user_id', self.client.session)
        self.assertEqual(self.client.get('/').context['entrance_mode'], 'opening')
        self.assertEqual(self.client.post(f'/borrow/{self.book.pk}/').status_code, 302)

    def test_successful_login_replays_doors_after_guest_visit(self):
        self.client.post('/guest/')
        self.client.get('/')
        self.client.post('/login/', {'username': 'reader', 'password': 'Test-only-Password-9371'})
        response = self.client.get('/')
        self.assertEqual(response.context['entrance_mode'], 'opening')
        self.assertContains(response, 'My borrowed books')
        self.assertContains(response, 'class="save-book"')
        self.assertNotIn('library_guest', self.client.session)
        self.assertEqual(self.client.get('/').context['entrance_mode'], 'hidden')

    def test_successful_registration_opens_doors(self):
        self.client.post('/register/', {'username': 'newcard',
            'password1': 'New-Test-Library-734!', 'password2': 'New-Test-Library-734!'})
        self.assertEqual(self.client.get('/').context['entrance_mode'], 'opening')
        self.assertEqual(self.client.get('/').context['entrance_mode'], 'hidden')

    def test_unsuccessful_auth_does_not_open_doors(self):
        self.client.post('/login/', {'username': 'reader', 'password': 'wrong'})
        self.assertNotIn('library_entry_pending', self.client.session)
        response = self.client.post('/register/', {'username': 'invalidcard',
            'password1': 'short', 'password2': 'different'})
        self.assertEqual(response.status_code, 200)
        self.assertNotIn('library_entry_pending', self.client.session)
        self.assertEqual(self.client.get('/').context['entrance_mode'], 'choices')

    def test_signout_restores_entrance_choices(self):
        self.client.force_login(self.member)
        self.client.post('/logout/')
        self.assertEqual(self.client.get('/').context['entrance_mode'], 'choices')

    def test_guest_choice_requires_csrf(self):
        from django.test import Client
        client = Client(enforce_csrf_checks=True)
        self.assertEqual(client.post('/guest/').status_code, 403)
        self.assertNotIn('library_entry_pending', client.session)

    def test_category_search_sort_and_availability(self):
        response = self.client.get('/', {'q': 'Austen', 'category': 'Classics', 'sort': 'author'})
        self.assertEqual(list(response.context['books']), [self.book])
        response = self.client.get('/', {'available': '1'})
        self.assertEqual(list(response.context['books']), [self.book])
        self.assertContains(self.client.get('/', {'q': 'no-matches-xyz'}), 'No stories on this shelf')

    def test_auth_forms_render_and_report_invalid_credentials(self):
        self.assertEqual(self.client.get('/register/').status_code, 200)
        response = self.client.post('/login/', {'username': 'reader', 'password': 'wrong'})
        self.assertContains(response, 'Please enter a correct username and password')

    def test_registration_creates_member_not_admin(self):
        response = self.client.post('/register/', {'username': 'newreader',
            'password1': 'New-Test-Library-734!', 'password2': 'New-Test-Library-734!'})
        self.assertRedirects(response, '/')
        self.assertFalse(User.objects.get(username='newreader').is_staff)

    def test_login_rejects_external_redirect(self):
        response = self.client.post('/login/', {'username': 'reader',
            'password': 'Test-only-Password-9371', 'next': 'https://example.com/'})
        self.assertRedirects(response, '/')

    def test_only_staff_can_edit_music(self):
        self.client.force_login(self.member)
        self.assertEqual(self.client.get('/admin/catalog/libraryambience/').status_code, 302)
        self.assertEqual(self.client.post('/admin/catalog/libraryambience/add/', {'title':'Changed'}).status_code, 302)
        self.assertFalse(LibraryAmbience.objects.exists())
        staff = User.objects.create_superuser('librarian', password='Test-Library-7951')
        self.client.force_login(staff)
        response = self.client.post('/admin/catalog/libraryambience/add/', {
            'title': 'Evening jazz', 'artist': 'Local quartet', 'audio_url': 'https://example.com/evening.mp3', 'enabled': 'on', '_save': 'Save'})
        self.assertEqual(response.status_code, 302)
        self.assertContains(self.client.get('/'), 'Evening jazz')

    def test_disabled_soundtrack_has_no_audio_element(self):
        LibraryAmbience.objects.create(enabled=False)
        self.assertNotContains(self.client.get('/'), '<audio')

    def test_logout_requires_post(self):
        self.client.force_login(self.member)
        self.assertEqual(self.client.get('/logout/').status_code, 405)
        self.assertRedirects(self.client.post('/logout/'), '/')
