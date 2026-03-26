from django.contrib.auth.models import User

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from users.decorators import with_authorization
from users.serializers import (
    UserSerializer, UserDetailSerializer,
    RegistrationSerializer, LoginSerializer
)
from users.utils import generate_token


"""
@api {GET} /api/users/list/ UserList
@apiName SecretsAPI
@apiGroup User
@apiSuccess (Ответ) {Object[]} users Список активных пользователей.
@apiSuccess (Ответ) {Number} users.id Идентификатор пользователя (-1 если не найден).
@apiSuccess (Ответ) {String} users.email Электронная почта пользователя.
@apiSuccess (Ответ) {Date} users.date_joined Дата регистрации аккаунта.
@apiSuccess (Ответ) {Boolean} users.is_superuser Статус администратора.

@apiSuccessExample Список пользователей (может быть пуст):
    HTTP/1.1 200 OK
    [
        {
            "id": 1,
            "email": "red_hot_osu_pepper@mail.ru",
            "date_joined": "2025-02-15T12:35:39.850569Z",
            "is_superuser": true
        }
    ]
"""
class UserList(APIView):
    def get(self, request):
        users = [
            UserSerializer(user).data
            for user in User.objects.filter(is_active=True)
        ]
        return Response(users)


"""
@api {GET} /api/users/detail/:id/ UserDetail
@apiGroup User

@apiParam {Number} id Идентификатор пользователя.

@apiSuccess (Ответ) {Number} id Идентификатор пользователя.
@apiSuccess (Ответ) {String} email Электронная почта пользователя.
@apiSuccess (Ответ) {Date} date_joined Дата регистрации аккаунта.
@apiSuccess (Ответ) {Boolean} is_superuser Статус администратора.
@apiSuccess (Ответ) {Boolean} is_active Статус активности.

@apiSuccessExample Пользователь существует:
    HTTP/1.1 200 OK
    {
        "id": 1,
        "email": "red_hot_osu_pepper@mail.ru",
        "date_joined": "2025-02-15T12:35:39.850569Z",
        "is_superuser": true,
        "is_active": true
    }

@apiErrorExample {json} Пользователя с указанным ид не существует:
    HTTP/1.1 404 Not Found
    {
        "id": -1
    }
"""
class UserDetail(APIView):
    def get(self, request, user_id: int):
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({'id': -1}, status=status.HTTP_404_NOT_FOUND)
        return Response(UserDetailSerializer(user).data)


class Registration(APIView):
    serializer_class = RegistrationSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


"""
@api {POST} /api/login/ Login
@apiGroup User
@apiBody {String} email Электронная почта пользователя.
@apiBody {String} password Пароль.

@apiSuccess (Ответ) {String} token Bearer-токен для headers.
@apiSuccess (Ответ) {Object} user Объект пользователя.
@apiSuccess (Ответ) {Number} user.id Идентификатор пользователя.
@apiSuccess (Ответ) {String} user.email Электронная почта пользователя.
@apiSuccess (Ответ) {Boolean} user.is_superuser Статус администратора.

@apiSuccessExample Успешный вход в аккаунт:
    HTTP/1.1 200 OK
    {
        "token": "eyJhbGciOiJIUzI1NisIInr5cCI6IkpXVCJ9.eYjcSZCI6Nn0.uCO9ujoT4xLkeE9S3yG_b-k0lSNERADmGqh8YRozqYE",
        "user": {
            "id": 1,
            "email": "red_hot_osu_pepper@mail.ru",
            "is_superuser": true
        }
    }

@apiErrorExample {json} Пропущено поле:
    HTTP/1.1 404 Not Found
    {
        "password": [
            "Обязательное поле."
        ]
    }

@apiErrorExample {json} Некорректно указана почта:
    HTTP/1.1 404 Not Found
    {
        "email": [
            "Введите правильный адрес электронной почты."
        ]
    }
"""
class Login(APIView):
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            user = User.objects.get(email=serializer.initial_data.get('email'), is_active=True)
            if not user.check_password(serializer.initial_data.get('password')):
                raise User.DoesNotExist
        except User.DoesNotExist:
            return Response({'user': -1}, status=status.HTTP_404_NOT_FOUND)
        token = generate_token(user.id)
        return Response({'token': token, 'user': LoginSerializer(user).data})


"""
@api {GET} /api/auth/ CheckToken
@apiGroup User
@apiDescription Токен берется из headers по ключу Authorized. Формат: Bearer TokenHere

@apiSuccess (Ответ) {Number} id Идентификатор пользователя (-1 при некорректном токене).
@apiSuccess (Ответ) {String} email Электронная почта пользователя.
@apiSuccess (Ответ) {Boolean} is_superuser Статус администратора.

@apiSuccessExample Аккаунт успешно зарегистрирован:
    HTTP/1.1 200 OK
    {
        "id": 1,
        "email": "red_hot_osu_pepper@mail.ru",
        "is_superuser": false
    }

@apiErrorExample {json} Токен не передан либо не соответствует активному пользователю:
    HTTP/1.1 401 Unauthorized
    {
        "id": -1
    }
"""
class CheckToken(APIView):
    serializer_class = LoginSerializer

    @with_authorization
    def get(self, request):
        if not request.user or not request.user.is_active:
            return Response({'id': -1}, status=status.HTTP_401_UNAUTHORIZED)
        return Response(self.serializer_class(request.user).data)