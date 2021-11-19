from django.conf.urls import url
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    url(r'^api/auth/', include('djoser.urls.authtoken')),
    path('api/', include('foodgram_api.urls'))
]
