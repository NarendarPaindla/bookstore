from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Review

class SignupForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        help_text='',
        widget=forms.EmailInput(attrs={
            'placeholder': 'Email Address',
            'class': 'form-input',
            'id': 'id_email'
        })
    )
    username = forms.CharField(
        max_length=150,
        help_text='',
        widget=forms.TextInput(attrs={
            'placeholder': 'Username',
            'class': 'form-input',
            'id': 'id_username'
        })
    )
    password1 = forms.CharField(
        label='Password',
        help_text='',
        widget=forms.PasswordInput(attrs={
            'placeholder': 'At least 8 characters',
            'class': 'form-input',
            'id': 'id_password1'
        })
    )
    password2 = forms.CharField(
        label='Confirm Password',
        help_text='',
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Repeat password',
            'class': 'form-input',
            'id': 'id_password2'
        })
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating','text']
        widgets = {
            'rating': forms.RadioSelect(attrs={'class':'star-rating'}),
            'text':   forms.Textarea(attrs={'rows':4, 'class':'form-input'}),
        }
        labels = {
            'text': 'Your Review',
        }