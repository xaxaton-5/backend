from django.urls import path

from messaging import api


urlpatterns = [
    path('messages/list/', api.message_list),
    path('messages/send/', api.message_send),
]
