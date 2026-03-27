from django.contrib.auth.models import User
from django.db import models


class ChatMessage(models.Model):
    text = models.TextField()
    from_user = models.ForeignKey(User, on_delete=models.CASCADE)
    sent_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)
