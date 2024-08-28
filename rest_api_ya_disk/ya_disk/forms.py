from django import forms


class NameForm(forms.Form):
    public_key = forms.URLField(max_length=255, label='Публичная ссылка')