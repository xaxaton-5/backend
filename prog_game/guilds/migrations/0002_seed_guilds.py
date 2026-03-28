from django.db import migrations


def seed_guilds(apps, schema_editor):
    Guild = apps.get_model('guilds', 'Guild')

    guilds = [
        {
            'name': 'Фронтенд-искатели',
            'slug': 'frontend-seekers',
            'emoji': '🎨',
            'tagline': 'Для тех, кто любит делать интерфейсы живыми',
            'description': 'Создаём яркие страницы, делимся идеями по анимациям и собираем мини-проекты для портфолио.',
            'focus': 'интерфейсы и UX',
            'topics': ['HTML', 'CSS', 'Vue', 'Анимации'],
        },
        {
            'name': 'Бэкенд-стражи',
            'slug': 'backend-guardians',
            'emoji': '⚙️',
            'tagline': 'Тут живёт логика, API и надёжные сервисы',
            'description': 'Обсуждаем архитектуру, базы данных и учимся строить устойчивые серверные приложения.',
            'focus': 'API и серверы',
            'topics': ['Python', 'Django', 'API', 'PostgreSQL'],
        },
        {
            'name': 'Игровые алхимики',
            'slug': 'game-alchemists',
            'emoji': '🧪',
            'tagline': 'Превращаем код в механику и приключение',
            'description': 'Придумываем игровые уровни, тестируем механики и вместе улучшаем обучающие мини-игры.',
            'focus': 'геймдизайн',
            'topics': ['GameDev', 'Логика', 'Баланс', 'Сюжеты'],
        },
        {
            'name': 'Космо-менторы',
            'slug': 'cosmo-mentors',
            'emoji': '🚀',
            'tagline': 'Поддержка новичков и командные разборы',
            'description': 'Помогаем новичкам стартовать, проводим разборы кода и собираем доброжелательное комьюнити.',
            'focus': 'обучение и помощь',
            'topics': ['Менторство', 'Разбор кода', 'Командная работа', 'Рост'],
        },
    ]

    for guild_data in guilds:
        Guild.objects.update_or_create(
            slug=guild_data['slug'],
            defaults=guild_data,
        )


def remove_guilds(apps, schema_editor):
    Guild = apps.get_model('guilds', 'Guild')
    Guild.objects.filter(
        slug__in=['frontend-seekers', 'backend-guardians', 'game-alchemists', 'cosmo-mentors']
    ).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('guilds', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(seed_guilds, remove_guilds),
    ]
