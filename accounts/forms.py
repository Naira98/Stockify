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

    
    ROLE_CHOICES = (
        ('admin', 'Manager'),
        ('user', 'Employee'),
    )
    
    role = forms.ChoiceField(
        choices=ROLE_CHOICES,
        required=True,
        label='Register as',
        widget=forms.RadioSelect(attrs={'class': 'flex space-x-4'}),
        initial='user'
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'is_admin' in self.fields:
            del self.fields['is_admin']
        
        if settings.DEBUG:
            self.fields['role'].help_text = '(Only available in development mode)'
        else:
            self.fields['role'].widget = forms.HiddenInput()
            self.fields['role'].initial = 'user'

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'image', 'role']

    def save(self, commit=True):
        user = super().save(commit=False)
        role = self.cleaned_data.get('role')
        
        if role == 'admin':
            user.is_superuser = True
            user.is_staff = True
        else:
            user.is_user = True
        
        if commit:
            user.save()
        return user
    
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