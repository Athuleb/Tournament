from django import forms
from .models import Registration, College

class RegistrationForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['college'].queryset = College.objects.all()
        self.fields['college'].empty_label = "Select College"
        self.fields['college'].widget.attrs.update({'class': 'form-control', 'id': 'collegeName'})

    class Meta:
        model = Registration
        fields = ['college', 'name', 'prn', 'department', 'photo']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'id': 'studentName', 'placeholder': 'Enter full name'}),
            'prn': forms.TextInput(attrs={'class': 'form-control', 'id': 'prn', 'placeholder': 'Enter PRN'}),
            'department': forms.TextInput(attrs={'class': 'form-control', 'id': 'department', 'placeholder': 'Enter department'}),
            'photo': forms.FileInput(attrs={'class': 'form-control', 'id': 'studentPhoto', 'accept': 'image/*'}),
        }
