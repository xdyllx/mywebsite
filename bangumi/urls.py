from django.conf.urls import include, url
from django.contrib import admin
import views

urlpatterns = [
    url(r'^updateanime/$', views.update_anime_database, name='update_anime_database'),
    url(r'friend/$', views.get_friend_evaluation, name='friend'),
    url(r'test/$', views.test_web, name='test')
]
