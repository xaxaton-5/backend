from django.contrib.auth.hashers import make_password
from django.db import migrations


ACHIEVEMENTS_DATA = [
    {
        'title': 'Первая переменная',
        'description': 'Создал свою первую переменную',
        'emoji': '📦',
        'exp': 50,
    },
    {
        'title': 'Король циклов',
        'description': 'Решил 10 задач на циклы',
        'emoji': '🔄',
        'exp': 100,
    },
    {
        'title': 'Мастер условий',
        'description': 'Решил 10 задач на if/else',
        'emoji': '🤔',
        'exp': 100,
    },
    {
        'title': 'Победитель бота',
        'description': 'Прошёл игру "Переменная битва"',
        'emoji': '🎮',
        'exp': 100,
    },
    {
        'title': 'Повелитель циклов',
        'description': 'Прошёл игру "Цикло-битва"',
        'emoji': '🌀',
        'exp': 100,
    },
    {
        'title': 'Мастер решений',
        'description': 'Прошёл игру "Робо-битва"',
        'emoji': '🤖',
        'exp': 100,
    },
    {
        'title': 'Социальный кодер',
        'description': 'Отправил 50 сообщений в чате',
        'emoji': '💬',
        'exp': 100,
    },
    {
        'title': 'Трудоголик',
        'description': 'Провёл 10 часов в обучении',
        'emoji': '⏰',
        'exp': 150,
    },
    {
        'title': 'Ежедневный вход',
        'description': 'Заходил в приложение 7 дней подряд',
        'emoji': '📅',
        'exp': 50,
    },
    {
        'title': 'Отличник',
        'description': 'Прошёл тест на 100%',
        'emoji': '⭐',
        'exp': 100,
    },
    {
        'title': 'Новичок',
        'description': 'Завершил первый урок',
        'emoji': '🌟',
        'exp': 25,
    },
    {
        'title': 'Усердный ученик',
        'description': 'Завершил 10 уроков',
        'emoji': '📚',
        'exp': 100,
    },
    {
        'title': 'Мастер программирования',
        'description': 'Завершил все уроки модуля 1',
        'emoji': '💻',
        'exp': 200,
    },
    {
        'title': 'Гуру циклов',
        'description': 'Завершил все уроки модуля 2',
        'emoji': '♾️',
        'exp': 200,
    },
    {
        'title': 'Стремительный старт',
        'description': 'Набрал 500 очков опыта',
        'emoji': '⚡',
        'exp': 150,
    },
    {
        'title': 'Опытный кодер',
        'description': 'Набрал 2000 очков опыта',
        'emoji': '🏆',
        'exp': 300,
    },
    {
        'title': 'Легенда',
        'description': 'Набрал 10000 очков опыта',
        'emoji': '👑',
        'exp': 1000,
    },
]

