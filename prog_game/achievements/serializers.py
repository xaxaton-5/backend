from rest_framework import serializers
from achievements.models import Achievement, UserAchievement
from users.serializers import UserDetailSerializer, UserSerializer


class AchievementCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания достижения"""
    
    class Meta:
        model = Achievement
        fields = ['id', 'title', 'description', 'emoji', 'exp', 'users']


class AchievementSerializer(serializers.ModelSerializer):
    """Сериализатор для просмотра достижения с пользователями"""
    users = UserDetailSerializer(many=True, read_only=True)
    users_count = serializers.IntegerField(source='users.count', read_only=True)
    
    class Meta:
        model = Achievement
        fields = ['id', 'title', 'description', 'emoji', 'exp', 
                  'users', 'users_count']


class UserAchievementCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания связи пользователь-достижение"""
    
    class Meta:
        model = UserAchievement
        fields = ['id', 'user', 'achievement']
    
    def validate(self, data):
        """Проверяем, что достижение еще не получено пользователем"""
        user = data['user']
        achievement = data['achievement']
        
        if UserAchievement.objects.filter(user=user, achievement=achievement).exists():
            raise serializers.ValidationError("Пользователь уже получил это достижение")
        
        return data
    
    def create(self, validated_data):
        """Создаем связь и начисляем опыт"""
        user = validated_data['user']
        achievement = validated_data['achievement']
        
        # Создаем запись о получении достижения
        user_achievement = UserAchievement.objects.create(
            user=user,
            achievement=achievement
        )
        
        # Начисляем опыт пользователю через профиль
        profile = user.profile
        profile.add_exp(achievement.exp)
        
        return user_achievement


class UserAchievementSerializer(serializers.ModelSerializer):
    """Сериализатор для просмотра связи пользователь-достижение"""
    user = UserSerializer(read_only=True)
    achievement = AchievementSerializer(read_only=True)
    
    class Meta:
        model = UserAchievement
        fields = ['id', 'user', 'achievement', 'datetime']