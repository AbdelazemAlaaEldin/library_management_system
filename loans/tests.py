from django.test import TestCase
from django.contrib.auth.models import User
from catalog.models import Book
from .models import Loan


class BorrowingTests(TestCase):
    def setUp(self):
        self.member = User.objects.create_user('reader')
        self.other = User.objects.create_user('anotherreader')
        self.book = Book.objects.create(title='A library book', author='An author',
            isbn='1234567890123', category='Fiction', total_copies=1,
            available_copies=1, publication_date='2020-01-01')
        self.client.force_login(self.member)

    def test_borrow_and_return_change_inventory_exactly_once(self):
        url = f'/borrow/{self.book.pk}/'
        self.assertEqual(self.client.get(url).status_code, 405)
        self.client.post(url)
        self.client.post(url)
        self.book.refresh_from_db()
        self.assertEqual(self.book.available_copies, 0)
        self.assertEqual(Loan.objects.filter(status='borrowed').count(), 1)
        loan = Loan.objects.get()
        self.assertContains(self.client.get('/?section=loans'), 'A library book')
        self.assertEqual(self.client.get(f'/return/{loan.pk}/').status_code, 405)
        self.client.post(f'/return/{loan.pk}/')
        self.client.post(f'/return/{loan.pk}/')
        self.book.refresh_from_db()
        loan.refresh_from_db()
        self.assertEqual(self.book.available_copies, 1)
        self.assertEqual(loan.status, 'returned')
        self.assertIsNotNone(loan.return_date)

    def test_cannot_borrow_unavailable_book(self):
        self.book.available_copies = 0
        self.book.save()
        self.client.post(f'/borrow/{self.book.pk}/')
        self.assertFalse(Loan.objects.exists())

    def test_other_member_cannot_view_or_return_private_loan(self):
        self.client.post(f'/borrow/{self.book.pk}/')
        loan = Loan.objects.get()
        self.client.force_login(self.other)
        self.assertNotContains(self.client.get('/?section=loans'), 'Borrowed Jan')
        self.assertEqual(len(self.client.get('/?section=loans').context['loans']), 0)
        self.assertEqual(self.client.post(f'/return/{loan.pk}/').status_code, 404)
        loan.refresh_from_db()
        self.assertEqual(loan.status, 'borrowed')

    def test_csrf_required_for_borrow(self):
        from django.test import Client
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.member)
        self.assertEqual(client.post(f'/borrow/{self.book.pk}/').status_code, 403)
        self.assertFalse(Loan.objects.exists())
