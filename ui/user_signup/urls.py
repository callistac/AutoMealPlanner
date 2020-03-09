from django.urls import path
from user_signup import views
from django.contrib.auth.views import LoginView, LogoutView
from django.conf.urls.static import static
from user_interface import settings

app_name = 'user_signup'
urlpatterns = [
    path('', views.home, name='user_signup/home.html'),
    path('login/', LoginView.as_view(template_name='user_signup/user_signup.html'), name = 'login'),
    path('logout/', LogoutView.as_view(template_name='user_signup/logout.html')),
    path('login/new_user/', views.register, name='user_signup/new_user.html'),
    path('about/', views.about, name='user_signup/about.html'),
    path('about/.', views.about_redirect, name = 'about_redirect'),
    path('dashboard/', views.User_Dashboard.as_view(), name='user_dash'),
    path('dashboard/meals/', views.MealGeneration.as_view(), name='meal_generation'),
    path('user_preferences/', views.Change_User_Info.as_view(), name='user_preferences'),
    path('deselect/', views.Deselect_Tracker.as_view(), name='deselect'),
    path('dashboard/meals/download/', views.DownloadFile, name='download_file'),
    path('dashboard/past_recipes/', views.DisplayPastRecipes.as_view(), name='past_recipes'),
    path('rating/', views.Rating.as_view(), name='rating')
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# path('login/new_user/user_info/', views.User_Info.as_view(), name = 'user_entry'),
