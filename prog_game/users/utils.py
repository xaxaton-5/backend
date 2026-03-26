import jwt
import logging


from django.contrib.auth.models import User
from django.conf import settings

from rest_framework import exceptions


AUTHENTICATION_HEADER_PREFIX = 'Bearer'
logger = logging.getLogger('core')


def get_user_by_token(auth_header_value: str) -> 'User|None':
    token = auth_header_value.split()
    if len(token) != 2:
        return None

    prefix, value = token
    if prefix != AUTHENTICATION_HEADER_PREFIX:
        return None

    try:
        payload = jwt.decode(
            value, settings.SECRET_KEY, algorithms=['HS256']
        )
    except Exception:
        raise exceptions.AuthenticationFailed('Ошибка аутентификации. Невозможно декодировать токен.')

    try:
        user = User.objects.get(id=payload['id'])
    except User.DoesNotExist:
        raise exceptions.AuthenticationFailed('Пользователь не найден.')

    if not user.is_active:
        logger.warning(f'user is not active {user.id}')
        raise exceptions.AuthenticationFailed('Пользователь неактивен.')

    return (user, token)


def generate_token(user_id: int):
    token = jwt.encode({'id': user_id}, settings.SECRET_KEY, algorithm='HS256')
    return token