from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm


class SignUpForm(UserCreationForm):
    class Meta:
        fields = ('username', 'email', 'password1', 'password2', 'is_tutor')
        model = get_user_model()
        labels = {
            'is_tutor': 'Are you a Tutor ?'
        }

        def __init__(self, *args, **kargs):
            super().__init__(self, *args, **kargs)
            self.fields['username'].label = 'Display Name'
            self.fields['email'].label = 'Email Address'


class LoginForm(forms.Form):
    username = forms.CharField(max_length=10, required=True)
    password = forms.CharField(min_length=8, widget=forms.PasswordInput(), required=True)

