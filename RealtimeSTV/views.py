from django.http import HttpResponse
from django.shortcuts import render
from pprint import pprint
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from   Blog.models import LocalActor


def index(request):
    return render(request, "templates/home/welcome.html")

def signup(request):
    if request.method == "POST":
        username=request.POST["username"]
        password=request.POST["password"]
        user = User(username=username, 
                    email="fake@email.com",
                    password=make_password(password))
        user.save()
        actor = LocalActor.objects.create(username=username,
                                          domain="ppl.manicphase.me", # TODO: not hardcode this
                                          owner=user)
        actor.fill_in_bits()


        return render(request, "templates/home/welcome.html")
    else:
        return render(request, "templates/home/signup.html")
    
def login(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = User.objects.get(username=username)

        if user.check_password(password):
            request.session["user"] = username

            return render(request, "templates/home/welcome.html")
    else:
        return render(request, "templates/home/login.html")