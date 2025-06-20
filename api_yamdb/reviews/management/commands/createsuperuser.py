from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils.text import capfirst
from getpass import getpass

User = get_user_model()


class Command(BaseCommand):

    def handle(self, *args, **options):
        while True:
            username = input(
                capfirst(User._meta.get_field('username').verbose_name) + ': '
            )
            if username.lower() == 'me':
                self.stderr.write(
                    self.style.ERROR(
                        "Имя пользователя 'me' использовать нельзя"
                    )
                )
                continue
            if User.objects.filter(username=username).exists():
                self.stderr.write(
                    self.style.ERROR(
                        "Пользователь с таким именем уже существует"
                    )
                )
                continue
            break
        email = input('Email: ')
        while True:
            password = getpass('Пароль: ')
            password2 = getpass('Подтвердите пароль: ')
            if password != password2:
                self.stderr.write(self.style.ERROR('Пароли не совпадают'))
            elif password == '':
                self.stderr.write(
                    self.style.ERROR('Пароль не может быть пустым')
                )
            else:
                break
        User.objects.create_superuser(
            username=username, email=email, password=password
        )
        self.stdout.write(
            self.style.SUCCESS(
                f"Суперпользователь '{username}' успешно создан!"
            )
        )
