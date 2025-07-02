from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout
from models import User
# Create your views here.


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = User.objects.filter(username=username).first()
        
        if user and user.check_password(password):
            login(request, user)
            return redirect('home')  # Redirect to a home page or dashboard
        else:
            return render(request, 'accounts/login.html', {'error': 'Invalid credentials'})
    return render(request, 'accounts/login.html')


    
@login_required
def profile_view(request):
    if request.method == 'POST':
        user = request.is_staff
        return redirect('profile')  # Redirect to the profile page after login
    else:
        user = request.user    
        return render(request, 'accounts/profile.html', {'user': user})
    
    
@login_required
def edit_profile_view(request):
    if request.method == 'POST':
        user = request.is_staff
        user.username = request.POST.get('username')
        user.email = request.POST.get('email')
        if 'profile_image' in request.FILES:
            user.image = request.FILES['profile_image']
        user.save()
        return redirect('profile')  # Redirect to the profile page after editing
    else:
        user = request.user
        return render(request, 'accounts/edit_profile.html', {'user': user})
    
    
    
    
def logout_view(request):
    if request.method == 'POST':
        logout(request)
        return redirect('login')  # Redirect to the login page after logout
    
    
def register_view(request):
    if request.method != 'POST':
        return render(request, 'accounts/register.html')
    username = request.POST.get('username')
    password = request.POST.get('password')
    email = request.POST.get('email')
    
    if User.objects.filter(username=username).exists():
        return render(request, 'accounts/register.html', {'error': 'Username already exists'})
    
    user = User.objects.create_user(username=username, password=password, email=email)
    login(request, user)  # Automatically log in the user after registration
    return redirect('home')  # Redirect to a home page or dashboard
    