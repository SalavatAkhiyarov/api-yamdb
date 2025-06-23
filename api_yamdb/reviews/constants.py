USER = 'user'
MODERATOR = 'moderator'
ADMIN = 'admin'
ROLE_CHOICES = (
    (USER, 'Аутентифицированный пользователь'),
    (MODERATOR, 'Модератор'),
    (ADMIN, 'Администратор')
)
MAX_NAME_FIELD_LENGTH = 150
MAX_LENGTH_EMAIL = 254
MAX_ROLE_LENGTH = max(len(role[0]) for role in ROLE_CHOICES)
STR_LIMIT = 20
