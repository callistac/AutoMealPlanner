from django.shortcuts import render
from django.contrib.auth.forms import UserCreationForm

# Create your views here.
def user_signup(request):
    return render(request, 'user_signup/user_signup.html', {})

def home(request):
    return render(request, 'user_signup/home.html', {})

def new_user(request):
    return render(request, 'user_signup/new_user.html', {})

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("/login")
    else:
        form = UserCreationForm()
        args = {"form":form}
        return render(request, 'user_signup/new_user.html', args)
