from django.contrib.auth.models import User

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from achievements.models import Achievement, UserAchievement
from achievements.serializers import (
    AchievementSerializer,
    UserAchievementCreateSerializer,
    UserAchievementSerializer,
)


class AchievementList(APIView):
    def get(self, request):
        achievements = Achievement.objects.all()
        data = [AchievementSerializer(achievement).data for achievement in achievements]
        return Response(data)


class UserAchievementList(APIView):
    def get(self, request, user_id: int):
        try:
            User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({'id': -1}, status=status.HTTP_404_NOT_FOUND)

        user_achievements = UserAchievement.objects.filter(user_id=user_id)
        data = [UserAchievementSerializer(user_achievement).data for user_achievement in user_achievements]
        return Response(data)


class UserAchievementCreate(APIView):
    serializer_class = UserAchievementCreateSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user_achievement = serializer.save()
        return Response(UserAchievementSerializer(user_achievement).data, status=status.HTTP_201_CREATED)
