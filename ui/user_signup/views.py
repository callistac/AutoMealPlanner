from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

# Create your views here.
def user_signup(request):
    return render(request, 'user_signup/user_signup.html', {})

def home(request):
    return render(request, 'user_signup/home.html', {})

def new_user(request):
    return render(request, 'user_signup/new_user.html', {})

def about(request):
    return render(request, 'user_signup/about.html', {})

def user_info(request):
    return render(request, 'user_signup/user_information.html', {})

def about_redirect(request):
    return redirect('/home/about')

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("/home")
    else:
        form = UserCreationForm()
        args = {"form":form}
        return render(request, 'user_signup/new_user.html', args)


def profile(request):
    args = {'user': request.user}
    return render(request, 'user_signup/home.html')
