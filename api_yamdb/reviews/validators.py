from django.core.exceptions import ValidationError

from datetime import datetime


def validate_year_not_in_future(value):
    if value > datetime.now().year:
        raise ValidationError('Год выпуска не может быть в будущем')
