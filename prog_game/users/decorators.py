from functools import wraps
from django.contrib.auth.models import User
from rest_framework.response import Response

from users import utils as user_utils


def with_authorization(method):
    """Декоратор для проверки авторизации"""
    @wraps(method)
    def inner(instance, request, *args, **kwargs):
        request = process_request(request)
        if request.user is None:
            return Response({'error': 'Unauthorized'}, status=403)
        return method(instance, request, *args, **kwargs)
    return inner


def only_admin(method):
    """Декоратор для проверки прав администратора"""
    @wraps(method)
    def inner(instance, request, *args, **kwargs):
        request = process_request(request)
        if request.user is None or not request.user.is_staff:
            return Response({'error': 'Forbidden. Admin rights required.'}, status=403)
        return method(instance, request, *args, **kwargs)
    return inner


def only_parent(method):
    """Декоратор для проверки, что пользователь является родителем"""
    @wraps(method)
    def inner(instance, request, *args, **kwargs):
        request = process_request(request)
        if request.user is None:
            return Response({'error': 'Unauthorized'}, status=403)
        
        # Проверяем наличие профиля и флага is_parent
        if not hasattr(request.user, 'profile') or not request.user.profile.is_parent:
            return Response({'error': 'Forbidden. Parent rights required.'}, status=403)
        
        return method(instance, request, *args, **kwargs)
    return inner


def only_child(method):
    """Декоратор для проверки, что пользователь является ребенком"""
    @wraps(method)
    def inner(instance, request, *args, **kwargs):
        request = process_request(request)
        if request.user is None:
            return Response({'error': 'Unauthorized'}, status=403)
        
        # Проверяем наличие профиля и наличие родителя
        if not hasattr(request.user, 'profile') or request.user.profile.parent is None:
            return Response({'error': 'Forbidden. Child rights required.'}, status=403)
        
        return method(instance, request, *args, **kwargs)
    return inner


def only_own_profile(method):
    """Декоратор для проверки, что пользователь работает со своим профилем"""
    @wraps(method)
    def inner(instance, request, *args, **kwargs):
        request = process_request(request)
        if request.user is None:
            return Response({'error': 'Unauthorized'}, status=403)
        
        # Получаем ID пользователя из kwargs (обычно pk или user_id)
        user_id = kwargs.get('pk') or kwargs.get('user_id')
        
        # Если ID не указан, проверяем, что это текущий пользователь
        if user_id is None:
            return method(instance, request, *args, **kwargs)
        
        # Проверяем, что запрашиваемый пользователь - это текущий пользователь
        if str(request.user.id) != str(user_id):
            return Response({'error': 'Forbidden. You can only access your own profile.'}, status=403)
        
        return method(instance, request, *args, **kwargs)
    return inner


def only_parent_or_self(method):
    """Декоратор для проверки, что пользователь либо родитель ребенка, либо сам ребенок"""
    @wraps(method)
    def inner(instance, request, *args, **kwargs):
        request = process_request(request)
        if request.user is None:
            return Response({'error': 'Unauthorized'}, status=403)
        
        # Получаем ID пользователя из kwargs
        user_id = kwargs.get('pk') or kwargs.get('user_id')
        
        if user_id is None:
            return method(instance, request, *args, **kwargs)
        
        # Проверяем, что это текущий пользователь
        if str(request.user.id) == str(user_id):
            return method(instance, request, *args, **kwargs)
        
        # Проверяем, является ли текущий пользователь родителем запрашиваемого
        if hasattr(request.user, 'profile') and request.user.profile.is_parent:
            try:
                target_user = User.objects.get(id=user_id)
                if target_user.profile.parent == request.user.profile:
                    return method(instance, request, *args, **kwargs)
            except User.DoesNotExist:
                pass
        
        return Response({'error': 'Forbidden. You can only access your own profile or your children.'}, status=403)
    return inner


def process_request(request):
    """Обработка запроса, добавление пользователя"""
    user = check_authorization(request)
    request.user = user
    return request


def check_authorization(request) -> 'User|None':
    """Проверка авторизации по токену"""
    auth_token = request.headers.get('Authorization')
    if auth_token:
        return get_user_by_token(auth_token)
    return None


def get_user_by_token(token: str) -> 'User|None':
    """Получение пользователя по токену"""
    try:
        user, token = user_utils.get_user_by_token(token)
        return user
    except Exception:
        return None
