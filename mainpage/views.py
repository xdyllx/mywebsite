# coding=utf-8
from django.http import Http404, HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from django.template import Template, Context


def show_main_page(request):
    return render(request, 'mainpage.html')
