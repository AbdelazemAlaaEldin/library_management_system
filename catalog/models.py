from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator, URLValidator

# Create your models here.

class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=100)
    isbn = models.CharField(max_length=13, unique=True)
    category = models.CharField(max_length=100)
    total_copies = models.PositiveIntegerField()
    available_copies = models.PositiveIntegerField()
    publication_date = models.DateField()
    cover_url = models.URLField(max_length=1000, blank=True, validators=[URLValidator(schemes=['https'])],
        help_text='HTTPS cover image URL. Filled by Google Books, or supply your own licensed cover.')
    google_books_id = models.CharField(max_length=80, blank=True, null=True, unique=True, editable=False)
    description = models.TextField(blank=True)
    cover_updated_at = models.DateTimeField(blank=True, null=True, editable=False)

    @property
    def cover_source_url(self):
        if self.google_books_id:
            from urllib.parse import urlencode
            return 'https://books.google.com/books?' + urlencode({'id': self.google_books_id})
        return ''
   
    def __str__(self):
        return self.title


class LibraryAmbience(models.Model):
    """One librarian-controlled soundtrack, shared by all visitors."""
    title = models.CharField(max_length=150, default='A quiet afternoon')
    artist = models.CharField(max_length=150, default='The Reading Room')
    audio_file = models.FileField(
        upload_to='library_music/', blank=True,
        validators=[FileExtensionValidator(['mp3', 'wav', 'ogg', 'm4a'])],
        help_text='Upload music you have permission to use. Maximum 20 MB.',
    )
    audio_url = models.URLField(blank=True, help_text='Or use a direct HTTPS audio URL, not a streaming-service page.')
    enabled = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Library soundtrack'
        verbose_name_plural = 'Library soundtrack'

    def clean(self):
        if self.audio_file and self.audio_url:
            raise ValidationError('Choose an uploaded file OR an audio URL, not both.')
        if self.audio_url and not self.audio_url.startswith('https://'):
            raise ValidationError({'audio_url': 'Use an HTTPS audio URL.'})
        if self.audio_file and self.audio_file.size > 20 * 1024 * 1024:
            raise ValidationError({'audio_file': 'Please choose a file smaller than 20 MB.'})

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title
