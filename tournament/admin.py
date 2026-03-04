from django.contrib import admin
from .models import Registration

@admin.register(Registration)
class RegistrationAdmin(admin.ModelAdmin):
    list_display = ('name', 'college', 'prn', 'department', 'created_at')
    list_filter = ('college', 'department')
    search_fields = ('name', 'prn')
