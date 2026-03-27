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
            'parent_username': None,
        },
        {
            'username': 'child_demo',
            'email': 'child@example.com',
            'first_name': 'Demo',
            'last_name': 'Child',
            'password': 'demo12345',
            'is_parent': False,
            'parent_username': 'parent_demo',
        },
        {
            'username': 'mentor_demo',
            'email': 'mentor@example.com',
            'first_name': 'Demo',
            'last_name': 'Mentor',
            'password': 'demo12345',
            'is_parent': True,
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
                'exp': 0,
            },
        )

    for user_data in users_data:
        user = created_users[user_data['username']]
        profile = Profile.objects.get(user=user)
        profile.is_parent = user_data['is_parent']
        parent_username = user_data['parent_username']
        profile.parent = None
        if parent_username:
            profile.parent = Profile.objects.get(user=created_users[parent_username])
        profile.save(update_fields=['is_parent', 'parent'])

    achievements_data = [
        {
            'title': 'First Login',
            'description': 'User successfully entered the platform for the first time.',
            'image': 'achievement_images/seed/first_login.png',
            'exp': 10,
        },
        {
            'title': 'Task Starter',
            'description': 'User completed the first training step.',
            'image': 'achievement_images/seed/task_starter.png',
            'exp': 25,
        },
        {
            'title': 'Fast Learner',
            'description': 'User earned several achievements in a row.',
            'image': 'achievement_images/seed/fast_learner.png',
            'exp': 50,
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

    granted_pairs = [
        ('child_demo', 'First Login'),
        ('child_demo', 'Task Starter'),
        ('parent_demo', 'First Login'),
    ]

    for username, achievement_title in granted_pairs:
        user = created_users[username]
        achievement = created_achievements[achievement_title]
        UserAchievement.objects.get_or_create(
            user=user,
            achievement=achievement,
        )

    for profile in Profile.objects.select_related('user'):
        total_exp = sum(
            item.achievement.exp
            for item in UserAchievement.objects.filter(user=profile.user).select_related('achievement')
        )
        if profile.exp != total_exp:
            profile.exp = total_exp
            profile.save(update_fields=['exp'])


def remove_initial_data(apps, schema_editor):
    User = apps.get_model('auth', 'User')
    Achievement = apps.get_model('achievements', 'Achievement')

    User.objects.filter(username__in=['parent_demo', 'child_demo', 'mentor_demo']).delete()
    Achievement.objects.filter(
        title__in=['First Login', 'Task Starter', 'Fast Learner']
    ).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_rename_isparent_profile_is_parent'),
        ('achievements', '0002_alter_userachievement_unique_together_and_more'),
    ]

    operations = [
        migrations.RunPython(seed_initial_data, remove_initial_data),
    ]
