from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from users.models import Profile


class ProfileSerializer(serializers.ModelSerializer):
    """Сериализатор для профиля"""
    parent = serializers.SerializerMethodField()
    children = serializers.SerializerMethodField()
    
    class Meta:
        model = Profile
        fields = ['exp', 'is_parent', 'parent', 'parent', 'children']
    
    def get_parent(self, obj):
        """Получить родителя"""
        if obj.parent:
            return {
                'id': obj.parent.user.id,
                'username': obj.parent.user.username,
                'email': obj.parent.user.email
            }
        return None
    
    def get_children(self, obj):
        """Получить детей"""
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


class RegistrationSerializer(serializers.ModelSerializer):
    """Сериализатор для регистрации нового пользователя"""
    login = serializers.CharField(source='username', required=True, write_only=True)
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    password_confirm = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    email = serializers.EmailField(required=True)
    
    # Поля профиля
    exp = serializers.IntegerField(source='profile.exp', required=False, default=0, read_only=True)
    is_parent = serializers.BooleanField(source='profile.is_parent', required=False, default=False)
    parent = serializers.PrimaryKeyRelatedField(
        source='profile.parent',
        queryset=Profile.objects.all(),
        required=False,
        allow_null=True
    )
    
    class Meta:
        model = User
        fields = ['id', 'login', 'username', 'password', 'password_confirm', 'email', 
                  'first_name', 'last_name', 'exp', 'is_parent', 'parent']
        extra_kwargs = {
            'first_name': {'required': False},
            'last_name': {'required': False},
        }
    
    def validate(self, data):
        """Проверка данных"""
        # Проверяем, что пароли совпадают
        password = data.get('password')
        password_confirm = data.get('password_confirm')
        
        if password != password_confirm:
            raise serializers.ValidationError({"password": "Passwords do not match"})
        
        # Проверяем, что login (username) уникален
        username = data.get('username')
        if User.objects.filter(username=username).exists():
            raise serializers.ValidationError({"login": "User with this login already exists"})
        
        # Проверяем, что email уникален
        email = data.get('email')
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError({"email": "User with this email already exists"})
        
        # Проверяем parent
        profile_data = data.get('profile', {})
        parent = profile_data.get('parent')
        if parent:
            if not parent.is_parent:
                raise serializers.ValidationError({"parent": "Specified user is not a parent"})
        
        return data
    
    def create(self, validated_data):
        """Создание пользователя"""
        # Извлекаем данные
        password = validated_data.pop('password')
        validated_data.pop('password_confirm')  # Удаляем подтверждение пароля
        username = validated_data.pop('username')
        profile_data = validated_data.pop('profile', {})
        
        # Создаем пользователя
        validated_data['username'] = username
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        
        # Обновляем профиль
        profile = user.profile
        for attr, value in profile_data.items():
            if attr == 'parent' and value:
                setattr(profile, attr, value)
            elif attr != 'parent':
                setattr(profile, attr, value)
        profile.save()
        
        return user


class LoginSerializer(serializers.Serializer):
    """Сериализатор для входа пользователя"""
    login = serializers.CharField(required=True, help_text="Username or email")
    password = serializers.CharField(required=True, write_only=True, style={'input_type': 'password'})
    
    def validate(self, data):
        """Проверка учетных данных"""
        login = data.get('login')
        password = data.get('password')
        
        if not login or not password:
            raise serializers.ValidationError("Both login and password are required")
        
        # Пытаемся найти пользователя по username или email
        user = None
        if '@' in login:
            # Если login содержит @, ищем по email
            try:
                user = User.objects.get(email=login)
            except User.DoesNotExist:
                pass
        else:
            # Ищем по username
            try:
                user = User.objects.get(username=login)
            except User.DoesNotExist:
                pass
        
        if user is None:
            raise serializers.ValidationError("Invalid login credentials")
        
        # Аутентифицируем пользователя
        authenticated_user = authenticate(username=user.username, password=password)
        
        if authenticated_user is None:
            raise serializers.ValidationError("Invalid login credentials")
        
        if not authenticated_user.is_active:
            raise serializers.ValidationError("User account is disabled")
        
        data['user'] = authenticated_user
        return data


class UserCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания пользователя (административный)"""
    login = serializers.CharField(source='username', required=True)
    password = serializers.CharField(write_only=True, required=True)
    exp = serializers.IntegerField(source='profile.exp', required=False, default=0)
    is_parent = serializers.BooleanField(source='profile.is_parent', required=False, default=False)
    parent = serializers.PrimaryKeyRelatedField(
        source='profile.parent',
        queryset=Profile.objects.all(),
        required=False,
        allow_null=True
    )
    
    class Meta:
        model = User
        fields = ['id', 'login', 'username', 'password', 'email', 'first_name', 
                  'last_name', 'exp', 'is_parent', 'parent']
    
    def validate_parent(self, value):
        """Проверяем, что родитель существует и является родителем"""
        if value:
            if not value.is_parent:
                raise serializers.ValidationError("Указанный пользователь не является родителем")
        return value
    
    def create(self, validated_data):
        profile_data = validated_data.pop('profile', {})
        password = validated_data.pop('password')
        username = validated_data.pop('username')
        validated_data['username'] = username
        
        # Создаем пользователя
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        
        # Обновляем профиль
        profile = user.profile
        for attr, value in profile_data.items():
            if attr == 'parent' and value:
                setattr(profile, attr, value)
            elif attr != 'parent':
                setattr(profile, attr, value)
        profile.save()
        
        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    """Сериализатор для обновления пользователя"""
    email = serializers.EmailField(required=False)
    first_name = serializers.CharField(required=False)
    last_name = serializers.CharField(required=False)
    exp = serializers.IntegerField(source='profile.exp', required=False)
    is_parent = serializers.BooleanField(source='profile.is_parent', required=False)
    parent = serializers.PrimaryKeyRelatedField(
        source='profile.parent',
        queryset=Profile.objects.all(),
        required=False,
        allow_null=True
    )
    
    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'exp', 'is_parent', 'parent']
    
    def validate_parent(self, value):
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
            if attr == 'parent' and value:
                setattr(profile, attr, value)
            elif attr != 'parent':
                setattr(profile, attr, value)
        profile.save()
        
        return instance


class UserDetailSerializer(serializers.ModelSerializer):
    """Детальный сериализатор для пользователя с профилем"""
    login = serializers.CharField(source='username', read_only=True)
    profile = ProfileSerializer(read_only=True)
    achievements_count = serializers.IntegerField(source='achievements.count', read_only=True)
    total_exp = serializers.IntegerField(source='profile.exp', read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'login', 'username', 'email', 'first_name', 'last_name',
                  'profile', 'achievements_count', 'total_exp', 'date_joined']


class UserSerializer(serializers.ModelSerializer):
    """Базовый сериализатор для пользователя"""
    login = serializers.CharField(source='username', read_only=True)
    exp = serializers.IntegerField(source='profile.exp', read_only=True)
    is_parent = serializers.BooleanField(source='profile.is_parent', read_only=True)
    parent = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'login', 'username', 'email', 'first_name', 'last_name', 
                  'exp', 'is_parent', 'parent', 'date_joined']
    
    def get_parent(self, obj):
        """Получить ID родителя"""
        if obj.profile.parent:
            return obj.profile.parent.user.id
        return None