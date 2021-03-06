# coding=utf-8
# from __future__ import unicode_literals
from bs4 import BeautifulSoup as bs
# import urllib,  urllib2
from datetime import datetime
import os
from django.shortcuts import render
from models import bgmUser, Anime, Episode
import json
from django.views.decorators.csrf import csrf_exempt
from django.http import Http404, HttpResponseRedirect, HttpResponse
from django.utils.safestring import mark_safe
# from base_functions import *
from db_operation import *


@csrf_exempt
def test_web(request):
    # quick_add_user('322380')
    add_anime('152091')
    print request.POST.get('cookie')
    # a = bgmUser.objects.filter(bgm_id='')[0]
    # a.delete()
    return render(request, 'error.html')


def show_anime(request):

    return render(request, 'distribution.html')
    animelist = []
    tmpa = Anime.objects.filter(bgm_id='111876')
    animelist.append(tmpa[0])
    return render(request, 'showAnime.html', {'animelist': animelist})


def mark_episode(request):
    user_id = request.GET.get('user_id')
    subject_id = request.GET.get('sub_id')
    ep_id = request.GET.get('ep_id')
    # print('marked', user_id, subject_id, ep_id)

    referer = request.META.get('HTTP_REFERER')
    if referer is not None:
        response = HttpResponseRedirect(referer)
    else:
        if subject_id is None:
            response = HttpResponseRedirect('https://bgm.tv')
        else:
            response = HttpResponseRedirect('https://bgm.tv/subject/' + subject_id)
    if user_id is None or subject_id is None or ep_id is None:
        return response

    user, u_iscreate = bgmUser.objects.get_or_create(bgm_id=user_id)
    if u_iscreate:
        user = quick_add_user(user_id)
    anime, a_iscreate = Anime.objects.get_or_create(bgm_id=subject_id)
    if a_iscreate:
        anime = add_anime(subject_id)

    ep = Episode.objects.filter(ep_id=ep_id)
    if len(ep) == 0:
        ep = Episode.objects.create(ep_id=ep_id)
        ep.set_evaluation({'user': [], 'rate': []})
    else:
        ep = ep[0]
    if ep.anime is None:
        ep.anime = anime
    ep.bgmUser.add(user)
    ep.save()
    return response


def delete_marked_episode(request):
    user_id = request.GET.get('user_id')
    subject_id = request.GET.get('sub_id')
    ep_id = request.GET.get('ep_id')

    ep = Episode.objects.filter(ep_id=ep_id)
    anime = Anime.objects.filter(bgm_id=subject_id)
    user = bgmUser.objects.filter(bgm_id=user_id)

    referer = request.META.get('HTTP_REFERER')
    if referer is not None:
        response = HttpResponseRedirect(referer)
    else:
        if subject_id is None:
            response = HttpResponseRedirect('https://bgm.tv')
        else:
            response = HttpResponseRedirect('https://bgm.tv/subject/' + subject_id)

    if len(ep) == 0 or len(anime) == 0 or len(user) == 0:
        return response

    ep = ep[0]

    if ep.anime is None:
        ep.anime = anime[0]

    ep.bgmUser.remove(user[0])
    ep.save()
    return response


def get_marked_episode(request):
    user_id = request.GET.get('user_id')
    subject_id = request.GET.get('sub_id')

    user, u_iscreate = bgmUser.objects.get_or_create(bgm_id=user_id)
    if u_iscreate:
        user = quick_add_user(user_id)
    anime, a_iscreate = Anime.objects.get_or_create(bgm_id=subject_id)
    if a_iscreate:
        anime = add_anime(subject_id)

    ret = {'success': False}
    if anime is not None and user is not None:
        eps = list(anime.episode_set.values_list('ep_id', flat=True))
        # print(eps, type(eps))
        marked_eps = user.episode_set.filter(ep_id__in=eps)

        # print(marked_eps)
        ret['success'] = True
        ret['eps'] = list(marked_eps.values_list('ep_id', flat=True))

    return HttpResponse(json.dumps(ret), content_type='application/json')


def did_user_judge_ep(request):
    user_id = request.GET.get('user_id')
    ep_id = request.GET.get('ep_id')

    ret = dict()
    ep = Episode.objects.filter(ep_id=ep_id)
    if len(ep) == 1:
        ep = ep[0]
        evaluation = ep.get_evaluation()
        if evaluation['user'].count(user_id) > 0:
            count = [0] * 5
            num = len(evaluation['rate'])
            for item in evaluation['rate']:
                count[5 - item] += 1  # 54321顺序
            width = list()
            for i in range(5):
                width.append('%.2f' % (count[i] * 100.0 / num))
            ret['count'] = count
            ret['width'] = width
            ret['choice'] = evaluation['rate'][evaluation['user'].index(user_id)]
            ret['res'] = True
            ret['voters'] = num
            return HttpResponse(json.dumps(ret), content_type='application/json')

    ret['res'] = False
    response = HttpResponse(json.dumps(ret), content_type='application/json')
    # response = HttpResponse(callback + '('+json.dumps(ret)+');', content_type='application/json')
    return response


