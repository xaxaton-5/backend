from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import path, include


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('users.urls')),
    path('api/', include('achievements.urls')),
    path('api/', include('messaging.urls')),
    path('api/', include('guilds.urls')),
]

urlpatterns += staticfiles_urlpatterns()
