from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


class Profile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile'
    )
    
    exp = models.IntegerField(default=0, help_text="Опыт пользователя")
    is_parent = models.BooleanField(default=False, help_text="Является ли пользователь родителем")
    parent = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='children',
        help_text="ID родителя (если пользователь - ребенок)"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Profile'
        verbose_name_plural = 'Profiles'
    
    def __str__(self):
        return f"Profile of {self.user.username}"
    
    def add_exp(self, amount):
        """Добавить опыт пользователю"""
        self.exp += amount
        self.save(update_fields=['exp'])
        return self.exp


class UserResult(models.Model):
    """Модель для сохранения результатов прохождения уроков/тестов/практик"""
    
    class ResultType(models.TextChoices):
        TEST = 'test', 'Тест'
        THEORY = 'theory', 'Теория'
        PRACTICE = 'practice', 'Практика'
        GAME = 'game', 'Игра'
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='results',
        verbose_name='Пользователь'
    )
    result_type = models.CharField(
        max_length=20,
        choices=ResultType.choices,
        verbose_name='Тип результата'
    )
    exp_earned = models.IntegerField(
        default=0,
        verbose_name='Заработанный опыт'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    
    class Meta:
        verbose_name = 'Результат пользователя'
        verbose_name_plural = 'Результаты пользователей'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'result_type']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.result_type} - {self.created_at}"


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Создает профиль при создании пользователя"""
    if created:
        Profile.objects.create(user=instance)