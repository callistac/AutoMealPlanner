from django.urls import path
from user_signup import views
from django.contrib.auth.views import LoginView, LogoutView


urlpatterns = [
    path('', views.home, name='user_signup/home.html'),
    path('login/', LoginView.as_view(template_name='user_signup/user_signup.html')),
    path('login/new_user/', LoginView.as_view(template_name='user_signup/new_user.html')),
    path('logout/', LogoutView.as_view(template_name='user_signup/logout.html'))
]
