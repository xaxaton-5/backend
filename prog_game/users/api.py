from django.contrib.auth.models import User
from django.db import transaction

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser

from users.decorators import with_authorization
from users.serializers import (
    UserSerializer, UserDetailSerializer,
    RegistrationSerializer, LoginSerializer,
    ProfileSerializer, ChildProfileSerializer,
    LinkChildSerializer, AddChildSerializer,
    UserUpdateSerializer, UserAdminUpdateSerializer
)
from users.utils import generate_token
from users.models import Profile


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


"""
@api {POST} /api/register/ Registration
@apiGroup User
@apiDescription Регистрация нового пользователя
@apiBody {String} login Логин пользователя
@apiBody {String} password Пароль
@apiBody {String} password_confirm Подтверждение пароля
@apiBody {String} email Электронная почта
@apiBody {String} [first_name] Имя
@apiBody {String} [last_name] Фамилия
@apiBody {Boolean} [is_parent] Является ли родителем (по умолчанию false)
@apiBody {Number} [parent_id] ID родителя (если регистрируется ребенок)

@apiSuccessExample Успешная регистрация:
    HTTP/1.1 201 Created
    {
        "id": 5,
        "username": "newuser",
        "email": "newuser@example.com",
        "profile": {
            "exp": 0,
            "is_parent": false,
            "parent": null,
            "children": []
        }
    }
"""
class Registration(APIView):
    serializer_class = RegistrationSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        with transaction.atomic():
            user = serializer.save()
            token = generate_token(user.id)
            return Response({
                'token': token,
                'user': UserSerializer(user).data,
                'profile': ProfileSerializer(user.profile).data
            }, status=status.HTTP_201_CREATED)


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


