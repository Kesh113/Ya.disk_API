import json
from django.shortcuts import render
from django.http import HttpResponseNotFound, HttpResponse, HttpResponsePermanentRedirect
import requests
from urllib.parse import unquote


from ya_disk.forms import KeyForm

URL = 'https://cloud-api.yandex.net/v1/disk/public/resources'
public_key = None
    

def get_files(path: str='') -> tuple[list, str]:
    """Получаем данные из выбранного каталога"""
    response = requests.get(f'{URL}?public_key={public_key}&path={path}')
    data = response.json()['_embedded']['items']
    json_data = response.text
    return data, json_data

def filter_types(data: list[dict]) -> dict:
    """Определяем MIME типы выведенных файлов и передаем их расширения для отображения"""
    exist_types = {'application/x-rar': '.rar', # Здесь добавляем MIME типы для отображения
                'application/vnd.rar': '.rar',
                'application/pdf': '.pdf',
                'application/vnd.ms-excel': '.xls', 
                'text/plain': '.txt',
                'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': '.xlsx',
                'image/jpeg': '.jpg/.jpeg', 
                'application/json': '.json',
                'application/xml': '.xml', 
                'application/msword': '.docx',
                'text/html': '.html',
                'application/vnd.ms-powerpoint': '.pptx'
                } 
    text_types = set()
    types = {}
    for item in data:
        if item['type'] == 'file':
            text_types.add(item['mime_type'])
    for type in text_types:
        if type in exist_types:
            types[type] = exist_types[type]
    return types


def index(request):
    """Запрос у пользователя публичной ссылки и получение данных с диска"""
    data = None
    json_data = None
    types_files = None
    global public_key
    
    if request.method == 'POST':
        form = KeyForm(request.POST)
        if form.is_valid():
            public_key = form.cleaned_data['public_key']
            
        response = requests.get(f'{URL}?public_key={public_key}')
        if response.status_code == 200:
            try:
                data = response.json()['_embedded']['items']
                full_data = response.json()
                if not data:
                    return HttpResponse(f'<h2>Публичный диск {full_data['public_url']} ("{full_data['name']}") пуст</h2>')
            except:
                return HttpResponse('Не корректный ответ сервера')
            json_data = response.text
        else:
            return HttpResponse('Код ошибки HTTP - ' + str(response.status_code))
        
        types_files = filter_types(data)
    else:
        form = KeyForm()
 
    return render(request, 'ya_disk/index.html', {'form': form, 'data': data, 'types_files': types_files, 'json_data': json_data})


def path_folder(request, path1: str=''):
    """Переход по каталогам"""
    try:
        data, json_data = get_files(path1)
    except:
        return HttpResponseNotFound('Не верный путь') 
    types_files = filter_types(data)
    return render(request, 'ya_disk/list_files.html', {'data': data, 'types_files': types_files, 'path': path1, 'json_data': json_data})

    
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
    

def filter(request):
    file_mime, type_files = request.POST.get('file_type').split(' + ')
    string = request.POST.get('json_data')
    list_data = json.loads(string)['_embedded']['items']
    path = json.loads(string)['path']
    filtered_data = []
    if file_mime:
        for file in list_data:
            if file['type'] != 'dir' and file['mime_type'] == file_mime:
                filtered_data.append(file)   
        return render(request, 'ya_disk/filtered_data.html', {'data': filtered_data, 'path': path, 'type_files': type_files})
    return HttpResponsePermanentRedirect('index')
    