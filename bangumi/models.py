# coding=utf-8

from django.db import models
import json
# CONST VALUE
NAME_MAX_LENGTH = 25
TIME_MAX_LENGTH = 40


class bgmUser(models.Model):
    name = models.CharField(max_length=NAME_MAX_LENGTH)
    bgmid = models.CharField(max_length=NAME_MAX_LENGTH)
    time = models.DateField(max_length=TIME_MAX_LENGTH) # 3天信息过期，进行更新
    state = models.SmallIntegerField(default=0)
    collect = models.CharField()
    do = models.CharField()
    on_hold = models.CharField()
    dropped = models.CharField()

    def set_collect(self, x):
        self.collect = json.dumps(x)

    def get_collect(self):
        return json.loads(self.collect)

    def __str__(self):
        return self.bgmid