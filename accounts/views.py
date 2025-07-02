from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm, ProfileEditForm  
from django.conf import settings
from .models import User  
from django.views.decorators.csrf import csrf_protect




# def login_view(request):
#     if request.method == 'POST':
#         form = loginForm(request.POST)
#         if form.is_valid():
#             username = form.cleaned_data['username']
#             password = form.cleaned_data['password']
#             if user := authenticate(request, username=username, password=password):
#                 login(request, user)
#                 return redirect('home')
#             else:
#                 form.add_error(None, 'Invalid login credentials')
#     else:
#         form = loginForm()
#     return render(request, 'accounts/login.html', {'form': form})

@login_required
def edit_profile_view(request):
    user = request.user
    if request.method == 'POST':
        form = ProfileEditForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = ProfileEditForm(instance=user)
    return render(request, 'accounts/edit_profile.html', {'form': form})


# TODO Rename this here and in `login_view`
# def _extracted_from_login_view_(form, request):
#     username = form.cleaned_data['username']
#     password = form.cleaned_data['password']
#     user = authenticate(request, username=username, password=password)
#     if not user:
#         return render(request, 'accounts/login.html', {'form': form, 'error': 'Invalid credentials'})
#     login(request, user)
#     return redirect('home')



@csrf_protect
def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST, request.FILES)
        if not form.is_valid():
            return render(request, 'accounts/register.html', {'form': form})
        user = form.save()
        login(request, user)
        return redirect('home')
    else:
        form = CustomUserCreationForm()
    return render(request, 'accounts/register.html', {'form': form})


@login_required
def profile_view(request):
    return render(request, 'accounts/profile.html', {'user': request.user})





def home_view(request):
    if not request.user.is_authenticated:
        return redirect('login')
    return render(request, 'accounts/home.html', {'user': request.user})
def logout_view(request):
    if request.method == 'POST':
        logout(request)
        return redirect('login')