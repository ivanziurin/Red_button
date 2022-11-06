from django import forms
from django.forms import TextInput

from .models import SparePartModel, StockModel


class SparePartModelForm(forms.ModelForm):
    class Meta:
        model = SparePartModel
        fields = ['name', 'min_value']
        widgets = {
            "name": TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'артикул'
            }),
            "min_value": TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Description'
            })
        }


class StockModelForm(forms.ModelForm):
    class Meta:
        model = StockModel
        fields = ['raw_img']