SEEDED_USERS = [
    {
        'username': 'МаминКодер',
        'email': 'ivan.petrov@example.com',
        'first_name': 'Иван',
        'last_name': 'Петров',
        'password': 'password123',
        'is_parent': True,
        'parent_username': None,
        'exp': 4800,
        'guild_slug': 'cosmo-mentors',
    },
    {
        'username': 'СуперКодер',
        'email': 'maria.sokolova@example.com',
        'first_name': 'Мария',
        'last_name': 'Соколова',
        'password': 'password123',
        'is_parent': True,
        'parent_username': None,
        'exp': 5600,
        'guild_slug': 'frontend-seekers',
    },
    {
        'username': 'DebugБатя',
        'email': 'dmitry.kozlov@example.com',
        'first_name': 'Дмитрий',
        'last_name': 'Козлов',
        'password': 'password123',
        'is_parent': True,
        'parent_username': None,
        'exp': 6400,
        'guild_slug': 'backend-guardians',
    },
    {
        'username': 'МамаНаПитоне',
        'email': 'anna.fedorova@example.com',
        'first_name': 'Анна',
        'last_name': 'Федорова',
        'password': 'password123',
        'is_parent': True,
        'parent_username': None,
        'exp': 5900,
        'guild_slug': 'backend-guardians',
    },
    {
        'username': 'Программист2000',
        'email': 'alexey.petrov@example.com',
        'first_name': 'Алексей',
        'last_name': 'Петров',
        'password': 'password123',
        'is_parent': False,
        'parent_username': 'МаминКодер',
        'exp': 2100,
        'guild_slug': 'frontend-seekers',
    },
    {
        'username': 'КодикОгонь',
        'email': 'olga.sokolova@example.com',
        'first_name': 'Ольга',
        'last_name': 'Соколова',
        'password': 'password123',
        'is_parent': False,
        'parent_username': 'СуперКодер',
        'exp': 2600,
        'guild_slug': 'frontend-seekers',
    },
    {
        'username': 'ПиксельныйГений',
        'email': 'egor.kozlov@example.com',
        'first_name': 'Егор',
        'last_name': 'Козлов',
        'password': 'password123',
        'is_parent': False,
        'parent_username': 'DebugБатя',
        'exp': 10800,
        'guild_slug': 'game-alchemists',
    },
    {
        'username': 'МегаАлгоритм',
        'email': 'maksim.novikov@example.com',
        'first_name': 'Максим',
        'last_name': 'Новиков',
        'password': 'password123',
        'is_parent': False,
        'parent_username': 'МамаНаПитоне',
        'exp': 3200,
        'guild_slug': 'backend-guardians',
    },
    {
        'username': 'ТихийКомпилятор',
        'email': 'svetlana.morozova@example.com',
        'first_name': 'Светлана',
        'last_name': 'Морозова',
        'password': 'password123',
        'is_parent': False,
        'parent_username': None,
        'exp': 3600,
        'guild_slug': 'game-alchemists',
    },
    {
        'username': 'ФункцияУспеха',
        'email': 'veronika.pavlova@example.com',
        'first_name': 'Вероника',
        'last_name': 'Павлова',
        'password': 'password123',
        'is_parent': False,
        'parent_username': None,
        'exp': 3900,
        'guild_slug': 'frontend-seekers',
    },
    {
        'username': 'БайтРыцарь',
        'email': 'kirill.zaitsev@example.com',
        'first_name': 'Кирилл',
        'last_name': 'Зайцев',
        'password': 'password123',
        'is_parent': False,
        'parent_username': None,
        'exp': 4400,
        'guild_slug': 'backend-guardians',
    },
    {
        'username': 'КодовыйФеникс',
        'email': 'sofia.orlova@example.com',
        'first_name': 'София',
        'last_name': 'Орлова',
        'password': 'password123',
        'is_parent': False,
        'parent_username': None,
        'exp': 1750,
        'guild_slug': 'cosmo-mentors',
    },
    {
        'username': 'ЛупМастер',
        'email': 'timur.kuznetsov@example.com',
        'first_name': 'Тимур',
        'last_name': 'Кузнецов',
        'password': 'password123',
        'is_parent': False,
        'parent_username': None,
        'exp': 2250,
        'guild_slug': 'game-alchemists',
    },
    {
        'username': 'АлгоЗвезда',
        'email': 'liza.romanova@example.com',
        'first_name': 'Елизавета',
        'last_name': 'Романова',
        'password': 'password123',
        'is_parent': False,
        'parent_username': None,
        'exp': 1450,
        'guild_slug': 'cosmo-mentors',
    },
]

NEW_ACHIEVEMENT_TITLES = [
    'Новичок',
    'Усердный ученик',
    'Мастер программирования',
    'Гуру циклов',
    'Стремительный старт',
    'Опытный кодер',
    'Легенда',
]


def seed_achievements(apps):
    Achievement = apps.get_model('achievements', 'Achievement')
    achievements_by_title = {}

    for achievement_data in ACHIEVEMENTS_DATA:
        achievement, _ = Achievement.objects.update_or_create(
            title=achievement_data['title'],
            defaults={
                'description': achievement_data['description'],
                'emoji': achievement_data['emoji'],
                'exp': achievement_data['exp'],
            },
        )
        achievements_by_title[achievement.title] = achievement

    return achievements_by_title


