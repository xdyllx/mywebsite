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
    time = models.DateField(max_length=TIME_MAX_LENGTH)  # 3天信息过期，进行更新
    state = models.SmallIntegerField(default=0)
    file_state = models.SmallIntegerField(default=0)  # 0 no  1 read  2 write
    # collect = models.CharField(max_length=10000)
    # do = models.CharField(max_length=2000)
    # on_hold = models.CharField(max_length=1000)
    # dropped = models.CharField(max_length=2000)

    def set_collect(self, x):
        while self.file_state != 0:
            time.sleep(0.05)
        self.file_state = 2
        f = open('user_collect' + os.sep + self.bgm_id + '.txt', 'w+')
        for item in x:
            f.write(item['id'] + ' ' + str(item['grade']) + '\n')
        f.close()
        self.file_state = 0

    def get_collect(self):
        while self.file_state == 2:
            time.sleep(0.05)
        self.file_state = 1
        f = open('user_collect'+os.sep+self.bgm_id+'.txt', 'r')
        content = f.readlines()
        f.close()
        self.file_state = 0
        collect = []
        for string in content:
            tmp = string.split()
            collect.append({'id': tmp[0], 'grade': int(tmp[1])})
        return collect
        # return json.loads(self.collect.decode('utf-8').replace("'", "\""))

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
