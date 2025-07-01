from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout
from django.contrib.auth import get_user_model
User = get_user_model()
# Create your views here.


def login_view(request):
    if request.method != 'POST':
        return render(request, 'accounts/login.html')
    
    username = request.POST.get('username')
    password = request.POST.get('password')
    
    user = User.objects.filter(username=username).first()
    
    if user and user.check_password(password):
        user.backend = 'django.contrib.auth.backends.ModelBackend'
        login(request, user)
        return redirect('home')  # Redirect to a home page or dashboard
    
    return render(request, 'accounts/login.html', {'error': 'Invalid credentials'})
    
@login_required
def profile_view(request):
    user = request.user
    return render(request, 'accounts/profile.html', {'user': user})

@login_required
def edit_profile_view(request):
    user = request.user
    if request.method == 'POST':
        user.username = request.POST.get('username')
        user.email = request.POST.get('email')
        # Only set image if the user model has an 'image' attribute
        if 'profile_image' in request.FILES and hasattr(user, 'image'):
            user.image = request.FILES['profile_image']
        user.save()
        return redirect('profile')  # Redirect to the profile page after editing
    return render(request, 'accounts/edit_profile.html', {'user': user})

def logout_view(request):
    if request.method == 'POST':
        logout(request)
        return redirect('login')  # Redirect to the login page after logout
    return redirect('login')

def register_view(request):
    """
    Handle user registration by creating a new user and logging them in.
    """
    if request.method != 'POST':
        return render(request, 'accounts/register.html')

    username = request.POST.get('username')
    password = request.POST.get('password')
    email = request.POST.get('email')

    # Basic validation
    if not username or not password or not email:
        return render(request, 'accounts/register.html', {'error': 'All fields are required.'})

    try:
        user = User.objects.create_user(username=username, password=password, email=email)
        login(request, user)  # Automatically log in the user after registration
        return redirect('home')  # Redirect to a home page or dashboard
    except Exception as e:
        return render(request, 'accounts/register.html', {'error': f'Error creating user: {str(e)}'})

    