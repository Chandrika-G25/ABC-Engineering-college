from django import forms
from django.contrib.auth import authenticate
from .models import User

class UserLoginForm(forms.Form):
    username = forms.CharField(
        label="Username or Email",
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Enter Username or Email',
            'autocomplete': 'username',
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Enter Password',
            'autocomplete': 'current-password',
        })
    )

    def clean(self):
        cleaned_data = super().clean()
        username_or_email = cleaned_data.get('username')
        password = cleaned_data.get('password')

        if username_or_email and password:
            user_obj = None
            if '@' in username_or_email:
                user_obj = User.objects.filter(email__iexact=username_or_email).first()
            if not user_obj:
                user_obj = User.objects.filter(username__iexact=username_or_email).first()

            if user_obj:
                authenticated_user = authenticate(username=user_obj.username, password=password)
                if authenticated_user:
                    cleaned_data['user'] = authenticated_user
                    return cleaned_data

            raise forms.ValidationError("Invalid credentials. Please check your username/email and password.")

        return cleaned_data

    def get_user(self):
        return self.cleaned_data.get('user')


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone', 'address', 'profile_picture']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'First Name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Last Name'}),
            'email': forms.EmailInput(attrs={'class': 'form-input', 'placeholder': 'Email Address'}),
            'phone': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Phone Number'}),
            'address': forms.Textarea(attrs={'class': 'form-input', 'rows': 3, 'placeholder': 'Full Address'}),
            'profile_picture': forms.FileInput(attrs={'class': 'form-file-input'}),
        }
