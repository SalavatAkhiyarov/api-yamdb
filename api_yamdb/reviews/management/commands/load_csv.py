import os
import csv
import datetime

from django.core.management.base import BaseCommand
from django.conf import settings

from reviews.models import User, Category, Genre, Title, Review, Comment


class Command(BaseCommand):
    help = 'Загружает данные из CSV файлов в бд'

    def handle(self, *args, **kwargs):
        # Путь к папке с данными
        data_path = os.path.join(settings.BASE_DIR, 'static/data')
        # Создаем словарь с моделями и именами файлов
        models_files = {
            User: 'users.csv',
            Category: 'category.csv',
            Genre: 'genre.csv',
            Title: 'titles.csv',
            Review: 'review.csv',
            Comment: 'comments.csv',
        }

        # Проходим циклом по словарю
        for model, filename in models_files.items():
            # Полный путь к файлу
            file_path = os.path.join(data_path, filename)
            # Открываем файл
            with open(file_path, encoding='utf-8') as f:
                # Создаем список объектов для создания
                objects = []
                # читаем как словарь
                reader = csv.DictReader(f)
                # Проходим циклом по строкам файла
                for row in reader:
                    # Создаем словарь с полями
                    fields = {}
                    # Проходим по словарю из строки CSV
                    for key, value in row.items():
                        # Проверяем специальные поля
                        if key == 'pub_date':
                            # Преобразование даты
                            fields[key] = datetime.datetime.strptime(
                                value, '%Y-%m-%dT%H:%M:%S.%fZ'
                            )
                        elif key in ['id', 'year', 'score']:
                            # Числовые поля
                            fields[key] = int(value)
                        elif key == 'category' and model == Title:
                            # Обработка категории (FK)
                            fields['category_id'] = int(value)
                        elif key == 'title_id' and model == Review:
                            # Обработка связи для Review
                            fields['title_id'] = int(value)
                        elif key == 'author' and model in (Review, Comment):
                            # Обработка автора
                            fields['author_id'] = int(value)
                        elif key == 'review_id' and model == Comment:
                            # Обработка связи для Comment
                            fields['review_id'] = int(value)
                        else:
                            # Для остальных полей - значение как есть
                            fields[key] = value
                    # Добавляем объект в список
                    objects.append(model(**fields))
            # Используем bulk_create для создания объектов
            model.objects.bulk_create(objects)
        # Связи м2м
        # берём отдельный файл genre_title.csv
        # где у нас связь жанров и произведений
        m2m_file = os.path.join(data_path, 'genre_title.csv')
        # Так же открываем и читаем как словарь
        with open(m2m_file, encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Получаем ИД произведения и жанра
                title_id = int(row['title_id'])
                genre_id = int(row['genre_id'])
                # Находим соответствующие объекты в бд
                title = Title.objects.get(id=title_id)
                genre = Genre.objects.get(id=genre_id)
                # Добавляем жанр к произведению,
                # это создаст связь в промежуточной таблице
                title.genre.add(genre)
        self.stdout.write(self.style.SUCCESS('Все данные успешно загружены!'))
