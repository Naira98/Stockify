from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm, ProfileEditForm  
from django.conf import settings
from .models import User  
from django.views.decorators.csrf import csrf_protect # Ensure CSRF protection for the registration view


@login_required
def edit_profile_view(request):
    user = request.user
    if request.method == 'POST':
        # Include request.FILES for image uploads
        form = ProfileEditForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ProfileEditForm(instance=user)
    
    # Pass form to template context
    return render(request, 'accounts/edit_profile.html', {
        'form': form,
        'user': user
    })


@csrf_protect 
def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save(commit=False)
            
            # Handle admin registration (only in development)
            if settings.DEBUG and form.cleaned_data.get('is_admin', False):
                user.is_staff = True
                user.is_superuser = True
            
            user.save()
            login(request, user)
            return redirect('home')
        else:
            return render(request, 'accounts/register.html', {
                'form': form,
                'DEBUG': settings.DEBUG
            })
    else:
        form = CustomUserCreationForm()
        return render(request, 'accounts/register.html', {
            'form': form,
            'DEBUG': settings.DEBUG
        })



@login_required
def profile_view(request):
    return render(request, 'accounts/profile.html', {'user': request.user})





def home_view(request):
    if not request.user.is_authenticated:
        return redirect('login')
    return render(request, 'accounts/home.html', {'user': request.user})

def logout_view(request):
    logout(request)
    return redirect('login')