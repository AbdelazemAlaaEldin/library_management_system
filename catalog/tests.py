from django.test import TestCase
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from .models import LibraryAmbience


class SoundtrackValidationTests(TestCase):
    def test_rejects_unsafe_or_ambiguous_audio(self):
        for ambience in (
            LibraryAmbience(audio_url='http://example.com/music.mp3'),
            LibraryAmbience(audio_file=SimpleUploadedFile('script.html', b'<script>test</script>')),
            LibraryAmbience(audio_file=SimpleUploadedFile('music.wav', b'RIFF'), audio_url='https://example.com/music.mp3'),
        ):
            with self.subTest(ambience=ambience.audio_url):
                with self.assertRaises(ValidationError):
                    ambience.full_clean()

    def test_rejects_oversize_file(self):
        upload = SimpleUploadedFile('music.mp3', b'a')
        upload.size = 21 * 1024 * 1024
        with self.assertRaises(ValidationError):
            LibraryAmbience(audio_file=upload).full_clean()

    def test_singleton_soundtrack(self):
        LibraryAmbience.objects.create(title='Morning')
        LibraryAmbience(title='Evening').save()
        self.assertEqual(LibraryAmbience.objects.count(), 1)
        self.assertEqual(LibraryAmbience.objects.get().title, 'Evening')
