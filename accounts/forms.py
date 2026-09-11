from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile


from django.conf import settings

class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    role = forms.ChoiceField(
        choices=[('member', 'Reader'), ('librarian', 'Librarian / Admin')],
        initial='member',
        widget=forms.RadioSelect,
    )
    access_code = forms.CharField(
        required=False,
        label='Librarian access code',
        widget=forms.PasswordInput(attrs={'autocomplete': 'off'}),
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def clean(self):
        cleaned = super().clean()
        if cleaned.get('role') == 'librarian':
            code = cleaned.get('access_code', '')
            if not code or code != settings.LIBRARIAN_ACCESS_CODE:
                self.add_error('access_code', 'This access code is not correct.')
        return cleaned

    def save(self, commit=True):
        user = super().save(commit=False)
        if self.cleaned_data.get('role') == 'librarian':
            user.is_staff = True
        if commit:
            user.save()
        return user


class AvatarClearableFileInput(forms.ClearableFileInput):
    template_name = 'accounts/widgets/avatar_input.html'


class AvatarUploadForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['avatar']
        widgets = {
            'avatar': AvatarClearableFileInput(attrs={
                'accept': 'image/*',
                'id': 'id_avatar',
                'hidden': True,
            })
        }