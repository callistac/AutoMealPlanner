from django.urls import path
from user_signup import views
from django.contrib.auth.views import LoginView, LogoutView
from django.conf.urls.static import static


urlpatterns = [
    path('', views.home, name='user_signup/home.html'),
    path('login/', LoginView.as_view(template_name='user_signup/user_signup.html')),
    path('logout/', LogoutView.as_view(template_name='user_signup/logout.html')),
    path('login/new_user/', views.register, name='user_signup/new_user.html'),
    path('about/', views.about, name='user_signup/about.html'),
    path('about/.', views.about_redirect, name = 'about_redirect')



]
