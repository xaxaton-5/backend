from django.contrib.auth.hashers import make_password
from django.db import migrations


def seed_initial_data(apps, schema_editor):
    User = apps.get_model('auth', 'User')
    Profile = apps.get_model('users', 'Profile')
    Achievement = apps.get_model('achievements', 'Achievement')
    UserAchievement = apps.get_model('achievements', 'UserAchievement')

    users_data = [
        {
            'username': 'parent_demo',
            'email': 'parent@example.com',
            'first_name': 'Demo',
            'last_name': 'Parent',
            'password': 'demo12345',
            'is_parent': True,
            'exp': 5000,
            'parent_username': None,
        },
        {
            'username': 'child_demo',
            'email': 'child@example.com',
            'first_name': 'Demo',
            'last_name': 'Child',
            'password': 'demo12345',
            'is_parent': False,
            'exp': 10000,
            'parent_username': 'parent_demo',
        },
        {
            'username': 'mentor_demo',
            'email': 'mentor@example.com',
            'first_name': 'Demo',
            'last_name': 'Mentor',
            'password': 'demo12345',
            'is_parent': True,
            'exp': 0,
            'parent_username': None,
        },
    ]

    created_users = {}

    for user_data in users_data:
        user, _ = User.objects.get_or_create(
            username=user_data['username'],
            defaults={
                'email': user_data['email'],
                'first_name': user_data['first_name'],
                'last_name': user_data['last_name'],
                'password': make_password(user_data['password']),
                'is_active': True,
            },
        )
        created_users[user.username] = user

        Profile.objects.get_or_create(
            user=user,
            defaults={
                'is_parent': user_data['is_parent'],
                'exp': user_data['exp'],
            },
        )

    for user_data in users_data:
        user = created_users[user_data['username']]
        profile = Profile.objects.get(user=user)
        profile.is_parent = user_data['is_parent']
        profile.exp = user_data['exp']
        parent_username = user_data['parent_username']
        profile.parent = None
        if parent_username:
            profile.parent = Profile.objects.get(user=created_users[parent_username])
        profile.save(update_fields=['is_parent', 'exp', 'parent'])

    achievements_data = [
        {
            'title': 'Первая переменная',
            'description': 'Создал свою первую переменную',
            'image': 'achievement_images/seed/pervaya_peremennaya.png',
            'exp': 50,
        },
        {
            'title': 'Король циклов',
            'description': 'Решил 10 задач на циклы',
            'image': 'achievement_images/seed/korol_ciklov.png',
            'exp': 100,
        },
        {
            'title': 'Мастер условий',
            'description': 'Решил 10 задач на if/else',
            'image': 'achievement_images/seed/master_usloviy.png',
            'exp': 100,
        },
        {
            'title': 'Победитель бота',
            'description': 'Прошёл игру "Переменная битва"',
            'image': 'achievement_images/seed/pobeditel_bota.png',
            'exp': 100,
        },
        {
            'title': 'Повелитель циклов',
            'description': 'Прошёл игру "Цикло-битва"',
            'image': 'achievement_images/seed/povelitel_ciklov.png',
            'exp': 100,
        },
        {
            'title': 'Мастер решений',
            'description': 'Прошёл игру "Робо-битва"',
            'image': 'achievement_images/seed/master_resheniy.png',
            'exp': 100,
        },
        {
            'title': 'Социальный кодер',
            'description': 'Отправил 50 сообщений в чате',
            'image': 'achievement_images/seed/socialniy_koder.png',
            'exp': 100,
        },
        {
            'title': 'Трудоголик',
            'description': 'Провёл 10 часов в обучении',
            'image': 'achievement_images/seed/trudogolik.png',
            'exp': 150,
        },
        {
            'title': 'Ежедневный вход',
            'description': 'Заходить в приложение 7 дней подряд',
            'image': 'achievement_images/seed/ezhednevniy_vhod.png',
            'exp': 50,
        },
        {
            'title': 'Отличник',
            'description': 'Пройти тест на 100%',
            'image': 'achievement_images/seed/otlichnik.png',
            'exp': 100,
        },
    ]

    created_achievements = {}

    for achievement_data in achievements_data:
        achievement, _ = Achievement.objects.get_or_create(
            title=achievement_data['title'],
            defaults={
                'description': achievement_data['description'],
                'image': achievement_data['image'],
                'exp': achievement_data['exp'],
            },
        )
        created_achievements[achievement.title] = achievement


def remove_initial_data(apps, schema_editor):
    User = apps.get_model('auth', 'User')
    Achievement = apps.get_model('achievements', 'Achievement')

    User.objects.filter(username__in=['parent_demo', 'child_demo', 'mentor_demo']).delete()
    Achievement.objects.filter(
        title__in=[
            'Первая переменная',
            'Король циклов',
            'Мастер условий',
            'Победитель бота',
            'Повелитель циклов',
            'Мастер решений',
            'Социальный кодер',
            'Трудоголик',
            'Ежедневный вход',
            'Отличник',
        ]
    ).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_rename_isparent_profile_is_parent'),
        ('achievements', '0002_alter_userachievement_unique_together_and_more'),
    ]

    operations = [
        migrations.RunPython(seed_initial_data, remove_initial_data),
    ]
