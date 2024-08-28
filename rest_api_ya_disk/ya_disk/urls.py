from django.urls import path, re_path

from ya_disk import views



urlpatterns = [
    path('api/', views.index, name='index'),
    path('api/key=<path:key>/<path:path>', views.path_folder, name='path')
]