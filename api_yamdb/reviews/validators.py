from datetime import datetime
import re

from django.core.exceptions import ValidationError


def validate_year_not_in_future(value):
    if value > datetime.now().year:
        raise ValidationError('Год выпуска не может быть в будущем')


def validate_username(value):
    if value.lower() == 'me':
        raise ValidationError('Username "me" запрещен')
    invalid_characters = re.sub(r'[\w.@+-]', '', value)
    if invalid_characters:
        unique_characters = ''.join(sorted(set(invalid_characters)))
        raise ValidationError(
            f'Username содержит недопустимые символы: {unique_characters}. '
            'Допустимые символы: буквы, цифры и символы @/./+/-/_'
        )
    return value
