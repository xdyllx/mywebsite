from django.conf.urls import include, url
from django.contrib import admin
import views

urlpatterns = [
    url(r'^updateanime/$', views.update_anime_database, name='update_anime_database'),
    url(r'friend/$', views.get_friend_evaluation, name='friend'),
    url(r'test/$', views.test_web, name='test'),
    url(r'updateInfo/$', views.updateInfo, name='updateInfo'),
    url(r'refreshInfo/$', views.refreshInfo, name='refreshInfo'),
    url(r'showDis/$', views.show_distribution, name='show_distribution'),
    url(r'user_ep/$', views.did_user_judge_ep, name='user_ep'),
    url(r'addVote/$', views.add_user_vote_ep, name='addvote'),
    url(r'mark_ep/$', views.mark_episode, name='mark_ep'),
    url(r'del_marked_ep/$', views.delete_marked_episode, name='del_marked_ep'),
    url(r'get_marked_ep/$', views.get_marked_episode, name='get_marked_ep'),
]
