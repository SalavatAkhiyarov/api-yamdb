import csv
import os
from datetime import datetime

from django.core.management.base import BaseCommand
from django.conf import settings

from reviews.models import Category, Genre, Title, Review, Comment, MyUser


class Command(BaseCommand):
    help = 'Загружает тестовые данные из csv файлов в бд'

    def handle(self, *args, **options):
        """Метод обработки команды"""
        # Очищаем бд от старых данных
        self.clear_database()
        self.stdout.write(self.style.SUCCESS('Данные очищены'))
        # Для каждой модели указываем
        # какой файл читать
        # как преобразоваять поля из файла
        models_data = {
            MyUser: {
                'filename': 'users.csv',
                'fields': {
                    # преобразуем в число
                    'id': self.convert_int,
                    # преобразуем в строку
                    'username': self.convert_str,
                    'email': self.convert_str,
                    'role': self.convert_str,
                    # пустые значения - None
                    'bio': self.convert_optional_str,
                    'first_name': self.convert_optional_str,
                    'last_name': self.convert_optional_str
                }
            },
            Category: {
                'filename': 'category.csv',
                'fields': {
                    'id': self.convert_int,
                    'name': self.convert_str,
                    'slug': self.convert_str
                }
            },
            Genre: {
                'filename': 'genre.csv',
                'fields': {
                    'id': self.convert_int,
                    'name': self.convert_str,
                    'slug': self.convert_str
                }
            },
            Title: {
                'filename': 'titles.csv',
                'fields': {
                    'id': self.convert_int,
                    'name': self.convert_str,
                    'year': self.convert_int,
                    # Для категорий находим объект по ИД
                    'category': self.get_category
                }
            },
            # Связи между произведениями и жарнрами
            'genre_title': {
                'filename': 'genre_title.csv',
                'fields': {
                    'id': self.convert_int,
                    'title_id': self.convert_int,
                    'genre_id': self.convert_int
                }
            },
            Review: {
                'filename': 'review.csv',
                'fields': {
                    'id': self.convert_int,
                    'title_id': self.convert_int,
                    'text': self.convert_str,
                    'author': self.get_user,
                    'score': self.convert_int,
                    'pub_date': self.convert_datetime
                }
            },
            Comment: {
                'filename': 'comments.csv',
                'fields': {
                    'id': self.convert_int,
                    'review_id': self.convert_int,
                    'text': self.convert_str,
                    'author': self.get_user,
                    'pub_date': self.convert_datetime
                }
            }
        }
        # Обрабатываем модели по череди
        for model, data in models_data.items():
            # путь к файлу
            filepath = os.path.join(
                settings.BASE_DIR,
                'static', 'data',
                data['filename']
            )
            # Проверяем найден ли файл
            if not os.path.exists(filepath):
                self.stdout.write(
                    self.style.ERROR(f'Файл не найден: {data["filename"]}')
                )
                return
            self.stdout.write(f'Загрузка файла: {data["filename"]}')
            try:
                # Тут для связи жанр-произведение особая обработка
                if model == 'genre_title':
                    self.process_genre_title(filepath)
                # Для обычных моделей
                else:
                    self.process_model_file(model, filepath, data['fields'])
                self.stdout.write(self.style.SUCCESS(
                    f'Успешно загружен: {data["filename"]}')
                )
                # Если возникла ошибка показываем и останавливаекм
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Ошибка: {data["filename"]} - {str(e)}')
                )
                return

        self.stdout.write(self.style.SUCCESS('Все данные успешно загружены'))

    # Методы преобразования данных
    def convert_int(self, value):
        """ Преобразуем в число"""
        return int(value)

    def convert_str(self, value):
        """Преобразуем в строку"""
        return str(value)

    def convert_optional_str(self, value):
        """" Поле необязательное - превращаем пустую строку в None"""
        return value if value else None

    def convert_datetime(self, value):
        """ Преобразуем дату в объект datetime"""
        return datetime.strptime(value, '%Y-%m-%dT%H:%M:%S.%fZ')

    def get_category(self, category_id):
        """ Находит объект категории по его ИД"""
        return Category.objects.get(id=int(category_id))

    def get_user(self, user_id):
        """Находит объект пользователя по его ИД"""
        return MyUser.objects.get(id=int(user_id))

    def clear_database(self):
        """Очистка данных в правильном порядке"""
        # Сначала удаляем комментарии (они зависят от отзывов)
        Comment.objects.all().delete()
        # Затем удаляем отзывы (они зависят от произведений)
        Review.objects.all().delete()
        # Удаляем связь между произведениями и жанрами
        Title.genre.through.objects.all().delete()
        Title.objects.all().delete()
        Genre.objects.all().delete()
        Category.objects.all().delete()
        MyUser.objects.all().delete()

    def process_model_file(self, model, filepath, fields_mapping):
        """
        Обрабатывает CSV файл и создает объекты модели,
        преобразует данные и сохраняет в базу
        """
        # Список для хранения объектов перед сохранением
        objects_to_create = []
        # Открываем CSV файл
        with open(filepath, encoding='utf-8') as f:
            # Читаем как словарь
            reader = csv.DictReader(f)
            # Перебираем каждую строку в файле
            for row in reader:
                # Создаём словарь для данных
                model_data = {}
                # Для каждого поля, которое нужно обработать
                for field, converter in fields_mapping.items():
                    try:
                        # Преобразуем значение с помощью функции
                        model_data[field] = converter(row[field])
                    except Exception as e:
                        # Если ошибка - сообщаем в каком поле проблема
                        raise ValueError(
                            f'Ошибка обработки поля {field}: {str(e)}'
                        )
                    # Создаем объект модели
                objects_to_create.append(model(**model_data))
        # Сохраняем все объекты одним запросом        
        model.objects.bulk_create(objects_to_create)

    def process_genre_title(self, filepath):
        """Обрабатывает связи между произведениями и жанрами"""
        with open(filepath, encoding='utf-8') as f:
            reader = csv.DictReader(f)
            # Для каждой строки в файле связей
            for row in reader:
                try:
                    # Находим произведение по ид
                    title = Title.objects.get(id=int(row['title_id']))
                    # Находим жанр по ид
                    genre = Genre.objects.get(id=int(row['genre_id']))
                    # Добавляем жанр к произведению (создаем связь)
                    title.genre.add(genre)
                except Exception as e:
                    raise ValueError(f'Ошибка создания связи: {str(e)}')
