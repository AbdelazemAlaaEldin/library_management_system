from django.templatetags.static import static
from .models import LibraryAmbience


def library_ambience(request):
    ambience = LibraryAmbience.objects.first()
    source = static('library/audio/quiet-afternoon.wav')
    if ambience:
        source = ambience.audio_file.url if ambience.audio_file else (ambience.audio_url or source)
    return {'ambience': {
        'title': ambience.title if ambience else 'A quiet afternoon',
        'artist': ambience.artist if ambience else 'The Reading Room',
        'enabled': ambience.enabled if ambience else True,
        'source': source,
    }}
