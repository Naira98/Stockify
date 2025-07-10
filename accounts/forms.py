from django import forms
from django.conf import settings
from django.core.validators import FileExtensionValidator
from django.contrib.auth.forms import UserCreationForm
from .models import User
from django.forms.widgets import FileInput


class AdminUserEditForm(forms.ModelForm):
    ROLE_CHOICES = (
        ("admin", "Admin"),
        ("employee", "Employee"),
    )

    role = forms.ChoiceField(
        choices=ROLE_CHOICES,
        required=True,
        label="User Role",
        widget=forms.RadioSelect(attrs={"class": "flex space-x-4"}),
        initial="employee",
    )

    class Meta:
        model = User
        fields = ["username", "email", "first_name", "last_name", "role"]

    def save(self, commit=True):
        user = super().save(commit=False)
        role = self.cleaned_data.get("role")

        if role == "admin":
            user.is_superuser = True
            user.is_staff = True
            user.is_user = False
        else:
            user.is_superuser = False
            user.is_staff = False
            user.is_user = True

        if commit:
            user.save()
        return user



class CustomUserCreationForm(UserCreationForm):
    ROLE_CHOICES = [
        ("admin", "Admin"),
        ("employee", "Employee"),
    ]

    role = forms.ChoiceField(
        choices=ROLE_CHOICES,
        widget=forms.RadioSelect(
            attrs={
                "class": "hidden",
            }
        ),
        initial="admin",
    )

    image = forms.ImageField(
        required=False,
        widget=FileInput(
            attrs={
                "class": "hidden",
                "id": "image-upload",
            }
        ),
    )

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2", "role", "image")
        widgets = {
            "username": forms.TextInput(
                attrs={
                    "class": "w-full px-4 py-2 rounded-lg border border-gray-300 focus:outline-none focus:ring-1 focus:ring-cyan-500",
                }
            ),
            "email": forms.EmailInput(
                attrs={
                    "class": "w-full px-4 py-2 rounded-lg border border-gray-300 focus:outline-none focus:ring-1 focus:ring-cyan-500",
                }
            ),
            "password1": forms.PasswordInput(
                attrs={
                    "class": "w-full px-4 py-2 rounded-lg border border-gray-300 focus:outline-none focus:ring-1 focus:ring-cyan-500",
                }
            ),
            "password2": forms.PasswordInput(
                attrs={
                    "class": "w-full px-4 py-2 rounded-lg border border-gray-300 focus:outline-none focus:ring-1 focus:ring-cyan-500",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name in self.fields:
            if field_name in ["password1", "password2"]:
                self.fields[field_name].help_text = ""
            if self.fields[field_name].help_text:
                self.fields[field_name].help_text = (
                    f'<span class="text-xs text-gray-500">{self.fields[field_name].help_text}</span>'
                )
            self.fields[field_name].widget.attrs.update(
                {
                    "class": "w-full px-4 py-2 rounded-lg border border-gray-300 focus:outline-none focus:ring-1 focus:ring-cyan-500"
                }
            )

    def save(self, commit=True):
        user = super().save(commit=False)
        role = self.cleaned_data.get("role")

        if role == "admin":
            user.is_staff = True
            user.is_superuser = True
        else:
            user.is_staff = False
            user.is_superuser = False

        if commit:
            user.save()
        return user


class loginForm(forms.Form):
    username = forms.CharField(max_length=150, required=True)
    password = forms.CharField(widget=forms.PasswordInput, required=True)


class ProfileEditForm(forms.ModelForm):
    # Add custom validation for image field
    image = forms.ImageField(
        required=False,
        validators=[FileExtensionValidator(["jpg", "jpeg", "png", "gif"])],
        widget=forms.FileInput(
            attrs={
                "class": "w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-medium file:bg-indigo-50 file:text-indigo-700 hover:file:bg-indigo-100"
            }
        ),
    )

    class Meta:
        model = User
        fields = ["image", "bio"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add form control classes to all fields
        for field in self.fields:
            self.fields[field].widget.attrs.update(
                {
                    "class": "w-full px-4 py-3 rounded-lg border border-gray-300 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                }
            )

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
        return user

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if email:
            email = email.lower()
            if (
                User.objects.exclude(id=self.instance.id)
                .filter(email__iexact=email)
                .exists()
            ):
                raise forms.ValidationError("This email address is already in use.")
        return email
