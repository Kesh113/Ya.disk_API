from django.shortcuts import render
from django.http import HttpResponseNotFound
import requests
from urllib.parse import unquote


from ya_disk.forms import KeyForm

URL = 'https://cloud-api.yandex.net/v1/disk/public/resources'
public_key = None
    

def get_files(path: str='') -> dict:
    """Получаем данные из выбранного каталога в виде словаря"""
    response = requests.get(f'{URL}?public_key={public_key}&path={path}')
    return response.json()['_embedded']['items']


def index(request):
    """Запрос у пользователя публичной ссылки и получение данных с диска"""
    data = None
    global public_key
    
    if request.method == 'POST':
        form = KeyForm(request.POST)
        if form.is_valid():
            public_key = form.cleaned_data['public_key']
        try:
            response = requests.get(f'{URL}?public_key={public_key}')
            data = response.json()['_embedded']['items']
        except:
            return HttpResponseNotFound('Некорректная ссылка')    
    else:
        form = KeyForm()
 
    return render(request, 'ya_disk/index.html', {'form': form, 'data': data})


def path_folder(request, path1: str=''):
    """Переход по каталогам"""
    try:
        data = get_files(path1)
    except:
        return HttpResponseNotFound('Не верный путь') 
    return render(request, 'ya_disk/list_files.html', {'data': data, 'path': path1})

    
def download_files(request):
    """Загрузка файлов в каталог = BASE_DIR"""
    file_paths = request.POST.getlist('file_paths')
    statuses = []
    
    for file in file_paths:
        response = requests.get(file)
        if response.status_code == 200:
            file_name = unquote(file.split('&')[1].split('=')[1], 'utf-8')
            try:
                with open(file_name, 'wb') as output:
                    output.write(response.content)
                status = file_name + ' - успешно загружен'
            except:
                status = file_name + ' - некорректное название файла'
        else:
            status = 'При обращении к ' + file_name + ' Произошла ошибка HTTP ' + response.status_code
        statuses.append(status)
    return render(request, 'ya_disk/download_status.html', {'statuses': statuses})
    



    