def seed_users(apps):
    User = apps.get_model('auth', 'User')
    Profile = apps.get_model('users', 'Profile')
    created_users = {}

    for user_data in SEEDED_USERS:
        user, created = User.objects.get_or_create(
            username=user_data['username'],
            defaults={
                'email': user_data['email'],
                'first_name': user_data['first_name'],
                'last_name': user_data['last_name'],
                'password': make_password(user_data['password']),
                'is_active': True,
            },
        )

        if not created:
            user.email = user_data['email']
            user.first_name = user_data['first_name']
            user.last_name = user_data['last_name']
            user.password = make_password(user_data['password'])
            user.is_active = True
            user.save(update_fields=['email', 'first_name', 'last_name', 'password', 'is_active'])

        Profile.objects.get_or_create(user=user)
        created_users[user.username] = user

    for user_data in SEEDED_USERS:
        user = created_users[user_data['username']]
        profile = Profile.objects.get(user=user)
        profile.is_parent = user_data['is_parent']
        profile.exp = user_data['exp']
        profile.parent = None

        parent_username = user_data['parent_username']
        if parent_username:
            profile.parent = Profile.objects.get(user=created_users[parent_username])

        profile.save(update_fields=['is_parent', 'exp', 'parent'])

    return created_users


def seed_guild_memberships(apps, created_users):
    Guild = apps.get_model('guilds', 'Guild')
    GuildMembership = apps.get_model('guilds', 'GuildMembership')

    guilds_by_slug = {guild.slug: guild for guild in Guild.objects.all()}

    for user_data in SEEDED_USERS:
        guild_slug = user_data.get('guild_slug')
        if not guild_slug:
            continue

        GuildMembership.objects.update_or_create(
            user=created_users[user_data['username']],
            defaults={'guild': guilds_by_slug[guild_slug]},
        )


def get_titles_for_exp(exp):
    titles = ['Первая переменная', 'Новичок']

    if exp >= 500:
        titles.append('Стремительный старт')
    if exp >= 1000:
        titles.extend(['Победитель бота', 'Ежедневный вход'])
    if exp >= 1500:
        titles.extend(['Мастер условий', 'Повелитель циклов'])
    if exp >= 2000:
        titles.extend(['Король циклов', 'Мастер решений', 'Опытный кодер'])
    if exp >= 3000:
        titles.extend(['Усердный ученик', 'Мастер программирования', 'Гуру циклов'])
    if exp >= 5000:
        titles.extend(['Социальный кодер', 'Трудоголик', 'Отличник'])
    if exp >= 10000:
        titles.append('Легенда')

    return titles


def seed_user_achievements(apps, created_users, achievements_by_title):
    UserAchievement = apps.get_model('achievements', 'UserAchievement')

    for user_data in SEEDED_USERS:
        user = created_users[user_data['username']]
        for title in get_titles_for_exp(user_data['exp']):
            UserAchievement.objects.get_or_create(
                user=user,
                achievement=achievements_by_title[title],
            )


def seed_demo_data(apps, schema_editor):
    achievements_by_title = seed_achievements(apps)
    created_users = seed_users(apps)
    seed_guild_memberships(apps, created_users)
    seed_user_achievements(apps, created_users, achievements_by_title)


def remove_seed_demo_data(apps, schema_editor):
    User = apps.get_model('auth', 'User')
    Achievement = apps.get_model('achievements', 'Achievement')

    User.objects.filter(username__in=[user['username'] for user in SEEDED_USERS]).delete()
    Achievement.objects.filter(title__in=NEW_ACHIEVEMENT_TITLES).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0006_alter_userresult_key'),
        ('guilds', '0002_seed_guilds'),
        ('achievements', '0005_alter_achievement_emoji'),
    ]

    operations = [
        migrations.RunPython(seed_demo_data, remove_seed_demo_data),
    ]
