from django import forms
from .models import Project

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['name', 'description', 'latitude', 'longitude', 'radius_m', 'assigned_staff']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'latitude': forms.NumberInput(attrs={'step': 'any', 'class': 'form-control'}),
            'longitude': forms.NumberInput(attrs={'step': 'any', 'class': 'form-control'}),
            'radius_m': forms.NumberInput(attrs={'class': 'form-control'}),
            'assigned_staff': forms.SelectMultiple(attrs={'class': 'form-control'}),
        }