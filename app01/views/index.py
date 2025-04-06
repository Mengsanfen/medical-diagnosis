from django.shortcuts import render, redirect


def index(request):
    return render(request, 'index.html')


def entrance(request):
    return render(request, 'entrance.html')
