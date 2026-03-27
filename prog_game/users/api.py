from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from users.decorators import with_authorization
from users.serializers import (
    UserSerializer, UserDetailSerializer,
    RegistrationSerializer, LoginSerializer,
    ProfileSerializer, ChildProfileSerializer,
    LinkChildSerializer, AddChildSerializer,
    UserUpdateSerializer, UserAdminUpdateSerializer,
    UserResultSerializer, UserResultCreateSerializer
)
from users.utils import generate_token
from users.models import Profile, UserResult


class UserList(APIView):
    def get(self, request):
        users = User.objects.filter(is_active=True)
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)


class UserDetail(APIView):
    def get(self, request, user_id: int):
        # Если запрашиваем свой профиль - используем request.user
        if request.user.is_authenticated and request.user.id == user_id:
            return Response(UserDetailSerializer(request.user).data)
        
        # Иначе ищем в БД
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
        user = serializer.save()
        token = generate_token(user.id)
        return Response({
            'token': token,
            'user': UserSerializer(user).data,
            'profile': ProfileSerializer(user.profile).data
        }, status=status.HTTP_201_CREATED)


class Login(APIView):
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = serializer.validated_data['user']
        token = generate_token(user.id)
        return Response({'token': token, 'user': UserSerializer(user).data})


class CheckToken(APIView):
    serializer_class = LoginSerializer

    @with_authorization
    def get(self, request):
        if not request.user or not request.user.is_active:
            return Response({'id': -1}, status=status.HTTP_401_UNAUTHORIZED)
        return Response(UserSerializer(request.user).data)


