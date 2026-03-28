from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Demo data is seeded by migrations and no longer populated from this command.'

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.WARNING(
                'Команда populate_data больше не создаёт данные. '
                'Демо-данные теперь заполняются сид-миграциями при применении migrations.'
            )
        )
