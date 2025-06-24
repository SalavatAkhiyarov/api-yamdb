import os
import csv
import datetime

from django.core.management.base import BaseCommand
from django.conf import settings

from reviews.models import User, Category, Genre, Title, Review, Comment


# Решил описать вспомогательные функции вне класса Command,
# если всё внести в handle() flake8 будет говорить, что слишком сложный метод
def process_row(model, row):
    """
    Преобразует данные и возвращает поля для модели
    из строк файла CSV
    """
    fields = {}
    # Берём каждое поле и приводим к нужному типу
    for key, value in row.items():
        # Поля с датой
        if key == 'pub_date':
            # строка в объект datetime
            fields[key] = datetime.datetime.strptime(
                value,
                '%Y-%m-%dT%H:%M:%S.%fZ'
            )
        # Для числовых полей
        elif key in ['id', 'year', 'score']:
            # Строку в число
            fields[key] = int(value)
        # внешние ключи FK
        # Для модели Title поле category это category_id
        elif key == 'category' and model == Title:
            # Создаем поле для связи по внешнему ключу
            fields['category_id'] = int(value)
        # Для модели Review поле title это title_id и так далее
        elif key == 'title_id' and model == Review:
            fields['title_id'] = int(value)
        elif key == 'author' and model in (Review, Comment):
            fields['author_id'] = int(value)
        elif key == 'review_id' and model == Comment:
            fields['review_id'] = int(value)
        # Для всех остальных полей
        # оставляем как есть
        else:
            fields[key] = value
        # Возвращаем словарь где ключи - название полей модели
        # Значения - подготовленные данные для создания объекта модели
    return fields


def load_model(model, file_path):
    """Загружает данные из файла в модель"""
    # Открываем файл
    with open(file_path, encoding='utf-8') as f:
        # Читаем как словарь
        # Тут у нас ключи будут названиями колонок,
        # значение - данные ячейки
        reader = csv.DictReader(f)
        # Список для накопления объектов
        objects = []
        # Перебираем строки в файле
        for row in reader:
            fields = process_row(model, row)
            # Создаем объект модели с подготовленными полями
            # и добавляем его в список
            objects.append(model(**fields))
        # Создаём сразу все объекты в бд одним запросом
        model.objects.bulk_create(objects)


def load_m2m(data_path):
    """Загружает связи м2м из файла genre_title.csv"""
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


class Command(BaseCommand):
    help = 'Загружает данные из CSV файлов в бд'

    def handle(self, *args, **kwargs):
        # Путь к папке с файлами
        data_path = os.path.join(settings.BASE_DIR, 'static/data')
        # Создаем словарь моделей и соответствующих файлов,
        # где под ключём передадим модель а под значением имя файла
        # Порядок важен, т.к. модели зависят друг от друга
        models_files = {
            User: 'users.csv',
            Category: 'category.csv',
            Genre: 'genre.csv',
            Title: 'titles.csv',
            Review: 'review.csv',
            Comment: 'comments.csv',
        }
        # Проходим по каждой паре (модель - файл) в словаре
        for model, filename in models_files.items():
            # полный путь к файлу
            file_path = os.path.join(data_path, filename)
            # Загружаем данные
            load_model(model, file_path)
        # Загружаем связи м2м
        load_m2m(data_path)
        self.stdout.write('Все данные успешно загружены!')
