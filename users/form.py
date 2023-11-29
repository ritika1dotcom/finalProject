from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from users.models import UserProfile

# class SignUpForm(UserCreationForm):
#     # def __init__(self, *args, **kwargs):
#     #     super().__init__(*args, **kwargs)
#     #     # Set a unique ID for the username field in the SignUpForm
#     #     self.fields['username'].widget.attrs.update({'id': 'signup-username'})
#     class Meta:
#         model = User
#         fields = ['username', 'email', 'password1', 'password2']


class AvatarForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ('avatar',)
