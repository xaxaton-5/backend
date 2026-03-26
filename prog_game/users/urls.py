from django.urls import path


from users import api


urlpatterns = [
    path('users/list/', api.UserList.as_view()),
    path('user/detail/<int:user_id>/', api.UserDetail.as_view()),
    path('register/', api.Registration.as_view()),
    path('login/', api.Login.as_view()),
    path('auth/', api.CheckToken.as_view()),
]
