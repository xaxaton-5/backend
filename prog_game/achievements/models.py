from django.contrib.auth.models import User
from django.db import models

# Оставляем функцию для обратной совместимости со старыми миграциями
def achievement_image_path(instance, filename):
    return 'achievement_images/{0}/{1}'.format(instance.id, filename)

class Achievement(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    emoji = models.CharField(max_length=2, default='🏆')
    exp = models.IntegerField()
    users = models.ManyToManyField(
        User,
        through='UserAchievement',
        related_name='achievements'
    )
    
    def __str__(self):
        return f"{self.emoji} {self.title}"

class UserAchievement(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    achievement = models.ForeignKey(Achievement, on_delete=models.CASCADE)
    datetime = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'achievement'],
                name='unique_user_achievement'
            )
        ]
        ordering = ['-datetime']
    
    def __str__(self):
        return f"{self.user.username} - {self.achievement.title} - {self.datetime}"