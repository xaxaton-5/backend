from django.urls import path
from users import api

urlpatterns = [
    # Пользователи
    path('users/list/', api.UserList.as_view()),
    path('user/detail/<int:user_id>/', api.UserDetail.as_view()),
    path('user/update/<int:user_id>/', api.UserUpdate.as_view()),
    
    # Аутентификация
    path('register/', api.Registration.as_view()),
    path('login/', api.Login.as_view()),
    path('auth/', api.CheckToken.as_view()),
    
    # Результаты и статистика
    path('user/result/', api.UserResultCreate.as_view()),  # Создать результат
    path('user/results/', api.UserResultList.as_view()),  # Список результатов
    path('user/result/<int:result_id>/', api.UserResultDetail.as_view()),  # Детали результата
    path('user/stats/', api.UserStats.as_view()),  # Статистика пользователя
    
    # Дети и родители
    path('user/children/', api.ChildrenList.as_view()),
    path('user/children/<int:user_id>/', api.UserChildrenList.as_view()),
    path('user/parent/', api.UserParent.as_view()),
    path('user/parent/<int:user_id>/', api.UserParentDetail.as_view()),
    path('user/add-child/', api.AddChild.as_view()),
    path('user/link-child/', api.LinkChild.as_view()),
    path('user/remove-child/<int:child_id>/', api.RemoveChild.as_view()),
    
    # Административные
    path('admin/users/create/', api.UserCreate.as_view()),
    path('admin/users/update/<int:user_id>/', api.UserAdminUpdate.as_view()),
]