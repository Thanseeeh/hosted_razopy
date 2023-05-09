from django import forms
from .models import Category, News, Banner

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Category Name', 'style': 'height: 2.8em; border-radius: 10px;'}),
        }


#News form
class NewsForm(forms.ModelForm):

    class Meta:
        model = News
        fields = ['heading', 'image']
        widgets = {
            'heading': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Heading'}),
        }


#Banner form
class BannerForm(forms.ModelForm):

    class Meta:
        model = Banner
        fields = ['heading', 'image']
        widgets = {
            'heading': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Heading'}),
        }