"""
@api {PUT} /api/user/update/:id/ UserUpdate
@apiGroup User
@apiDescription Обновление профиля пользователя (только свои данные)
@apiParam {Number} id Идентификатор пользователя
@apiBody {String} [email] Электронная почта
@apiBody {String} [first_name] Имя
@apiBody {String} [last_name] Фамилия

@apiSuccessExample Успешное обновление:
    HTTP/1.1 200 OK
    {
        "id": 1,
        "email": "newemail@example.com",
        "first_name": "New",
        "last_name": "Name"
    }
"""
class UserUpdate(APIView):
    @with_authorization
    def put(self, request, user_id: int):
        if request.user.id != user_id:
            return Response({'error': 'You can only update your own profile'}, 
                          status=status.HTTP_403_FORBIDDEN)
        
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({'id': -1}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = UserUpdateSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(UserDetailSerializer(user).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


"""
@api {DELETE} /api/user/delete/:id/ UserDelete
@apiGroup User
@apiDescription Удаление пользователя (только свои данные или администратор)
@apiParam {Number} id Идентификатор пользователя

@apiSuccessExample Успешное удаление:
    HTTP/1.1 200 OK
    {
        "message": "User deleted successfully"
    }
"""
class UserDelete(APIView):
    @with_authorization
    def delete(self, request, user_id: int):
        if request.user.id != user_id and not request.user.is_staff:
            return Response({'error': 'Permission denied'}, 
                          status=status.HTTP_403_FORBIDDEN)
        
        try:
            user = User.objects.get(id=user_id)
            user.delete()
            return Response({'message': 'User deleted successfully'}, 
                          status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'id': -1}, status=status.HTTP_404_NOT_FOUND)


"""
@api {GET} /api/user/children/ ChildrenList
@apiGroup User
@apiDescription Получить список детей текущего пользователя
@apiHeader {String} Authorization Bearer токен

@apiSuccessExample Список детей:
    HTTP/1.1 200 OK
    [
        {
            "user_id": 3,
            "username": "child1",
            "email": "child1@example.com",
            "exp": 150,
            "created_at": "2024-01-15T10:30:00Z"
        }
    ]
"""
class ChildrenList(APIView):
    @with_authorization
    def get(self, request):
        profile = request.user.profile
        
        if not profile.is_parent:
            return Response({'error': 'User is not a parent'}, 
                          status=status.HTTP_403_FORBIDDEN)
        
        children = profile.children.all()
        serializer = ChildProfileSerializer(children, many=True)
        return Response(serializer.data)


"""
@api {GET} /api/user/children/:user_id/ UserChildrenList
@apiGroup User
@apiDescription Получить список детей конкретного пользователя
@apiParam {Number} user_id ID пользователя
@apiHeader {String} Authorization Bearer токен

@apiSuccessExample Список детей:
    HTTP/1.1 200 OK
    [
        {
            "user_id": 3,
            "username": "child1",
            "email": "child1@example.com",
            "exp": 150,
            "created_at": "2024-01-15T10:30:00Z"
        }
    ]
"""
class UserChildrenList(APIView):
    @with_authorization
    def get(self, request, user_id: int):
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({'id': -1}, status=status.HTTP_404_NOT_FOUND)
        
        if request.user.id != user_id and not request.user.is_staff:
            return Response({'error': 'Permission denied'}, 
                          status=status.HTTP_403_FORBIDDEN)
        
        if not user.profile.is_parent:
            return Response({'error': 'User is not a parent'}, 
                          status=status.HTTP_403_FORBIDDEN)
        
        children = user.profile.children.all()
        serializer = ChildProfileSerializer(children, many=True)
        return Response(serializer.data)


"""
@api {GET} /api/user/parent/ UserParent
@apiGroup User
@apiDescription Получить родителя текущего пользователя
@apiHeader {String} Authorization Bearer токен

@apiSuccessExample Информация о родителе:
    HTTP/1.1 200 OK
    {
        "id": 2,
        "username": "parent_user",
        "email": "parent@example.com",
        "exp": 500,
        "is_parent": true,
        "parent": null,
        "children": [...]
    }
"""
class UserParent(APIView):
    @with_authorization
    def get(self, request):
        profile = request.user.profile
        
        if not profile.parent:
            return Response({'error': 'User has no parent'}, 
                          status=status.HTTP_404_NOT_FOUND)
        
        serializer = ProfileSerializer(profile.parent)
        return Response(serializer.data)


"""
@api {GET} /api/user/parent/:user_id/ UserParentDetail
@apiGroup User
@apiDescription Получить родителя конкретного пользователя
@apiParam {Number} user_id ID пользователя
@apiHeader {String} Authorization Bearer токен

@apiSuccessExample Информация о родителе:
    HTTP/1.1 200 OK
    {
        "id": 2,
        "username": "parent_user",
        "email": "parent@example.com",
        "exp": 500,
        "is_parent": true,
        "parent": null,
        "children": [...]
    }
"""
class UserParentDetail(APIView):
    @with_authorization
    def get(self, request, user_id: int):
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({'id': -1}, status=status.HTTP_404_NOT_FOUND)
        
        if request.user.id != user_id and not request.user.is_staff:
            return Response({'error': 'Permission denied'}, 
                          status=status.HTTP_403_FORBIDDEN)
        
        if not user.profile.parent:
            return Response({'error': 'User has no parent'}, 
                          status=status.HTTP_404_NOT_FOUND)
        
        serializer = ProfileSerializer(user.profile.parent)
        return Response(serializer.data)


"""
@api {POST} /api/user/add-child/ AddChild
@apiGroup User
@apiDescription Создать нового ребенка и привязать к текущему пользователю
@apiHeader {String} Authorization Bearer токен
@apiBody {String} username Логин ребенка
@apiBody {String} email Электронная почта
@apiBody {String} password Пароль
@apiBody {String} password_confirm Подтверждение пароля
@apiBody {String} [first_name] Имя
@apiBody {String} [last_name] Фамилия

@apiSuccessExample Ребенок создан:
    HTTP/1.1 201 Created
    {
        "child": {
            "user_id": 3,
            "username": "newchild",
            "email": "newchild@example.com",
            "exp": 0,
            "created_at": "2024-01-15T10:30:00Z"
        },
        "message": "Child created and linked successfully"
    }
"""
class AddChild(APIView):
    @with_authorization
    def post(self, request):
        profile = request.user.profile
        
        if not profile.is_parent:
            return Response({'error': 'Only parents can add children'}, 
                          status=status.HTTP_403_FORBIDDEN)
        
        serializer = AddChildSerializer(data=request.data)
        if serializer.is_valid():
            with transaction.atomic():
                child_user = User.objects.create_user(
                    username=serializer.validated_data['username'],
                    email=serializer.validated_data['email'],
                    password=serializer.validated_data['password'],
                    first_name=serializer.validated_data.get('first_name', ''),
                    last_name=serializer.validated_data.get('last_name', '')
                )
                
                child_user.profile.parent = profile
                child_user.profile.is_parent = False
                child_user.profile.save()
                
                response_data = {
                    'child': ChildProfileSerializer(child_user.profile).data,
                    'message': 'Child created and linked successfully'
                }
                return Response(response_data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


"""
@api {POST} /api/user/link-child/ LinkChild
@apiGroup User
@apiDescription Привязать существующего ребенка к текущему пользователю
@apiHeader {String} Authorization Bearer токен
@apiBody {Number} child_id ID ребенка для привязки

@apiSuccessExample Ребенок привязан:
    HTTP/1.1 200 OK
    {
        "child": {
            "user_id": 3,
            "username": "child1",
            "email": "child1@example.com",
            "exp": 150,
            "created_at": "2024-01-15T10:30:00Z"
        },
        "message": "Child linked successfully"
    }
"""
class LinkChild(APIView):
    @with_authorization
    def post(self, request):
        profile = request.user.profile
        
        if not profile.is_parent:
            return Response({'error': 'Only parents can link children'}, 
                          status=status.HTTP_403_FORBIDDEN)
        
        serializer = LinkChildSerializer(data=request.data)
        if serializer.is_valid():
            child_id = serializer.validated_data['child_id']
            child_profile = Profile.objects.get(user__id=child_id)
            
            if child_profile.parent:
                return Response({'error': 'Child already has a parent'}, 
                              status=status.HTTP_400_BAD_REQUEST)
            
            child_profile.parent = profile
            child_profile.save()
            
            return Response({
                'child': ChildProfileSerializer(child_profile).data,
                'message': 'Child linked successfully'
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


"""
@api {DELETE} /api/user/remove-child/:child_id/ RemoveChild
@apiGroup User
@apiDescription Отвязать ребенка от текущего пользователя
@apiParam {Number} child_id ID ребенка
@apiHeader {String} Authorization Bearer токен

@apiSuccessExample Ребенок отвязан:
    HTTP/1.1 200 OK
    {
        "message": "Child unlinked successfully",
        "child_id": 3
    }
"""
class RemoveChild(APIView):
    @with_authorization
    def delete(self, request, child_id: int):
        profile = request.user.profile
        
        if not profile.is_parent:
            return Response({'error': 'Only parents can remove children'}, 
                          status=status.HTTP_403_FORBIDDEN)
        
        try:
            child_profile = Profile.objects.get(user__id=child_id, parent=profile)
            child_profile.parent = None
            child_profile.save()
            
            return Response({
                'message': 'Child unlinked successfully',
                'child_id': child_id
            }, status=status.HTTP_200_OK)
        except Profile.DoesNotExist:
            return Response({'error': 'Child not found or not linked to this parent'}, 
                          status=status.HTTP_404_NOT_FOUND)


"""
@api {POST} /api/admin/users/create/ UserCreate
@apiGroup Admin
@apiDescription Создание пользователя (административный)
@apiHeader {String} Authorization Bearer токен (требуются права администратора)
@apiBody {String} username Логин
@apiBody {String} password Пароль
@apiBody {String} email Электронная почта
@apiBody {String} [first_name] Имя
@apiBody {String} [last_name] Фамилия
@apiBody {Number} [exp] Опыт (по умолчанию 0)
@apiBody {Boolean} [is_parent] Является родителем
@apiBody {Number} [parent_id] ID родителя

@apiSuccessExample Пользователь создан:
    HTTP/1.1 201 Created
    {
        "id": 5,
        "username": "newuser",
        "email": "newuser@example.com"
    }
"""
class UserCreate(APIView):
    @with_authorization
    def post(self, request):
        if not request.user.is_staff:
            return Response({'error': 'Admin access required'}, 
                          status=status.HTTP_403_FORBIDDEN)
        
        serializer = UserAdminUpdateSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(UserDetailSerializer(user).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


"""
@api {PUT} /api/admin/users/update/:user_id/ UserAdminUpdate
@apiGroup Admin
@apiDescription Обновление пользователя (административный)
@apiParam {Number} user_id ID пользователя
@apiHeader {String} Authorization Bearer токен (требуются права администратора)
@apiBody {String} [email] Электронная почта
@apiBody {String} [first_name] Имя
@apiBody {String} [last_name] Фамилия
@apiBody {Number} [exp] Опыт
@apiBody {Boolean} [is_parent] Является родителем
@apiBody {Number} [parent_id] ID родителя

@apiSuccessExample Пользователь обновлен:
    HTTP/1.1 200 OK
    {
        "id": 5,
        "username": "updateduser",
        "email": "updated@example.com"
    }
"""
class UserAdminUpdate(APIView):
    @with_authorization
    def put(self, request, user_id: int):
        if not request.user.is_staff:
            return Response({'error': 'Admin access required'}, 
                          status=status.HTTP_403_FORBIDDEN)
        
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({'id': -1}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = UserAdminUpdateSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(UserDetailSerializer(user).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)