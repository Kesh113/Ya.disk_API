from django.urls import path


from ya_disk import views



urlpatterns = [   
    path('api/', views.index, name='index'), # GET: форма получения public_key, POST: отображение публичного каталога
    path('api/filter/', views.filter, name='filter'),
    path('api/download/', views.download_files, name='download'), # POST: загрузка нескольких файлов одновременно
    path('api<path:path1>', views.path_folder, name='path_folder'), # POST: перемещение по каталогам
]