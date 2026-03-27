from django.contrib.auth.models import User
from django.db import models

# User - Achievement с ManyToMany, но через посредника UserAchievement

class Achievement(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    image = models.ImageField(upload_to='achievement_images/')
    datetime = models.DateTimeField(auto_now_add=True)
    exp = models.IntegerField()
    users = models.ManyToManyField(
        User,
        through='UserAchievement',
        related_name='achievements'
    )

class UserAchievement(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    achievement = models.ForeignKey(Achievement, on_delete=models.CASCADE)
    datetime = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'achievement']
        ordering = ['-datetime']
    
    def __str__(self):
        return f"{self.user.username} - {self.achievement.name} - {self.datetime}"