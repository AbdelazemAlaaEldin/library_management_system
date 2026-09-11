from django import forms
from .models import Book


class ManualBookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = [
            'title', 'author', 'isbn', 'category',
            'total_copies', 'available_copies',
            'publication_date', 'cover_url', 'description',
        ]
        widgets = {
            'publication_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 4}),
        }

    def clean(self):
        cleaned = super().clean()
        total = cleaned.get('total_copies')
        available = cleaned.get('available_copies')
        if total is not None and available is not None and available > total:
            raise forms.ValidationError('Available copies cannot exceed total copies.')
        return cleaned