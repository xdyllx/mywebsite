import grequests


def muti_scrawl_page(urls):
    rs = (grequests.get(u) for u in urls)
    tmp = grequests.map(rs, size=10)
    return tmp


def get_prepare_user():
    max_num = 381000
    user = []
    for i in range(1,11,10):
        urls = []
        for j in range(10):
            urls.append('http://bgm.tv/user/%d' % i)
        res = muti_scrawl_page(urls)
        for r in res:
            if r is None:
                continue


