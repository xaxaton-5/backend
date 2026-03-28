from django.contrib.auth.models import User
from django.db import models


class Guild(models.Model):
    name = models.CharField(max_length=120, unique=True)
    slug = models.SlugField(max_length=120, unique=True)
    emoji = models.CharField(max_length=4, default='🛡️')
    tagline = models.CharField(max_length=160)
    description = models.TextField()
    focus = models.CharField(max_length=120)
    topics = models.JSONField(default=list, blank=True)
    users = models.ManyToManyField(
        User,
        through='GuildMembership',
        related_name='guilds',
    )

    class Meta:
        ordering = ['name']
        verbose_name = 'Guild'
        verbose_name_plural = 'Guilds'

    def __str__(self):
        return f'{self.emoji} {self.name}'


class GuildMembership(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='guild_membership',
    )
    guild = models.ForeignKey(
        Guild,
        on_delete=models.CASCADE,
        related_name='memberships',
    )
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-joined_at']
        verbose_name = 'Guild membership'
        verbose_name_plural = 'Guild memberships'

    def __str__(self):
        return f'{self.user.username} -> {self.guild.name}'
