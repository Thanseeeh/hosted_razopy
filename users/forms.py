from django import forms
from .models import Token

class TokenForm(forms.ModelForm):
    class Meta:
        model = Token
        fields = ['name', 'description', 'price', 'brand', 'image', 'category']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Name', 'style': 'height: 2.8em; border-radius: 10px'}),
            'description': forms.Textarea(attrs={'placeholder': 'This art is...', 'rows': '4', 'cols': '50', 'style': 'border-radius: 10px'}),
            'price': forms.TextInput(attrs={'placeholder': '0.00', 'style': 'height: 2.8em; border-radius: 10px'}),
            'brand': forms.TextInput(attrs={'placeholder': 'Brand name', 'style': 'height: 2.8em; border-radius: 10px'}),
            'category': forms.Select(attrs={'style': 'height: 2.8em; border-radius: 10px'}),
        }
