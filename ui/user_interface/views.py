from django.shortcuts import redirect

def login_redirect(request):
    return redirect('/home/')

def about_redirect(request):
    return redirect('/home/about')
