from django.contrib.auth.models import User
from django.db import transaction

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

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
        return Response({'token': token, 'user': LoginSerializer(user).data})


class CheckToken(APIView):
    serializer_class = LoginSerializer

    @with_authorization
    def get(self, request):
        if not request.user or not request.user.is_active:
            return Response({'id': -1}, status=status.HTTP_401_UNAUTHORIZED)
        return Response(self.serializer_class(request.user).data)


class UserUpdate(APIView):
    @with_authorization
    def put(self, request, user_id: int):
        # Проверяем, что обновляем свой профиль
        if request.user.id != user_id:
            return Response({'error': 'You can only update your own profile'}, 
                          status=status.HTTP_403_FORBIDDEN)
        
        # Используем request.user вместо отдельного запроса
        serializer = UserUpdateSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(UserDetailSerializer(request.user).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


"""
@api {POST} /api/user/deactivate/ UserDeactivate
@apiGroup User
@apiDescription Деактивация пользователя (мягкое удаление)
"""
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
        # Если запрашиваем свои данные - используем request.user
        if request.user.id == user_id:
            profile = request.user.profile
        else:
            # Проверяем права админа
            if not request.user.is_staff:
                return Response({'error': 'Permission denied'}, 
                              status=status.HTTP_403_FORBIDDEN)
            
            # Получаем пользователя с профилем одним запросом
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