from django.db import models
from django.contrib.auth.models import User
from catalog.models import Book
    #create your models here.
class Loan(models.Model):
    member = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    borrow_date = models.DateField(auto_now_add=True)
    return_date = models.DateField(null=True, blank=True)

    status = models.CharField(
        max_length=20,
        choices=[
            ('borrowed', 'Borrowed'),
            ('returned', 'Returned'),
        ],
        default='borrowed'
    )

    def __str__(self):
        return f"{self.member.username} - {self.book.title}"