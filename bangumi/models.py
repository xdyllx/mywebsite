# coding=utf-8

from django.db import models
import os, time
# import json
# CONST VALUE
NAME_MAX_LENGTH = 25
TIME_MAX_LENGTH = 40


class bgmUser(models.Model):
    name = models.CharField(max_length=NAME_MAX_LENGTH)
    bgm_id = models.CharField(max_length=NAME_MAX_LENGTH)
    time = models.DateField(max_length=TIME_MAX_LENGTH)  # 7天信息过期，进行更新
    state = models.SmallIntegerField(default=0)
    file_state = models.SmallIntegerField(default=0)  # 0 no  1 read  2 write
    # img_url = models.CharField(max_length=50)
    # collect = models.CharField(max_length=10000)
    # do = models.CharField(max_length=2000)
    # on_hold = models.CharField(max_length=1000)
    # dropped = models.CharField(max_length=2000)

    def set_collect(self, x, _type='collect'):
        while self.file_state != 0:
            time.sleep(0.05)
        self.file_state = 2
        f = open('user_' + _type + os.sep + self.bgm_id + '.txt', 'w+')
        for item in x:
            f.write(item['id'] + ' ' + str(item['grade']) + '\n')
        f.close()
        self.file_state = 0

    def get_collect(self, _type='collect'):
        while self.file_state == 2:
            time.sleep(0.05)
        self.file_state = 1
        f = open('user_'+_type+os.sep+self.bgm_id+'.txt', 'r')
        content = f.readlines()
        f.close()
        self.file_state = 0
        collect = []
        for string in content:
            tmp = string.split()
            collect.append({'id': tmp[0], 'grade': int(tmp[1])})
        return collect
        # return json.loads(self.collect.decode('utf-8').replace("'", "\""))

    def set_all(self, collect, do, on_hold, dropped):
        self.set_collect(collect, 'collect')
        self.set_collect(do, 'do')
        self.set_collect(on_hold, 'on_hold')
        self.set_collect(dropped, 'dropped')

    def get_all(self):
        collect = self.get_collect('collect')
        do = self.get_collect('do')
        on_hold = self.get_collect('on_hold')
        dropped = self.get_collect('dropped')
        return collect, do, on_hold, dropped

    def get_all_in_one_list(self):
        collect = self.get_collect('collect')
        do = self.get_collect('do')
        on_hold = self.get_collect('on_hold')
        dropped = self.get_collect('dropped')
        return collect + do + on_hold + dropped

    def __str__(self):
        return self.bgm_id


class Anime(models.Model):
    name = models.CharField(max_length=NAME_MAX_LENGTH)
    foreign_name = models.CharField(max_length=NAME_MAX_LENGTH)
    bgm_id = models.CharField(max_length=7)
    num = models.CharField(max_length=15)  # graded people
    grade = models.FloatField(default=0.0)
    img_url = models.CharField(max_length=50)
    info = models.CharField(max_length=100)
    rank = models.SmallIntegerField(default=0)
