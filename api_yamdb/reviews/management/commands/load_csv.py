import os
import csv
import datetime

from django.core.management.base import BaseCommand
from django.conf import settings

from reviews.models import (
    User, Category, Genre, Title, Review, Comment, TitleGenre
)


class Command(BaseCommand):
    help = 'Загружает данные из CSV файлов в БД'

    def handle(self, *args, **kwargs):
        data_path = os.path.join(settings.BASE_DIR, 'static/data')
        models_files = {
            User: 'users.csv',
            Category: 'category.csv',
            Genre: 'genre.csv',
            Title: 'titles.csv',
            Review: 'review.csv',
            Comment: 'comments.csv',
            TitleGenre: 'genre_title.csv',
        }
        foreign_keys = {
            'category': (Category, 'category'),
            'title_id': (Title, 'title'),
            'author': (User, 'author'),
            'review_id': (Review, 'review'),
        }
        for model, filename in models_files.items():
            file_path = os.path.join(data_path, filename)
            with open(file_path, encoding='utf-8') as f:
                reader = csv.DictReader(f)
                objects = []
                if model == TitleGenre:
                    for row in reader:
                        title_id = int(row['title_id'])
                        genre_id = int(row['genre_id'])
                        TitleGenre.objects.get_or_create(
                            title_id=title_id, genre_id=genre_id
                        )
                    continue
                for row in reader:
                    fields = {}
                    for key, value in row.items():
                        if key == 'pub_date':
                            fields[key] = datetime.datetime.strptime(
                                value, '%Y-%m-%dT%H:%M:%S.%fZ'
                            )
                        elif key in ['id', 'year', 'score']:
                            fields[key] = int(value)
                        elif key in foreign_keys:
                            model_class, field_name = foreign_keys[key]
                            fields[field_name] = model_class.objects.get(
                                id=int(value)
                            )
                        else:
                            fields[key] = value
                    objects.append(model(**fields))
                model.objects.bulk_create(objects)
        self.stdout.write(self.style.SUCCESS('Данные успешно загружены!'))
