from django.urls import path

from guilds import api


urlpatterns = [
    path('guilds/list/', api.guild_list),
    path('guilds/join/', api.guild_join),
]
