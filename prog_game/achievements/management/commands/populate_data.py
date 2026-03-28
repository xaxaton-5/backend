import random
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from achievements.models import Achievement, UserAchievement
from users.models import Profile


class Command(BaseCommand):
    help = 'Populate database with achievements and test users'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing achievements and users before creating new ones'
        )
        parser.add_argument(
            '--users',
            type=int,
            default=12,
            help='Number of users to create (default: 12)'
        )
        parser.add_argument(
            '--parents',
            type=int,
            default=4,
            help='Number of parent users to create (default: 4)'
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.clear_data()

        # Создаем достижения из вашего списка
        achievements = self.create_achievements()

        # Создаем пользователей
        users = self.create_users(options['users'], options['parents'])

        # Назначаем достижения пользователям
        self.assign_achievements_to_users(users, achievements)

        self.stdout.write(
            self.style.SUCCESS(
                f'\n✅ Successfully created {len(achievements)} achievements '
                f'and {len(users)} users'
            )
        )

    def clear_data(self):
        """Очистка существующих данных"""
        self.stdout.write('Clearing existing data...')
        UserAchievement.objects.all().delete()
        Achievement.objects.all().delete()
        User.objects.exclude(is_superuser=True).delete()
        self.stdout.write(self.style.SUCCESS('✓ Data cleared successfully'))

    def create_achievements(self):
        """Создание достижений из фронтенд-списка"""
        self.stdout.write('\n📚 Creating achievements...')

        # Данные достижений с эмодзи
        achievements_data = [
            {
                'title': 'Первая переменная',
                'description': 'Создал свою первую переменную',
                'emoji': '📦',
                'exp': 50,
                'condition_type': 'completed_lessons',
                'condition_value': 1
            },
            {
                'title': 'Король циклов',
                'description': 'Решил 10 задач на циклы',
                'emoji': '🔄',
                'exp': 100,
                'condition_type': 'completed_practice_lessons',
                'condition_value': 2,
                'condition_module': 2
            },
            {
                'title': 'Мастер условий',
                'description': 'Решил 10 задач на if/else',
                'emoji': '🤔',
                'exp': 100,
                'condition_type': 'completed_practice_lessons',
                'condition_value': 2,
                'condition_module': 3
            },
            {
                'title': 'Победитель бота',
                'description': 'Прошёл игру "Переменная битва"',
                'emoji': '🎮',
                'exp': 100,
                'condition_type': 'completed_game',
                'condition_value': 'variables'
            },
            {
                'title': 'Повелитель циклов',
                'description': 'Прошёл игру "Цикло-битва"',
                'emoji': '🔄',
                'exp': 100,
                'condition_type': 'completed_game',
                'condition_value': 'loops'
            },
            {
                'title': 'Мастер решений',
                'description': 'Прошёл игру "Робо-битва"',
                'emoji': '🤖',
                'exp': 100,
                'condition_type': 'completed_game',
                'condition_value': 'conditions'
            },
            {
                'title': 'Социальный кодер',
                'description': 'Отправил 50 сообщений в чате',
                'emoji': '💬',
                'exp': 100,
                'condition_type': 'messages_sent',
                'condition_value': 50,
                'is_active': False
            },
            {
                'title': 'Трудоголик',
                'description': 'Провёл 10 часов в обучении',
                'emoji': '⏰',
                'exp': 150,
                'condition_type': 'learning_time_hours',
                'condition_value': 10,
                'is_active': False
            },
            {
                'title': 'Ежедневный вход',
                'description': 'Заходить в приложение 7 дней подряд',
                'emoji': '📅',
                'exp': 50,
                'condition_type': 'daily_streak',
                'condition_value': 7
            },
            {
                'title': 'Отличник',
                'description': 'Пройти тест на 100%',
                'emoji': '⭐️',
                'exp': 100,
                'condition_type': 'perfect_test',
                'condition_value': 100,
                'is_active': False
            },
            {
                'title': 'Новичок',
                'description': 'Завершить первый урок',
                'emoji': '🌟',
                'exp': 25,
                'condition_type': 'completed_lessons',
                'condition_value': 1
            },
            {
                'title': 'Усердный ученик',
                'description': 'Завершить 10 уроков',
                'emoji': '📚',
                'exp': 100,
                'condition_type': 'completed_lessons',
                'condition_value': 10
            },
            {
                'title': 'Мастер программирования',
                'description': 'Завершить все уроки модуля 1',
                'emoji': '💻',
                'exp': 200,
                'condition_type': 'completed_module',
                'condition_value': 1
            },
            {
                'title': 'Гуру циклов',
                'description': 'Завершить все уроки модуля 2',
                'emoji': '🔄',
                'exp': 200,
                'condition_type': 'completed_module',
                'condition_value': 2
            },
            {
                'title': 'Стремительный старт',
                'description': 'Набрать 500 очков опыта',
                'emoji': '⚡',
                'exp': 150,
                'condition_type': 'total_exp',
                'condition_value': 500
            },
            {
                'title': 'Опытный кодер',
                'description': 'Набрать 2000 очков опыта',
                'emoji': '🏆',
                'exp': 300,
                'condition_type': 'total_exp',
                'condition_value': 2000
            },
            {
                'title': 'Легенда',
                'description': 'Набрать 10000 очков опыта',
                'emoji': '👑',
                'exp': 1000,
                'condition_type': 'total_exp',
                'condition_value': 10000
            }
        ]

        achievements = []
        for data in achievements_data:
            achievement, created = Achievement.objects.get_or_create(
                title=data['title'],
                defaults={
                    'description': data['description'],
                    'emoji': data['emoji'],
                    'exp': data['exp'],
                }
            )

            # Если достижение уже существует, обновляем поля
            if not created:
                achievement.description = data['description']
                achievement.emoji = data['emoji']
                achievement.exp = data['exp']
                achievement.save()

            achievements.append(achievement)

            if created:
                self.stdout.write(f'  ✓ Created: {achievement.emoji} {achievement.title} (+{data["exp"]} XP)')
            else:
                self.stdout.write(f'  ○ Updated: {achievement.emoji} {achievement.title}')

        return achievements

    def create_users(self, total_users, parent_count):
        """Создание пользователей"""
        self.stdout.write(f'\n👥 Creating {total_users} users ({parent_count} parents)...')

        parent_profiles = [
            ('МаминКодер', 'ivan.petrov@example.com', 'Иван', 'Петров'),
            ('СуперКодер', 'maria.sokolova@example.com', 'Мария', 'Соколова'),
            ('Сергей Иванов', 'sergey.ivanov@example.com', 'Сергей', 'Иванов'),
            ('Елена Смирнова', 'elena.smirnova@example.com', 'Елена', 'Смирнова'),
            ('DebugБатя', 'dmitry.kozlov@example.com', 'Дмитрий', 'Козлов'),
            ('МамаНаПитоне', 'anna.fedorova@example.com', 'Анна', 'Федорова'),
        ]
        child_profiles = [
            ('Программист2000', 'alexey.petrov@example.com', 'Алексей', 'Петров'),
            ('КодикОгонь', 'olga.sokolova@example.com', 'Ольга', 'Соколова'),
            ('Никита Иванов', 'nikita.ivanov@example.com', 'Никита', 'Иванов'),
            ('Алина Смирнова', 'alina.smirnova@example.com', 'Алина', 'Смирнова'),
            ('ПиксельныйГений', 'egor.kozlov@example.com', 'Егор', 'Козлов'),
            ('Полина Федорова', 'polina.fedorova@example.com', 'Полина', 'Федорова'),
            ('МегаАлгоритм', 'maksim.novikov@example.com', 'Максим', 'Новиков'),
            ('София Орлова', 'sofia.orlova@example.com', 'София', 'Орлова'),
            ('Тимур Кузнецов', 'timur.kuznetsov@example.com', 'Тимур', 'Кузнецов'),
            ('Лиза Романова', 'liza.romanova@example.com', 'Лиза', 'Романова'),
        ]
        adult_profiles = [
            ('КодМастер', 'andrey.volkov@example.com', 'Андрей', 'Волков'),
            ('ТихийКомпилятор', 'svetlana.morozova@example.com', 'Светлана', 'Морозова'),
            ('ДядяДебаг', 'kirill.zaitsev@example.com', 'Кирилл', 'Зайцев'),
            ('ФункцияУспеха', 'veronika.pavlova@example.com', 'Вероника', 'Павлова'),
        ]

        # Создаем родителей
        parents = []
        for i in range(parent_count):
            username, email, first_name, last_name = parent_profiles[i % len(parent_profiles)]
            user = self.create_single_user(
                username=username,
                email=email,
                first_name=first_name,
                last_name=last_name,
                is_parent=True,
                exp=random.randint(500, 5000)
            )
            parents.append(user)
            self.stdout.write(f'  ✓ Created parent: {user.username} (XP: {user.profile.exp})')

        # Создаем детей
        children_count = total_users - parent_count
        children = []

        for i in range(children_count):
            # Выбираем случайного родителя
            parent = random.choice(parents) if parents else None
            username, email, first_name, last_name = child_profiles[i % len(child_profiles)]

            user = self.create_single_user(
                username=username,
                email=email,
                first_name=first_name,
                last_name=last_name,
                is_parent=False,
                parent=parent.profile if parent else None,
                exp=random.randint(500, 5000)
            )
            children.append(user)
            self.stdout.write(
                f'  ✓ Created child: {user.username} (XP: {user.profile.exp}, '
                f'Parent: {parent.username if parent else "None"})'
            )

        # Добавляем взрослых без детей
        adults_count = max(0, total_users - parent_count - children_count)
        for i in range(adults_count):
            username, email, first_name, last_name = adult_profiles[i % len(adult_profiles)]
            user = self.create_single_user(
                username=username,
                email=email,
                first_name=first_name,
                last_name=last_name,
                is_parent=False,
                parent=None,
                exp=random.randint(500, 5000)
            )
            children.append(user)
            self.stdout.write(f'  ✓ Created adult: {user.username} (XP: {user.profile.exp})')

        return parents + children

    def create_single_user(self, username, email, first_name, last_name, is_parent=False, parent=None, exp=0):
        """Создание одного пользователя"""
        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                'email': email,
                'first_name': first_name,
                'last_name': last_name,
                'is_active': True
            }
        )

        if created:
            user.set_password('password123')
            user.save()

            # Обновляем профиль
            profile = user.profile
            profile.is_parent = is_parent
            if parent:
                profile.parent = parent
            profile.exp = exp
            profile.save()
        else:
            # Обновляем существующего пользователя
            user.email = email
            user.first_name = first_name
            user.last_name = last_name
            user.is_active = True
            user.save(update_fields=['email', 'first_name', 'last_name', 'is_active'])

            profile = user.profile
            if is_parent:
                profile.is_parent = is_parent
            if parent:
                profile.parent = parent
            profile.exp = exp
            profile.save()

        return user

    def assign_achievements_to_users(self, users, achievements):
        """Назначение достижений пользователям"""
        self.stdout.write(f'\n🏆 Assigning achievements to users...')

        assigned_count = 0

        for user in users:
            # Определяем, какие достижения заслужил пользователь на основе его опыта
            earned_achievements = []

            for achievement in achievements:
                # Проверяем, подходит ли достижение по опыту
                if achievement.exp <= user.profile.exp:
                    earned_achievements.append(achievement)

            # Назначаем от 2 до 4 достижений (но не больше, чем заработано)
            num_to_assign = min(
                random.randint(2, 4),
                len(earned_achievements)
            )

            if num_to_assign > 0 and earned_achievements:
                selected_achievements = random.sample(earned_achievements, num_to_assign)

                for achievement in selected_achievements:
                    user_achievement, created = UserAchievement.objects.get_or_create(
                        user=user,
                        achievement=achievement,
                        defaults={'datetime': timezone.now()}
                    )

                    if created:
                        assigned_count += 1
                        self.stdout.write(f'  ✓ {user.username} earned: {achievement.emoji} {achievement.title}')

        self.stdout.write(self.style.SUCCESS(f'\n✨ Assigned {assigned_count} achievements in total'))

    def create_test_families(self):
        """Создание тестовых семей (можно вызвать отдельно)"""
        self.stdout.write('\n👨‍👩‍👧‍👦 Creating test families...')

        # Создаем семью с двумя родителями и двумя детьми
        parent1 = self.create_single_user(
            username='МаминКодер',
            email='ivan@family.com',
            first_name='Иван',
            last_name='Петров',
            is_parent=True,
            exp=random.randint(500, 5000)
        )

        parent2 = self.create_single_user(
            username='СуперКодер',
            email='maria@family.com',
            first_name='Мария',
            last_name='Петрова',
            is_parent=True,
            exp=random.randint(500, 5000)
        )

        # Дети
        child1 = self.create_single_user(
            username='Программист2000',
            email='aleksandr.petrov@family.com',
            first_name='Александр',
            last_name='Петров',
            is_parent=False,
            parent=parent1.profile,
            exp=random.randint(500, 5000)
        )

        child2 = self.create_single_user(
            username='КодикОгонь',
            email='olga.petrova@family.com',
            first_name='Ольга',
            last_name='Петрова',
            is_parent=False,
            parent=parent1.profile,
            exp=random.randint(500, 5000)
        )

        self.stdout.write(self.style.SUCCESS(
            f'✓ Created family: {parent1.username}, {parent2.username} '
            f'with children {child1.username}, {child2.username}'
        ))

        return [parent1, parent2, child1, child2]
