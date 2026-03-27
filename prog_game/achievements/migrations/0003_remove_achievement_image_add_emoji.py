from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('achievements', '0002_alter_userachievement_unique_together_and_more'),
    ]

    operations = [
        # Удаляем поле image
        migrations.RemoveField(
            model_name='achievement',
            name='image',
        ),
        # Добавляем поле emoji
        migrations.AddField(
            model_name='achievement',
            name='emoji',
            field=models.CharField(
                default='🏆', 
                help_text='Эмодзи для достижения (2 символа)', 
                max_length=2
            ),
        ),
    ]