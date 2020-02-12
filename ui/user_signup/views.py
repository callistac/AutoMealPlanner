from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from user_signup.forms import CustomForm
from django.views.generic import TemplateView

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
    if request.method == 'POST':
        print(request.POST.getlist('firstname'))
        form = CustomForm(request.POST)
        return redirect("/home/dashboard")
    else:
        form = UserCreationForm()
        args = {"form":form}
        return render(request, 'user_signup/user_information.html', args)
'''
class User_Info(TemplateView):
    template_name = 'user_signup/user_information.html'
    def get(self, request):
        form = CustomForm()
        return render(request, self.template_name, {'form':form})

    def post(self, request):
        form = CustomForm(request.POST)
        if form.is_valid():
            post = form.save(commit = False)
            post.user = request.user
            print(post.user)
            post.save()
            # post below comes from initalization in forms.py
            text = form.cleaned_data['post']
            form = CustomForm()
            return redirect('/home/dashboard')

        args = {'form':form, 'text':text}
        return render(request, self.template_name, args)
'''
def about_redirect(request):
    return redirect('/home/about')

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("/home/login/new_user/user_info")
    else:
        form = UserCreationForm()
        args = {"form":form}
        return render(request, 'user_signup/new_user.html', args)

def profile(request):
    args = {'user': request.user}
    return render(request, 'user_signup/dashboard.html', args)
