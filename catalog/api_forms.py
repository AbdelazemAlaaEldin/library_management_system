from django import forms


class APIKeyForm(forms.Form):
    api_key = forms.CharField(label='Google Books API key', required=False, max_length=200,
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password', 'spellcheck': 'false'}),
        help_text='Leave blank to keep the existing key. Never enter a TMDB key here.')
    clear_key = forms.BooleanField(label='Remove the saved local key', required=False)

    def clean(self):
        data = super().clean()
        if data.get('api_key') and data.get('clear_key'):
            raise forms.ValidationError('Choose either a replacement key or removal, not both.')
        return data


class VolumeImportForm(forms.Form):
    volume_id = forms.RegexField(regex=r'^[A-Za-z0-9_-]{1,80}$', max_length=80)
    copies = forms.IntegerField(min_value=0, max_value=10000, initial=0)


class CoverSelectionForm(forms.Form):
    volume_id = forms.RegexField(regex=r'^[A-Za-z0-9_-]{1,80}$', max_length=80)
