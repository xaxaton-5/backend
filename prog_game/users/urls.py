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
    
    # Дети и родители
    path('user/children/', api.ChildrenList.as_view()),  # Список детей текущего пользователя
    path('user/children/<int:user_id>/', api.UserChildrenList.as_view()),  # Список детей конкретного пользователя
    path('user/parent/', api.UserParent.as_view()),  # Получить родителя текущего пользователя
    path('user/parent/<int:user_id>/', api.UserParentDetail.as_view()),  # Получить родителя конкретного пользователя
    path('user/add-child/', api.AddChild.as_view()),  # Добавить ребенка (создать нового)
    path('user/link-child/', api.LinkChild.as_view()),  # Привязать существующего ребенка
    path('user/remove-child/<int:child_id>/', api.RemoveChild.as_view()),  # Отвязать ребенка
    
    # Административные
    path('admin/users/create/', api.UserCreate.as_view()),
    path('admin/users/update/<int:user_id>/', api.UserAdminUpdate.as_view()),
]