def add_user_vote_ep(request):
    user_id = request.POST.get('user_id')
    ep_id = request.POST.get('ep_id')
    rate = request.POST.get('rate')

    # print(user_id, ep_id, rate)
    ret = dict()
    if user_id is None or ep_id is None or rate is None:
        ret['success'] = False
        ret['message'] = 'unknown error'
        return HttpResponse(json.dumps(ret), content_type='application/json')
    # rate valid
    rate = int(rate)
    ep = Episode.objects.filter(ep_id=ep_id)
    if len(ep) == 0:
        evaluation = {'user': [user_id], 'rate': [rate]}
        ep = Episode.objects.create(ep_id=ep_id, evaluation=json.dumps(evaluation))
    else:
        ep = ep[0]
        evaluation = ep.get_evaluation()
        if evaluation['user'].count(user_id) > 0:
            ret['success'] = False
            ret['message'] = '你已投过票！'
            return HttpResponse(json.dumps(ret), content_type='application/json')

        evaluation['user'].append(user_id)
        evaluation['rate'].append(rate)
        ep.set_evaluation(evaluation)
    count = [0]*5
    num = len(evaluation['rate'])
    for item in evaluation['rate']:
        count[5-item] += 1  # 54321顺序
    width = list()
    for i in range(5):
        width.append('%.2f' % (count[i] * 100.0 / num))
    ret['count'] = count
    ret['width'] = width
    ret['choice'] = rate
    ret['success'] = True
    ret['voters'] = num
    return HttpResponse(json.dumps(ret), content_type='application/json')


def show_distribution(request):
    user_id = request.GET.get('id')
    if user_id is None:
        return render(request, 'error.html')
    bgmuser = bgmUser.objects.filter(bgm_id=user_id)
    if len(bgmuser) == 0:
        bgmuser = add_user(user_id)
        return render(request, 'error.html', {'error_message':'抱歉，  没有查询到该用户的信息'})
    elif dif_time_from_now(bgmuser[0].time) > UPDATE_DAYS:
        bgmuser = update_user(user_id)
    else:
        bgmuser = bgmuser[0]

    collect = bgmuser.get_collect()
    distri = get_distribution(collect)
    dropped = bgmuser.get_collect(_type='dropped')
    dropped_distri = get_distribution(dropped)
    print bgmuser.time
    return render(request, 'distribution.html', {'collect_data': json.dumps(distri[1:]),
                                                 'dropped_data': json.dumps(dropped_distri[1:]),
                                                 'time': str(bgmuser.time), 'bgm_id':user_id})


def refreshInfo(request):
    # print request.POST.get('cookie')
    user_id = request.POST.get('id')
    tmp = dict(request.POST)
    choice = tmp.get('choice[]')
    bgmuser = bgmUser.objects.filter(bgm_id=user_id)

    if len(bgmuser) != 1:
        print 'refreshInfo error'
        return render(request, 'error.html')
    else:
        distri = []
        data = {'status': 'success'}
        for i in range(4):
            if choice[i] == 'true':
                distri.append(get_distribution(bgmuser[0].get_collect(_type=TYPE[i]))[1:])
            else:
                distri.append([])
        data['distri'] = distri
        data['choice'] = choice
        return HttpResponse(json.dumps(data), content_type='application/json')


@csrf_exempt
def updateInfo(request):
    # return HttpResponse(json.dumps({"status": "success", "distribution": [1]*10}), content_type='application/json')
    user_id = request.POST.get('id')
    tmp = dict(request.POST)
    choice = tmp.get('choice[]')
    print user_id, type(user_id)
    bgmuser = update_user(user_id)
    if bgmuser == -1:
        print 'no such user'
        return render(request, 'error.html')
    else:
        distri = []
        data = {'status': 'success'}
        for i in range(4):
            if choice[i] == 'true':
                distri.append(get_distribution(bgmuser.get_collect(_type=TYPE[i]))[1:])
            else:
                distri.append([])
        data['distri'] = distri
        data['choice'] = choice
        data['time'] = str(bgmuser.time)
        return HttpResponse(json.dumps(data), content_type='application/json')


