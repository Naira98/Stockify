from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from .forms import ProfileEditForm, AdminUserEditForm
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator
from .forms import AdminUserCreationForm
from django.contrib.admin.views.decorators import staff_member_required
from .models import User

@login_required
@staff_member_required
def user_management_view(request):
    users = User.objects.all().order_by("-date_joined")

    # Pagination
    paginator = Paginator(users, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    if request.method == "POST":
        form = AdminUserCreationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            messages.success(request, f"User {user.username} created successfully!")
            return redirect("accounts:user_management")
    else:
        form = AdminUserCreationForm()

    return render(
        request,
        "accounts/user_management.html",
        {"users": page_obj, "form": form, "page_obj": page_obj},
    )


@login_required
@staff_member_required
def edit_user_admin_view(request, user_id):
    user_to_edit = get_object_or_404(User, id=user_id)

    if request.method == "POST":
        form = AdminUserEditForm(request.POST, request.FILES, instance=user_to_edit)
        if form.is_valid():
            form.save()
            messages.success(
                request, f"User {user_to_edit.username} updated successfully!"
            )
            return redirect("accounts:user_management")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = AdminUserEditForm(instance=user_to_edit)

    return render(
        request,
        "accounts/admin_edit_user.html",
        {"form": form, "user_to_edit": user_to_edit},
    )


@login_required
@staff_member_required
def delete_user_view(request, user_id):
    if request.user.id == user_id:
        messages.error(request, "You cannot delete your own account!")
        return redirect("accounts:user_management")

    user = get_object_or_404(User, id=user_id)
    if request.method == "POST":
        username = user.username
        user.delete()
        messages.success(request, f"User {username} deleted successfully!")
        return redirect("accounts:user_management")

    return render(request, "accounts/confirm_delete.html", {"user": user})


@login_required
def profile_view(request):
    return render(request, "accounts/profile.html", {"user": request.user})


@login_required
def edit_profile_view(request):
    if request.method == "POST":
        form = ProfileEditForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Your profile has been updated successfully!")
            return redirect("accounts:profile")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = ProfileEditForm(instance=request.user)

    return render(request, "accounts/edit_profile.html", {"form": form})
