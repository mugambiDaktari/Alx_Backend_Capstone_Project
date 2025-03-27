from django.urls import path
from .views import HomeView, RegisterView, UserLoginView, UserLogoutView

urlpatterns = [
    path('', HomeView.as_view(), name='homepage'),  # the empty string represents the root URL
    path("register/", RegisterView.as_view(next_page="/login/"), name="register"),
    path("login/", UserLoginView.as_view(), name="login"),
    path("logout/", UserLogoutView.as_view(), name="logout"),
]
