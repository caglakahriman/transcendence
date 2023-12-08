from django import forms

class RegistrationForm(forms.Form):
    login = forms.CharField(label='Username', max_length=10)
    token = forms.CharField(label='Password', max_length=100, widget=forms.PasswordInput)

class ProfileForm(forms.Form):
    login = forms.CharField(label='New Username', max_length=10, required=False)
    avatar = forms.ImageField(label='New Avatar', required=False)

