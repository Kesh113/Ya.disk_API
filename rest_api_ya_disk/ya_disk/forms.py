from django import forms


class KeyForm(forms.Form):
    public_key = forms.URLField(max_length=255, label='Публичная ссылка на диск')