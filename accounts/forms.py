from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.conf import settings
from django.core.validators import FileExtensionValidator
from .models import User

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField()
    image = forms.ImageField(
        required=False,
        widget=forms.ClearableFileInput(attrs={'accept': 'image/*'})
    )
    terms = forms.BooleanField(
        required=True,
        label='I agree to the Terms and Conditions',
        error_messages={
            'required': 'You must agree to the terms and conditions to register.'
        }
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        if settings.DEBUG:
            self.fields['is_admin'] = forms.BooleanField(
                required=False,
                label='Register as Administrator',
                help_text='(Only available in development mode)'
            )

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'image']
    
    def clean_email(self):
        email = self.cleaned_data.get('email').lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("This email address is already in use.")
        return email
class loginForm(forms.Form):
    username = forms.CharField(max_length=150, required=True)
    password = forms.CharField(widget=forms.PasswordInput, required=True)
    


class ProfileEditForm(forms.ModelForm):
    # Add custom validation for image field
    image = forms.ImageField(
        required=False,
        validators=[FileExtensionValidator(['jpg', 'jpeg', 'png', 'gif'])],
        widget=forms.FileInput(attrs={'class': 'w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-medium file:bg-indigo-50 file:text-indigo-700 hover:file:bg-indigo-100'})
    )
    
    class Meta:
        model = User
        fields = ['username', 'email', 'image', 'first_name', 'last_name', 'bio']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add form control classes to all fields
        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent'
            })
        
        # Add specific attributes to email field
        self.fields['email'].widget.attrs.update({
            'type': 'email',
            'required': 'required'
        })