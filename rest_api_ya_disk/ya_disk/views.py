from django.shortcuts import render
from django.http import HttpResponseNotFound, HttpResponsePermanentRedirect
from django.urls import reverse
import requests
import urllib.parse


from ya_disk.forms import NameForm

URL = 'https://cloud-api.yandex.net/v1/disk/public/resources'

def get_disc_files(public_key):
    """Получаем файлы с диска в виде словаря"""
    response = requests.get(f'{URL}?public_key={public_key}')
    return response.json()['_embedded']['items']

def get_path_files(public_key, path):
    """Получаем файлы с диска в виде словаря"""
    print(path)
    response = requests.get(f'{URL}?public_key={public_key}&path=/{path}')
    print(response)
    return response.json()['_embedded']['items']

def index(request):
    """Запрос публичной ссылки и получение списка файлов"""
    data = None
    public_key = None
    
    if request.method == 'POST':
        form = NameForm(request.POST)
        if form.is_valid():
            public_key = form.cleaned_data['public_key']
            public_key = urllib.parse.quote_plus(public_key)
        try:
            data = get_disc_files(public_key)
        except:
            return HttpResponseNotFound('Некорректная ссылка')    
    else:
        form = NameForm()
 
    return render(request, 'ya_disk/index.html', {'form': form, 'key': public_key, 'data': data})


def path_folder(request, key='', path=''):
    try:
        data = get_path_files(key, path)
    except:
        return HttpResponseNotFound('Не верный путь') 
    return render(request, 'ya_disk/list_files.html', {'data': data, 'key': key, 'path': path})
    