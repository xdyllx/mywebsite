# coding=utf-8
# from __future__ import unicode_literals
import re
from bs4 import BeautifulSoup as bs
import urllib,  urllib2
import grequests
from datetime import datetime
import os
from django.shortcuts import render
from models import bgmUser, Anime
import json
from django.views.decorators.csrf import csrf_exempt
from django.http import Http404, HttpResponseRedirect, HttpResponse
from django.utils.safestring import mark_safe


headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:23.0) Gecko/20100101 Firefox/23.0'}
MIN_PEOPLE_NUM = 5
ONE_PAGE_MAX_NUM = 100
TYPE = ['collect', 'do', 'on_hold', 'dropped']
CHINESE_TYPE = ['看过', '在看', '搁置', '抛弃']
UPDATE_DAYS = 7
NUM_ONE_PAGE = 24

anime_num_pattern = '<ul class=\"navSubTabs\">.*?</ul>'
span_pattern = '<span>.*?</span>'


def to_str(string):
    return string.encode('latin-1').decode('unicode_escape').encode('raw_unicode_escape').decode()


def is_positive_int(string):
    int_pattern = r'^0*[123456789]\d*$'
    res = re.match(pattern=int_pattern, string=string)
    return res is not None


def test_web(request):
    # a = bgmUser.objects.filter(bgm_id='')[0]
    # a.delete()
    return render(request, 'error.html')


def dif_time_from_now(time):
    # _time = datetime.strptime(time, '%Y-%m-%d')
    now = datetime.now().date()
    return (now-time).days


def get_current_time():
    # time = str(datetime.now())
    # pos = time.find(' ')
    # return time[:pos]
    return datetime.now().date()


def get_bgm_num(bgm_id):
    url = 'http://bgm.tv/anime/list/%s/collect' % bgm_id
    request = urllib2.Request(url=url, headers=headers)
    response = urllib2.urlopen(request)
    data = response.read()
    if data.find('数据库中没有查询到该用户的信息') != -1:
        return [-1] * 4
    num = [0] * 4
    a = re.findall(string=data, pattern=anime_num_pattern, flags=re.S)
    if len(a) == 1:
        b = re.findall(string=a[0], pattern=span_pattern)
        for item in b:
            for i in range(4):
                tmp = item.find(CHINESE_TYPE[i])
                if tmp != -1:
                    tmp1 = item.find(')')
                    # print item[tmp+8:tmp1]
                    num[i] = int(item[tmp+8:tmp1])
                    break

    else:
        print 'error: cannot get number show on bgm '

    return num


def muti_scrawl_page(urls):
    rs = (grequests.get(u) for u in urls)
    tmp = grequests.map(rs, size=6)
    for item in tmp:
        if item is None:
            print 'None response'
            tmp = grequests.map(rs, size=5)
            break
    return tmp


def show_anime(request):
    return render(request, 'distribution.html')
    animelist = []
    tmpa = Anime.objects.filter(bgm_id='111876')
    animelist.append(tmpa[0])
    return render(request, 'showAnime.html', {'animelist': animelist})


def add_user(bgm_id):
    print 'add user', bgm_id
    collect, do, on_hold, dropped = get_user_all_bgm(bgm_id)
    if collect is None:
        return None
    bgmuser = bgmUser.objects.filter(bgm_id=bgm_id)
    if len(bgmuser) == 0:
        bgmuser = bgmUser.objects.create(
            bgm_id=bgm_id,
            time=get_current_time(),
        )
    else:
        bgmuser = bgmuser[0]
    bgmuser.set_all(collect, do, on_hold, dropped)
    # bgmuser.collect = user_collect
    bgmuser.save()
    return bgmuser


def update_user(bgm_id):
    print 'update user', bgm_id
    bgmuser = bgmUser.objects.filter(bgm_id=bgm_id)
    if len(bgmuser) != 1:
        print 'update user error', len(bgmuser)
        return -1

    collect, do, on_hold, dropped = get_user_all_bgm(bgm_id)
    bgmuser[0].set_all(collect, do, on_hold, dropped)
    bgmuser[0].time = get_current_time()
    bgmuser[0].save()
    return bgmuser[0]


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
        data['time'] = bgmuser.time
        return HttpResponse(json.dumps(data), content_type='application/json')


def get_distribution(anime_list):
    distri = [0] * 11
    for anime in anime_list:
        distri[anime['grade']] += 1
    return distri


def get_user_all_bgm(bgm_id):
    num = get_bgm_num(bgm_id)
    if num[0] == -1:
        return [None] * 4
    collect = get_user_collect(bgm_id, num[0], 'collect')
    do = get_user_collect(bgm_id, num[1], 'do')
    on_hold = get_user_collect(bgm_id, num[2], 'on_hold')
    dropped = get_user_collect(bgm_id, num[3], 'dropped')
    return collect, do, on_hold, dropped


def get_all_num(bgm_id):
    url = 'http://bgm.tv/user/' + bgm_id
    request = urllib2.Request(url=url, headers=headers)
    response = urllib2.urlopen(request)
    data = response.read()


def get_user_collect(bgm_id, anime_num, _type='collect'):
    if anime_num == 0:
        return []

    user_collect = []
    urls = []
    page_num = (anime_num - 1) / 24 + 1
    for i in range(page_num):
        urls.append('http://bgm.tv/anime/list/%s/%s?page=%d' % (bgm_id, _type, i+1))
    res = muti_scrawl_page(urls)

    for r in res:
        if get_page(r.content, user_collect) is None:
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

        # name_res = re.search(name_pattern, animation[i]).group()
        # pos = name_res.rfind('>')
        # name = name_res[pos + 1: -3]
        # name = name.replace('\\\\', '\\')
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
        return render(request, 'error.html', {'error_message': '???unknown error'})
    friends = get_friend(user_id)
    if len(friends) == 0:
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
            collect = add_user(bgm_id).get_collect()
        elif dif_time_from_now(tmpuser[0].time) > UPDATE_DAYS:
            collect = update_user(bgm_id).get_collect()
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
    list_length = len(show_list)
    page_max = (list_length - 1) / NUM_ONE_PAGE + 1
    if page > page_max:
        page = page_max
    if page * NUM_ONE_PAGE > list_length:
        show_list = show_list[(page-1)*NUM_ONE_PAGE+1:]
    else:
        show_list = show_list[(page-1)*NUM_ONE_PAGE+1:page*NUM_ONE_PAGE+1]
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
               'num': item['count'], 'grade': item['grade'], 'int_grade': int(item['grade']),
               'img_url': tmpa.img_url, 'info': tmpa.info, 'rank': c,  'flag': c % 2}
        real_list.append(dic)

    before_list = range(max(1, page-5), page-1)
    after_list = range(page+1, min(page+5, page_max+1))

    return render(request, 'showAnime.html', {'animelist': real_list, 'bgm_id': user_id,
                                              'page': page, 'page_max': page_max,
                                              'before_list': before_list, 'after_list': after_list})


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

