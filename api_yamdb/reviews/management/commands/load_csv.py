import csv
import os
from datetime import datetime

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from reviews.models import Category, Genre, Title, Review, Comment, MyUser


class Command(BaseCommand):
    help = 'Загружает тестовые данные из csv файлов в бд'

    def add_arguments(self, parser):
        # Добавляем аргумент --clear очистим данные
        # перед каждым повторным заупском
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Очистить все перед загрузкой'
        )

    def handle(self, *args, **options):
        # Если укажем --clear, очистим данные
        if options['clear']:
            self.clear_database()
            self.stdout.write(self.style.SUCCESS('Данные очищены'))
        # Указываем путь к папке с данными
        data_folder = os.path.join(settings.BASE_DIR, 'static', 'data')
        # Даём порядок загрузки файлов
        # (важно т.к они зависят друг от друга, т.е. комменты без пользователя загружать нельзя)
        load_order = [
            ('users.csv', self.load_users),
            ('category.csv', self.load_categories),
            ('genre.csv', self.load_genres),
            ('titles.csv', self.load_titles),
            ('genre_title.csv', self.load_genre_title),
            ('review.csv', self.load_reviews),
            ('comments.csv', self.load_comments),
        ]
        # загружаем каждый файл по очереди
        for filename, loader in load_order:
            filepath = os.path.join(data_folder, filename)
            # Проверяем существование файла,
            # если его нет - останавливаем процесс
            if not os.path.exists(filepath):
                self.stdout.write(
                    self.style.ERROR(f'Файл не найден: {filename}')
                )
                return  # Останавливаем выполнение
            # Показываем какой файл загружается
            self.stdout.write(f'Загрузка файла: {filename}')
            try:
                # Вызываем метод загрузки
                loader(filepath)
                self.stdout.write(
                    self.style.SUCCESS(f'Успешно загружен: {filename}')
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Ошибка: {filename} - {str(e)}')
                )
                return  # Останавлием при ошибке
        # После цикла сообщаем что всё успешно загружено
        self.stdout.write(
            self.style.SUCCESS('Все данные успешно загружены')
        )

    # Метод очистки бд(Тот самый флажок --clear)
    def clear_database(self):
        """Очистка данных"""
        # Важно соблюдать порядок из-за связей между моделями
        Comment.objects.all().delete()
        Review.objects.all().delete()
        Title.genre.through.objects.all().delete()
        Title.objects.all().delete()
        Genre.objects.all().delete()
        Category.objects.all().delete()
        MyUser.objects.all().delete()

    # Методы загрузки данных
    def load_users(self, filepath):
        """ Загружает пользователей
        Формат файла: id,username,email,role,bio,first_name,last_name
        (формат соответсвует полям моделей,
        либо уже указаны в самих файлах csv)
        """
        # Открываем файл
        with open(filepath, encoding='utf-8') as f:
            reader = csv.DictReader(f)  # Читаем файл как словарь
            # Создаём пользователя сохраняя ИД
            for row in reader:
                # Используем update_or_creat для защиты от дублирования
                # Чтобы каждый раз не очищать БД
                MyUser.objects.update_or_create(
                    id=row['id'],
                    defaults={
                        'username': row['username'],
                        'email': row['email'],
                        'role': row['role'],
                        # Где возможны пустые строки ставим None
                        'bio': row['bio'] or None,
                        'first_name': row['first_name'] or None,
                        'last_name': row['last_name'] or None
                    }
                )

    def load_categories(self, filepath):
        """
        Загружает категории
        """
        with open(filepath, encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                Category.objects.update_or_create(
                    id=row['id'],
                    defaults={
                        'name': row['name'],
                        'slug': row['slug']
                    }
                )

    def load_genres(self, filepath):
        """
        Загружает жанры
        """
        with open(filepath, encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                Genre.objects.update_or_create(
                    id=row['id'],
                    defaults={
                        'name': row['name'],
                        'slug': row['slug']
                    }
                )

    # Важно чтобы категории были загружены ранее
    def load_titles(self, filepath):
        """
        Загружает произведения
        """
        with open(filepath, encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Преобразуем год в число
                year = int(row['year'])
                # Находим категорию по ид. Она уже должна существовать
                category = Category.objects.get(id=row['category'])
                Title.objects.update_or_create(
                    id=row['id'],
                    defaults={
                        'name': row['name'],
                        'year': year,
                        'category': category,
                    }
                )

    # Опять же важно чтобы произведения и жанры были загружены раньше
    def load_genre_title(self, filepath):
        """
        Создает связи между произведениями и жанрами
        """
        with open(filepath, encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Находим произведение и жанр по ИД
                title = Title.objects.get(id=row['title_id'])
                genre = Genre.objects.get(id=row['genre_id'])
                # Добавляем связь мэни ту мэни,
                # т.е. добавляем жанр к произведению
                title.genre.add(genre)

    def load_reviews(self, filepath):
        """
        Загружает отзывы
        """
        with open(filepath, encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Преобразуем строку даты в datetime
                pub_date = datetime.strptime(
                    row['pub_date'],
                    '%Y-%m-%dT%H:%M:%S.%fZ'
                )
                score = int(row['score'])
                Review.objects.update_or_create(
                    id=row['id'],
                    defaults={
                        'title_id': row['title_id'],
                        'text': row['text'],
                        'author_id': row['author'],
                        'score': score,
                        'pub_date': pub_date
                    }
                )

    def load_comments(self, filepath):
        """
        Загружает комментарии
        """
        with open(filepath, encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                pub_date = datetime.strptime(
                    row['pub_date'], 
                    '%Y-%m-%dT%H:%M:%S.%fZ'
                )
                Comment.objects.update_or_create(
                    id=row['id'],
                    defaults={
                        'review_id': row['review_id'],
                        'text': row['text'],
                        'author_id': row['author'],
                        'pub_date': pub_date
                    }
                )
# Команда для запуска python manage.py load_csv