def get_friend_evaluation(request):
    user_id = request.GET.get('id')
    if user_id is None:
        return render(request, 'error.html', {'error_message': '???unknown error'})
    friends = get_friend(user_id)
    if len(friends) == 1:
        return render(request, 'error.html', {'error_message': 'Sorry, you do not have friend.'})
    page = request.GET.get('page')
    if page is None or is_positive_int(page) is not True:
        page = 1
    else:
        page = int(page)

    show_list = []
    anime_id = []
    grade = []
    count = []
    for bgm_id in friends:
        tmpuser = bgmUser.objects.filter(bgm_id=bgm_id)
        if len(tmpuser) == 0:
            collect = add_user(bgm_id).get_all_in_one_list()
        elif dif_time_from_now(tmpuser[0].time) > UPDATE_DAYS:
            collect = update_user(bgm_id).get_all_in_one_list()
        else:
            collect = tmpuser[0].get_all_in_one_list()
        for anime in collect:
            if anime['grade'] == 0:
                continue
            if anime['id'] not in anime_id:
                anime_id.append(anime['id'])
                grade.append(anime['grade'])
                count.append(1)
            else:
                index = anime_id.index(anime['id'])
                grade[index] += anime['grade']
                count[index] += 1

    length = len(anime_id)

    for i in range(length):
        if count[i] > MIN_PEOPLE_NUM:
            show_list.append({'id': anime_id[i], 'grade': round(float(grade[i]) / count[i], 4), 'count': count[i]})
    show_list.sort(key=lambda x: x['count'], reverse=True)
    show_list.sort(key=lambda x: x['grade'], reverse=True)

    # f = open('grade.txt', 'w+')
    # for i in range(120):
    #     f.write('%s %s %d\n' % (show_list[i]['id'], str(show_list[i]['grade']), show_list[i]['count']))
    # #     f.write(show_list[i]['id'] + ' 第%d名 '%(i+1) + str(show_list[i]['grade']) + '(' + str(show_list[i]['count']) + '人评分)\n')
    # f.close()
    list_length = len(show_list)
    page_max = (list_length - 1) / NUM_ONE_PAGE + 1
    if page > page_max:
        page = page_max
    if page * NUM_ONE_PAGE > list_length:
        show_list = show_list[(page-1)*NUM_ONE_PAGE:]
    else:
        show_list = show_list[(page-1)*NUM_ONE_PAGE:page*NUM_ONE_PAGE]
    real_list = []
    c = (page-1) * 24
    for item in show_list:

        # print item['id']
        tmpa = Anime.objects.filter(bgm_id=item['id'])
        if len(tmpa) == 0:
            continue
        tmpa = tmpa[0]
        c += 1
        dic = {'name': tmpa.name, 'foreign_name': tmpa.foreign_name, 'bgm_id': item['id'],
               'num': item['count'], 'grade': item['grade'], 'int_grade': int(item['grade']+0.5),
               'img_url': tmpa.img_url, 'info': tmpa.info, 'rank': c,  'flag': c % 2}
        real_list.append(dic)

    before_list = range(max(1, page-5), page)
    after_list = range(page+1, min(page+5, page_max+1))

    return render(request, 'showAnime.html', {'animelist': real_list, 'bgm_id': user_id,
                                              'page': page, 'page_max': page_max,
                                              'before_list': before_list, 'after_list': after_list})


def get_friend(username):
    url = base_url + 'user/' + username + '/friends'
    res = scrawl_one_page(url)
    print 'end read'
    # res = opener.open(req).read()
    soup = bs(str(res), 'lxml')
    friend_filter = soup.find_all('a', class_='avatar')
    print len(friend_filter)
    friends = []
    for item in friend_filter:
        tmp = str(item)
        pos1 = tmp.find('user/')
        pos2 = tmp.find('>')
        if tmp[pos1+5: pos2-1] != 'soranomethod':
            friends.append(tmp[pos1+5: pos2-1])
    return friends


def update_anime_database(request):
    # relative_dir = '..' + os.sep + 'bgm_anime' + os.sep + 'html' + os.sep
    relative_dir = 'bgm_anime' + os.sep + 'html' + os.sep
    anime_pattern = '<li id=.*?</li>'
    name_pattern = '<a href=.*? class=\"l\".*?</a'
    for i in range(154, 155):
        if i % 20 == 0:
            print 'end %d page' % i
        f = open(relative_dir + '%d.html' % i)
        content = f.read()
        content = content.replace('/subject/', 'http://bgm.tv/subject/')
        animes_str = re.findall(pattern=anime_pattern, string=content, flags=re.S)
        animes_str.pop()
        animes_str.pop()  # remove the last two
        # print len(animes_str)
        # print animes_str[4]
        for anime_str in animes_str:
            pos1 = anime_str.find('class')
            bgm_id = anime_str[13: pos1-2]
            soup = bs(anime_str, 'lxml')
            img_res = soup.find_all('img')
            if len(img_res) == 0:
                img_url = ''
            else:
                img_url = img_res[0]['src']

            name = soup.select('.l')[0].string
            foreign_name_res = soup.select('.grey')
            if len(foreign_name_res) > 0:
                foreign_name = foreign_name_res[0].string
            else:
                foreign_name = ''
            info = soup.select('p[class="info tip"]')[0].string
            grade_res = soup.select('.fade')
            if len(grade_res) > 0:
                grade = float(grade_res[0].string)
            else:
                grade = 0.0
            num_res = soup.select('.tip_j')
            if len(num_res) == 0:
                num = '0'
            else:
                num = num_res[0].string

            # name_res = re.search(name_pattern, anime_str).group()
            # pos = name_res.rfind('>')
            # name = name_res[pos + 1: -3]
            name = name.replace('\\\\', '\\')
            # print bgm_id, name
            res = Anime.objects.filter(bgm_id=bgm_id)
            if len(res) == 0:
                Anime.objects.create(bgm_id=bgm_id, name=name,
                                     foreign_name=foreign_name, num=num,
                                     grade=grade, img_url=img_url,info=info)

    return render(request, 'showAnime.html')

