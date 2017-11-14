# coding=utf-8
# from __future__ import unicode_literals
import re
from bs4 import BeautifulSoup as bs
import urllib,  urllib2
from datetime import datetime
import os
from django.shortcuts import render
from models import bgmUser, Anime
import json

from django.utils.safestring import mark_safe


headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:23.0) Gecko/20100101 Firefox/23.0'}
MIN_PEOPLE_NUM = 3
ONE_PAGE_MAX_NUM = 100


def to_str(string):
    return string.encode('latin-1').decode('unicode_escape').encode('raw_unicode_escape').decode()


def test_web(request):
    a = bgmUser.objects.filter(bgm_id='basertyu')[0]
    # a.delete()
    print a.get_collect()
    return render(request, 'error.html')


def show_anime(request):
    return render(request, 'distribution.html')
    animelist = []
    tmpa = Anime.objects.filter(bgm_id='111876')
    animelist.append(tmpa[0])
    return render(request, 'showAnime.html', {'animelist': animelist})


def add_user(bgm_id):
    print 'add user', bgm_id
    user_collect = get_user_collect(bgm_id)
    bgmuser = bgmUser.objects.create(
        bgm_id=bgm_id,
        time=str(datetime.now()).split()[0],
    )
    bgmuser.set_collect(user_collect)
    print len(user_collect)
    bgmuser.collect = user_collect
    bgmuser.save()
    return user_collect


def show_distribution(request):
    user_id = request.GET.get('id')
    bgmuser = bgmUser.objects.filter(bgm_id=user_id)
    if len(bgmuser) == 0:
        print 'no such user'
        return render(request, 'error.html')
    else:
        collect = bgmuser[0].get_collect()
        distri = get_distribution(collect)

        return render(request, 'distribution.html', {'data': json.dumps(distri[1:])})


def get_distribution(anime_list):
    distri = [0] * 11
    for anime in anime_list:
        distri[anime['grade']] += 1
    return distri


def get_user_collect(bgm_id):
    count = 0
    user_collect = []
    while 1:
        now = datetime.now()
        display_now = str(now).split(' ')[1][:-3]
        count += 1
        print(display_now, u'第%d页' % count)
        url = 'http://bgm.tv/anime/list/' + bgm_id + '/collect?orderby=rate&page='+str(count)
        request = urllib2.Request(url=url, headers=headers)
        response = urllib2.urlopen(request)
        data = response.read()
        print 'end read'
        res = str(data)
        if get_page(res, user_collect) is None:
            break
    # data = data.decode('utf-8')
    # print(res)
    return user_collect


def get_page(string, user_collect):
    tmp = []
    animation_pattern = '<div class=\"inner\">.*?</div>'
    name_pattern = '<a href=.*? class=\"l\".*?</a'
    grade_pattern = 'sstars.*?></span>'
    animeid_pattern = '<a href=\"/subject/.*?\"'
    animation = re.findall(animation_pattern, string, re.S)
    length = len(animation)
    # print(length)
    if length == 3:
        return None
    for i in range(2, length - 1):
        dic = {}

        name_res = re.search(name_pattern, animation[i]).group()
        pos = name_res.rfind('>')
        name = name_res[pos + 1: -3]
        name = name.replace('\\\\', '\\')
        # print('name =', to_str(name))
        # dic['name'] = name
        id_res = re.search(animeid_pattern, animation[i]).group()
        pos = id_res.rfind('/')
        anime_id = id_res[pos+1: -1]
        dic['id'] = anime_id
        grade_res = re.search(grade_pattern, animation[i])

        if grade_res is not None:
            grade_res = grade_res.group()
            pos = grade_res.find(' ')
            grade = int(grade_res[6:pos])
            # print('grade=', grade)
            dic['grade'] = grade
        else:
            dic['grade'] = 0
        user_collect.append(dic)
    if length < 27:
        return None
    return 1


def get_friend_evaluation(request):
    user_id = request.GET.get('id')
    if user_id is None:
        return render(request, 'error.html')
    friends = get_friend(user_id)
    if len(friends) == 0:
        return render(request, 'error.html', {'error_message': 'Sorry, you do not have friend.'})

    show_list = []
    anime_id = []
    grade = []
    count = []
    for bgm_id in friends:
        tmpuser = bgmUser.objects.filter(bgm_id=bgm_id)
        if len(tmpuser) == 0:
            collect = add_user(bgm_id)
        else:
            collect = tmpuser[0].get_collect()
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

    show_list.sort(key=lambda x: x['grade'], reverse=True)
    print len(show_list)
    if len(show_list) > ONE_PAGE_MAX_NUM:
        show_list = show_list[:ONE_PAGE_MAX_NUM]
    real_list = []
    c = 0
    for item in show_list:

        # print item['id']
        tmpa = Anime.objects.filter(bgm_id=item['id'])
        if len(tmpa) == 0:
            continue
        tmpa = tmpa[0]
        c += 1
        dic = {'name': tmpa.name, 'foreign_name': tmpa.foreign_name,
               'bgm_id': item['id'], 'num': item['count'], 'grade': item['grade'],
               'img_url': tmpa.img_url, 'info': tmpa.info, 'rank': c,  'flag': c % 2}
        real_list.append(dic)
    return render(request, 'showAnime.html', {'animelist': real_list})


def get_friend(username):
    url = 'http://bgm.tv/user/' + username + '/friends'
    # opener = urllib2.build_opener()
    req = urllib2.Request(url, headers=headers)
    res = urllib2.urlopen(req).read()
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


if __name__ == '__main__':
    # get_friend('windrises')
    add_user('windrises')
    # update_anime_database(1)