class UserUpdate(APIView):
    @with_authorization
    def put(self, request, user_id: int):
        if request.user.id != user_id:
            return Response({'error': 'You can only update your own profile'}, 
                          status=status.HTTP_403_FORBIDDEN)
        
        serializer = UserUpdateSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(UserDetailSerializer(request.user).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserDeactivate(APIView):
    @with_authorization
    def post(self, request):
        user = request.user
        
        if user.is_superuser or user.is_staff:
            return Response({'error': 'Cannot deactivate admin users via API'}, 
                          status=status.HTTP_403_FORBIDDEN)
        
        user.is_active = False
        user.save()
        
        return Response({
            'message': 'User deactivated successfully',
            'user_id': user.id
        }, status=status.HTTP_200_OK)


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


class UserChildrenList(APIView):
    @with_authorization
    def get(self, request, user_id: int):
        if request.user.id == user_id:
            profile = request.user.profile
        else:
            if not request.user.is_staff:
                return Response({'error': 'Permission denied'}, 
                              status=status.HTTP_403_FORBIDDEN)
            
            try:
                user = User.objects.select_related('profile').get(id=user_id)
                profile = user.profile
            except User.DoesNotExist:
                return Response({'id': -1}, status=status.HTTP_404_NOT_FOUND)
        
        if not profile.is_parent:
            return Response({'error': 'User is not a parent'}, 
                          status=status.HTTP_403_FORBIDDEN)
        
        children = profile.children.all()
        serializer = ChildProfileSerializer(children, many=True)
        return Response(serializer.data)


class UserParent(APIView):
    @with_authorization
    def get(self, request):
        profile = request.user.profile
        
        if not profile.parent:
            return Response({'error': 'User has no parent'}, 
                          status=status.HTTP_404_NOT_FOUND)
        
        serializer = ProfileSerializer(profile.parent)
        return Response(serializer.data)


class UserParentDetail(APIView):
    @with_authorization
    def get(self, request, user_id: int):
        if request.user.id == user_id:
            profile = request.user.profile
        else:
            if not request.user.is_staff:
                return Response({'error': 'Permission denied'}, 
                              status=status.HTTP_403_FORBIDDEN)
            
            try:
                user = User.objects.select_related('profile').get(id=user_id)
                profile = user.profile
            except User.DoesNotExist:
                return Response({'id': -1}, status=status.HTTP_404_NOT_FOUND)
        
        if not profile.parent:
            return Response({'error': 'User has no parent'}, 
                          status=status.HTTP_404_NOT_FOUND)
        
        serializer = ProfileSerializer(profile.parent)
        return Response(serializer.data)


class AddChild(APIView):
    @with_authorization
    def post(self, request):
        profile = request.user.profile
        
        if not profile.is_parent:
            return Response({'error': 'Only parents can add children'}, 
                          status=status.HTTP_403_FORBIDDEN)
        
        serializer = AddChildSerializer(data=request.data)
        if serializer.is_valid():
            child_user = User.objects.create_user(
                username=serializer.validated_data['username'],
                email=serializer.validated_data['email'],
                password=serializer.validated_data['password']
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
            
            try:
                child_profile = Profile.objects.select_related('user').get(user__id=child_id)
            except Profile.DoesNotExist:
                return Response({'error': 'Child profile not found'}, 
                              status=status.HTTP_404_NOT_FOUND)
            
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
"""
@api {POST} /api/user/result/ UserResultCreate
@apiGroup User
@apiDescription Сохранение результата прохождения урока/теста/практики
@apiHeader {String} Authorization Bearer токен
@apiBody {String} result_type Тип результата (test/theory/practice/game)
@apiBody {String} key Ключ результата (например: "variables_lesson_1")
@apiBody {Number} exp_earned Заработанный опыт

@apiSuccessExample Результат сохранен:
    HTTP/1.1 201 Created
    {
        "id": 1,
        "user_id": 1,
        "username": "user1",
        "result_type": "test",
        "key": "variables_lesson_1",
        "exp_earned": 100,
        "created_at": "2024-01-15T10:30:00Z"
    }
"""
class UserResultCreate(APIView):
    @with_authorization
    def post(self, request):
        serializer = UserResultCreateSerializer(
            data=request.data,
            context={'request': request}
        )
        if serializer.is_valid():
            result = serializer.save()
            return Response(
                UserResultSerializer(result).data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


"""
@api {GET} /api/user/results/ UserResultList
@apiGroup User
@apiDescription Получить список результатов текущего пользователя
@apiHeader {String} Authorization Bearer токен
@apiParam {String} [result_type] Фильтр по типу (test/theory/practice/game)
@apiParam {String} [key] Фильтр по ключу
@apiParam {Number} [limit] Лимит записей
@apiParam {Number} [offset] Смещение для пагинации

@apiSuccessExample Список результатов:
    HTTP/1.1 200 OK
    {
        "count": 10,
        "next": null,
        "previous": null,
        "results": [
            {
                "id": 1,
                "user_id": 1,
                "username": "user1",
                "result_type": "test",
                "key": "variables_lesson_1",
                "exp_earned": 100,
                "created_at": "2024-01-15T10:30:00Z"
            }
        ]
    }
"""
class UserResultList(APIView):
    @with_authorization
    def get(self, request):
        user = request.user
        results = UserResult.objects.filter(user=user)
        
        # Фильтр по типу
        result_type = request.query_params.get('result_type')
        if result_type:
            results = results.filter(result_type=result_type)
        
        # Фильтр по ключу
        key = request.query_params.get('key')
        if key:
            results = results.filter(key=key)
        
        # Пагинация
        limit = int(request.query_params.get('limit', 50))
        offset = int(request.query_params.get('offset', 0))
        
        total = results.count()
        results = results[offset:offset + limit]
        
        serializer = UserResultSerializer(results, many=True)
        
        return Response({
            'count': total,
            'next': None,
            'previous': None,
            'results': serializer.data
        })


"""
@api {GET} /api/user/result/{result_id}/ UserResultDetail
@apiGroup User
@apiDescription Получить детальную информацию о результате
@apiParam {Number} result_id ID результата
@apiHeader {String} Authorization Bearer токен

@apiSuccessExample Детальная информация:
    HTTP/1.1 200 OK
    {
        "id": 1,
        "user_id": 1,
        "username": "user1",
        "result_type": "test",
        "key": "variables_lesson_1",
        "exp_earned": 100,
        "created_at": "2024-01-15T10:30:00Z"
    }
"""
class UserResultDetail(APIView):
    @with_authorization
    def get(self, request, result_id: int):
        try:
            result = UserResult.objects.get(id=result_id, user=request.user)
        except UserResult.DoesNotExist:
            return Response({'error': 'Result not found'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = UserResultSerializer(result)
        return Response(serializer.data)


"""
@api {GET} /api/user/stats/ UserStats
@apiGroup User
@apiDescription Получить статистику пользователя
@apiHeader {String} Authorization Bearer токен

@apiSuccessExample Статистика:
    HTTP/1.1 200 OK
    {
        "total_exp": 1250,
        "total_tests": 5,
        "total_practice": 10,
        "total_theory": 8,
        "total_games": 3,
        "last_activity": "2024-01-15T10:30:00Z",
        "achievements_count": 4
    }
"""
class UserStats(APIView):
    @with_authorization
    def get(self, request):
        user = request.user
        results = UserResult.objects.filter(user=user)
        
        # Статистика по типам
        total_tests = results.filter(result_type='test').count()
        total_practice = results.filter(result_type='practice').count()
        total_theory = results.filter(result_type='theory').count()
        total_games = results.filter(result_type='game').count()
        
        # Последняя активность
        last_result = results.order_by('-created_at').first()
        last_activity = last_result.created_at if last_result else None
        
        return Response({
            'total_exp': user.profile.exp,
            'total_tests': total_tests,
            'total_practice': total_practice,
            'total_theory': total_theory,
            'total_games': total_games,
            'last_activity': last_activity,
            'achievements_count': user.achievements.count(),
        })