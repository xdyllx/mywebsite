from django.contrib import admin
from models import bgmUser, Anime, Episode

import sys

reload(sys)
sys.setdefaultencoding("utf-8")

admin.site.register(bgmUser)
admin.site.register(Anime)
admin.site.register(Episode)
