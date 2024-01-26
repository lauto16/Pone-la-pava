from django import forms


class Register(forms.Form):
    username = forms.CharField(label="", max_length=148, widget=forms.TextInput(
        attrs={'placeholder': 'Nombre de usuario'}))
    email = forms.EmailField(label="", max_length=100, widget=forms.TextInput(
        attrs={'placeholder': 'Correo electrónico'}))
    password = forms.CharField(label="", max_length=100, widget=forms.PasswordInput(
        attrs={'placeholder': 'Contraseña'}))
    password_repeat = forms.CharField(label="", max_length=100, widget=forms.PasswordInput(
        attrs={'placeholder': 'Repetir contraseña'}))


class Login(forms.Form):
    username = forms.CharField(label="", max_length=148, widget=forms.TextInput(
        attrs={'placeholder': 'Nombre de usuario'}))
    password = forms.CharField(label="", max_length=100, widget=forms.PasswordInput(
        attrs={'placeholder': 'Contraseña'}))
