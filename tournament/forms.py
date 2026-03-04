from django import forms
from .models import Registration

class RegistrationForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['college'].widget.attrs.update({'class': 'form-control', 'id': 'collegeName'})

    class Meta:
        model = Registration
        fields = ['college', 'name', 'prn', 'department', 'photo']
        widgets = {
            'college': forms.HiddenInput(), # Usually hidden in reg page since it's pre-filled from session
            'name': forms.TextInput(attrs={'class': 'form-control', 'id': 'studentName', 'placeholder': 'Enter full name', 'required': 'required'}),
            'prn': forms.TextInput(attrs={'class': 'form-control', 'id': 'prn', 'placeholder': 'Enter PRN', 'required': 'required'}),
            'department': forms.TextInput(attrs={'class': 'form-control', 'id': 'department', 'placeholder': 'Enter department', 'required': 'required'}),
            'photo': forms.FileInput(attrs={'class': 'form-control', 'id': 'studentPhoto', 'accept': 'image/*', 'required': 'required'}),
        }
