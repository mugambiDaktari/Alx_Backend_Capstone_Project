from django.shortcuts import render
from django.views.generic.edit import CreateView
from django.contrib.auth import login
from django.urls import reverse_lazy
from .forms import UserRegistrationForm
from .models import User
from django.views.generic import TemplateView
from django.contrib.auth.views import LoginView, LogoutView
# Create your views here.


class HomeView(TemplateView):
    template_name = "hotel_app/homepage.html"

class RegisterView(CreateView):
    model = User
    form_class = UserRegistrationForm
    template_name = "hotel_app/register.html"
    success_url = reverse_lazy("homepage")  # Redirect after successful registration
class UserLoginView(LoginView):
    template_name = "hotel_app/login.html"

class UserLogoutView(LogoutView):
    next_page = "login"  # Redirect to login page after logout


