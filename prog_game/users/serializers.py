from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework.exceptions import ValidationError
from users.models import Profile


class ProfileSerializer(serializers.ModelSerializer):
    """Сериализатор для профиля"""
    parent = serializers.SerializerMethodField()
    children = serializers.SerializerMethodField()
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    
    class Meta:
        model = Profile
        fields = ['id', 'username', 'email', 'exp', 'is_parent', 'parent', 'children']
    
    def get_parent(self, obj):
        """Получить информацию о родителе"""
        if obj.parent:
            return {
                'id': obj.parent.user.id,
                'username': obj.parent.user.username,
                'email': obj.parent.user.email,
                'exp': obj.parent.exp
            }
        return None
    
    def get_children(self, obj):
        """Получить информацию о детях"""
        if obj.is_parent:
            children = Profile.objects.filter(parent=obj)
            return [
                {
                    'id': child.user.id,
                    'username': child.user.username,
                    'email': child.user.email,
                    'exp': child.exp
                }
                for child in children
            ]
        return []


class ChildProfileSerializer(serializers.ModelSerializer):
    """Упрощенный сериализатор для детей"""
    user_id = serializers.IntegerField(source='user.id', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    
    class Meta:
        model = Profile
        fields = ['user_id', 'username', 'email', 'exp', 'created_at']


class RegistrationSerializer(serializers.ModelSerializer):
    """Сериализатор для регистрации нового пользователя"""
    username = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    password_confirm = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    
    # Поля профиля
    is_parent = serializers.BooleanField(default=False)
    parent_id = serializers.IntegerField(required=False, allow_null=True, write_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'password_confirm', 'is_parent', 'parent_id']
    
    def validate(self, data):
        """Проверка данных"""
        # Проверяем, что пароли совпадают
        password = data.get('password')
        password_confirm = data.get('password_confirm')
        
        if password != password_confirm:
            raise serializers.ValidationError({"password": "Passwords do not match"})
        
        # Проверяем, что username уникален
        username = data.get('username')
        if User.objects.filter(username=username).exists():
            raise serializers.ValidationError({"username": "User with this username already exists"})
        
        # Проверяем, что email уникален
        email = data.get('email')
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError({"email": "User with this email already exists"})
        
        # Проверяем parent_id
        parent_id = data.get('parent_id')
        if parent_id:
            try:
                parent_profile = Profile.objects.get(id=parent_id)
                if not parent_profile.is_parent:
                    raise serializers.ValidationError({"parent_id": "Specified user is not a parent"})
                data['parent_profile'] = parent_profile
            except Profile.DoesNotExist:
                raise serializers.ValidationError({"parent_id": "Parent profile not found"})
        
        return data
    
    def create(self, validated_data):
        """Создание пользователя"""
        # Извлекаем данные
        password = validated_data.pop('password')
        validated_data.pop('password_confirm')
        is_parent = validated_data.pop('is_parent', False)
        parent_profile = validated_data.pop('parent_profile', None)
        
        # Создаем пользователя
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=password
        )
        
        # Обновляем профиль
        profile = user.profile
        profile.is_parent = is_parent
        if parent_profile:
            profile.parent = parent_profile
        profile.exp = 0  # exp по умолчанию 0
        profile.save()
        
        return user


class LinkChildSerializer(serializers.Serializer):
    """Сериализатор для привязки существующего ребенка"""
    child_id = serializers.IntegerField(required=True, help_text="ID ребенка для привязки")
    
    def validate_child_id(self, value):
        """Проверка, что ребенок существует и не имеет родителя"""
        try:
            child_profile = Profile.objects.get(user__id=value)
        except Profile.DoesNotExist:
            raise ValidationError("Child profile not found")
        
        if child_profile.parent:
            raise ValidationError("This child already has a parent")
        
        if child_profile.is_parent:
            raise ValidationError("Cannot set a parent as a child")
        
        return value


class AddChildSerializer(serializers.Serializer):
    """Сериализатор для создания нового ребенка"""
    username = serializers.CharField(required=True, help_text="Логин ребенка")
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, required=True)
    password_confirm = serializers.CharField(write_only=True, required=True)
    
    def validate(self, data):
        """Проверка данных"""
        if data['password'] != data['password_confirm']:
            raise ValidationError({"password": "Passwords do not match"})
        
        if User.objects.filter(username=data['username']).exists():
            raise ValidationError({"username": "Username already exists"})
        
        if User.objects.filter(email=data['email']).exists():
            raise ValidationError({"email": "Email already exists"})
        
        return data


class LoginSerializer(serializers.Serializer):
    """Сериализатор для входа пользователя"""
    email = serializers.EmailField(required=True, help_text="Email пользователя")
    password = serializers.CharField(required=True, write_only=True, style={'input_type': 'password'})
    
    def validate(self, data):
        """Проверка учетных данных"""
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            raise serializers.ValidationError("Both email and password are required")
        
        # Ищем пользователя по email
        try:
            user = User.objects.get(email=email, is_active=True)
        except User.DoesNotExist:
            raise serializers.ValidationError("Invalid email or password")
        
        # Аутентифицируем пользователя
        authenticated_user = authenticate(username=user.username, password=password)
        
        if authenticated_user is None:
            raise serializers.ValidationError("Invalid email or password")
        
        data['user'] = authenticated_user
        return data


class UserDetailSerializer(serializers.ModelSerializer):
    """Детальный сериализатор для пользователя с профилем"""
    profile = ProfileSerializer(read_only=True)
    achievements_count = serializers.IntegerField(source='achievements.count', read_only=True)
    total_exp = serializers.IntegerField(source='profile.exp', read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'profile', 'achievements_count', 'total_exp', 'date_joined']


class UserSerializer(serializers.ModelSerializer):
    """Базовый сериализатор для пользователя"""
    exp = serializers.IntegerField(source='profile.exp', read_only=True)
    is_parent = serializers.BooleanField(source='profile.is_parent', read_only=True)
    parent_id = serializers.IntegerField(source='profile.parent.id', read_only=True)
    children_count = serializers.IntegerField(source='profile.children.count', read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'exp', 'is_parent', 'parent_id', 'children_count', 'date_joined']


class UserUpdateSerializer(serializers.ModelSerializer):
    """Сериализатор для обновления пользователя (обычный пользователь)"""
    email = serializers.EmailField(required=False)
    
    class Meta:
        model = User
        fields = ['email']


class UserAdminUpdateSerializer(serializers.ModelSerializer):
    """Сериализатор для обновления пользователя (администратор)"""
    email = serializers.EmailField(required=False)
    exp = serializers.IntegerField(source='profile.exp', required=False)
    is_parent = serializers.BooleanField(source='profile.is_parent', required=False)
    parent_id = serializers.PrimaryKeyRelatedField(
        source='profile.parent',
        queryset=Profile.objects.all(),
        required=False,
        allow_null=True
    )
    
    class Meta:
        model = User
        fields = ['email', 'exp', 'is_parent', 'parent_id']
    
    def validate_parent_id(self, value):
        """Проверяем, что родитель существует и является родителем"""
        if value:
            if not value.is_parent:
                raise serializers.ValidationError("Указанный пользователь не является родителем")
        return value
    
    def update(self, instance, validated_data):
        profile_data = validated_data.pop('profile', {})
        
        # Обновляем поля User
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Обновляем поля Profile
        profile = instance.profile
        for attr, value in profile_data.items():
            if value is not None:
                setattr(profile, attr, value)
        profile.save()
        
        return instance