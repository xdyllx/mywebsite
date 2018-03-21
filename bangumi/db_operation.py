# coding=utf-8
from base_functions import *
import json
from models import bgmUser, Anime, Episode

# def add_anime(content):


def get_anime_by_api(bgm_id):

    url = api_url + 'subject/' + bgm_id + '?responseGroup=large'
    content = scrawl_one_page(url).decode()
    # content = content.replace('\\\\', '\\')
    # content = content[2:-1]
    print(content)
    dic = json.loads(content)
    print(dic)
    print dic['eps']


def get_bgm_num(bgm_id):
    url = base_url + 'anime/list/%s/collect' % bgm_id
    # request = urllib2.Request(url=url, headers=headers)
    # response = urllib2.urlopen(request)
    data = scrawl_one_page(url)
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
                    tmp1 = item.find('(')
                    tmp2 = item.find(')')
                    num[i] = int(item[tmp1+1:tmp2])
                    break

    else:
        print 'error: cannot get number show on bgm '

    return num


def quick_add_user(bgm_id):
    url = api_url + 'user/' + bgm_id
    content = scrawl_one_page(url).decode()
    dic = json.loads(content)
    print dic
    print dic['username'], dic['nickname'], dic['id'], type(dic['id'])
    user, iscreate = bgmUser.objects.update_or_create(bgm_id=str(dic['id']))
    user.username = dic['username']
    user.nickname = dic['nickname']
    user.avatar = dic['avatar']['large']
    user.save()


def add_user(bgm_id):
    print datetime.now(), 'add user', bgm_id
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
    print datetime.now(), 'update user', bgm_id
    bgmuser = bgmUser.objects.filter(bgm_id=bgm_id)
    if len(bgmuser) != 1:
        print 'update user error', len(bgmuser)
        return -1

    collect, do, on_hold, dropped = get_user_all_bgm(bgm_id)
    bgmuser[0].set_all(collect, do, on_hold, dropped)
    bgmuser[0].time = get_current_time()
    bgmuser[0].save()
    return bgmuser[0]


def add_anime(bgm_id):
    url = api_url + 'subject/' + bgm_id
    content = scrawl_one_page(url).decode()
    dic = json.loads(content)
    print dic
    anime, iscreate = Anime.objects.update_or_create(bgm_id=str(dic['id']))
    anime.rank, anime.name, anime.name_cn = dic['rank'], dic['name'], dic['name_cn']
    anime.img_url, anime.total_num = dic['images']['small'], dic['rating']['total']
    nums = ''
    score = 0.0
    for i in range(1, 11):
        count = dic['rating']['count'][str(i)]
        score += count * i
        nums = nums + str(count) + ','
    if dic['rating']['total'] != 0:
        score /= dic['rating']['total']
    anime.score = score
    anime.nums = nums
    date = dic['air_date']
    if date != '':
        date = date.split('-')
        anime.year = int(date[0])
        anime.month = int(date[1])
    if dic.get('eps_count') is not None:
        anime.ep_count = dic['eps_count']
    anime.save()
    return anime


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


def get_user_collect(bgm_id, anime_num, _type='collect'):
    if anime_num == 0:
        return []

    user_collect = []
    urls = []
    page_num = (anime_num - 1) / 24 + 1
    for i in range(page_num):
        urls.append(base_url + 'anime/list/%s/%s?page=%d' % (bgm_id, _type, i + 1))
    res = muti_scrawl_page(urls)

    for r in res:
        if r is None:
            print 'None error, continue'
            continue
        if get_page(r.content, user_collect) is None:
            break
    # data = data.decode('utf-8')
    # print(res)
    print 'finish', bgm_id, _type
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
        id_res = re.search(animeid_pattern, animation[i]).group()
        pos = id_res.rfind('/')
        anime_id = id_res[pos + 1: -1]
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

if __name__ == '__main__':
    get_anime_by_api('876')
