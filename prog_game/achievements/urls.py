from django.urls import path

from achievements import views


urlpatterns = [
    path('achievements/list/', views.AchievementList.as_view()),
    path('achievements/user/<int:user_id>/', views.UserAchievementList.as_view()),
    path('achievements/user/create/', views.UserAchievementCreate.as_view()),
]
