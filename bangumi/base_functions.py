# coding=utf-8
import re
import grequests
from datetime import datetime


headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:23.0) Gecko/20100101 Firefox/23.0'}
MIN_PEOPLE_NUM = 10
ONE_PAGE_MAX_NUM = 100
TYPE = ['collect', 'do', 'on_hold', 'dropped']
CHINESE_TYPE = ['看过', '在看', '搁置', '抛弃']
UPDATE_DAYS = 13
NUM_ONE_PAGE = 24
MUTI_SCRAWL_SIZE = 25
anime_num_pattern = '<ul class=\"navSubTabs\">.*?</ul>'
span_pattern = '<span>.*?</span>'
base_url = 'http://mirror.bgm.rin.cat/'
api_url = 'http://api.bgm.tv/'


def to_str(string):
    return string.encode('latin-1').decode('unicode_escape').encode('raw_unicode_escape').decode()


def is_positive_int(string):
    int_pattern = r'^0*[123456789]\d*$'
    res = re.match(pattern=int_pattern, string=string)
    return res is not None


def dif_time_from_now(time):
    # _time = datetime.strptime(time, '%Y-%m-%d')
    now = datetime.now().date()
    return (now-time).days


def get_current_time():
    # time = str(datetime.now())
    # pos = time.find(' ')
    # return time[:pos]
    return datetime.now().date()


def scrawl_one_page(url):
    urls = [url]
    rs = (grequests.get(u) for u in urls)
    tmp = grequests.map(rs, size=1)
    while tmp[0] is None:
        tmp = grequests.map(rs, size=1)
    return tmp[0].content


def muti_scrawl_page(urls, size=MUTI_SCRAWL_SIZE):
    rs = (grequests.get(u) for u in urls)
    res = grequests.map(rs, size=size)
    nonelist = []
    for i, item in enumerate(res):
        if item is None:
            nonelist.append(i)
    if len(nonelist) == 0:
        return res
    else:
        tmpurls = []
        for num in nonelist:
            tmpurls.append(urls[num])
        print('scrawl failure, %d' % len(tmpurls))
        tmpres = muti_scrawl_page(tmpurls, size=size)
        for i, num in enumerate(nonelist):
            res[num] = tmpres[i]
        return res

