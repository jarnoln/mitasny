from django.shortcuts import render
from django.http import HttpResponse


def home(request):
    return HttpResponse("<html> <head> <title> Tasks </title> </head> </html>")
