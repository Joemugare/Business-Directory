from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .forms import UserRegistrationForm, UserLoginForm

def user_login(request):
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            user = authenticate(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password']
            )
            if user:
                login(request, user)
                next_url = request.GET.get('next', 'accounts:dashboard')
                return redirect(next_url)
            else:
                form.add_error(None, 'Invalid username or password')
        return render(request, 'accounts/login.html', {'form': form})
    else:
        form = UserLoginForm()
        return render(request, 'accounts/login.html', {'form': form, 'next': request.GET.get('next', '')})

def user_register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('accounts:login')
        else:
            form = UserRegistrationForm()
        return render(request, 'accounts/register.html', {'form': form})
    else:
        form = UserRegistrationForm()
        return render(request, 'accounts/register.html', {'form': form})

@login_required
def user_profile(request):
    return render(request, 'accounts/profile.html', {'user': request.user})

@login_required
def user_dashboard(request):
    return render(request, 'accounts/dashboard.html', {'user': request.user})