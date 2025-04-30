from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import CustomSignupForm, CustomLoginForm, UserProfileForm
from .models import User

def home_view(request):
    """
    Home page view
    """
    if request.user.is_authenticated:
        return redirect('dashboard')
    return redirect('dashboard')  # Redirect to the dashboard view instead


def login_view(request):
    """
    Login view
    """
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = CustomLoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('login')
            password = form.cleaned_data.get('password')
            remember_me = form.cleaned_data.get('remember_me')
            
            user = authenticate(request, email=email, password=password)
            if user is not None:
                login(request, user)
                if not remember_me:
                    request.session.set_expiry(0)
                return redirect('dashboard')
            else:
                messages.error(request, 'Invalid email or password.')
    else:
        form = CustomLoginForm()
    
    return render(request, 'accounts/login.html', {'form': form})

def signup_view(request):
    """
    Signup view
    """
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = CustomSignupForm(request.POST)
        if form.is_valid():
            user = form.save(request)
            login(request, user)
            return redirect('dashboard')
    else:
        form = CustomSignupForm()
    
    return render(request, 'accounts/signup.html', {'form': form})

def logout_view(request):
    """
    Logout view
    """
    logout(request)
    return redirect('home')

@login_required
def dashboard_view(request):
    """
    Dashboard view
    """
    context = {
        'user': request.user
    }
    return render(request, 'accounts/dashboard.html', context)

@login_required
def profile_view(request):
    """
    Profile view
    """
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('profile')
    else:
        form = UserProfileForm(instance=request.user)
    
    context = {
        'form': form
    }
    return render(request, 'accounts/profile.html', context)

class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    """
    Profile update view
    """
    model = User
    form_class = UserProfileForm
    template_name = 'accounts/profile_update.html'
    success_url = reverse_lazy('profile')
    
    def get_object(self):
        return self.request.user
