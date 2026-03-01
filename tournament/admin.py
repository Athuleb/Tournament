from django.contrib import admin
from django.contrib.auth.hashers import make_password
from .models import College, Registration

@admin.register(College)
class CollegeAdmin(admin.ModelAdmin):
    list_display = ('name', 'username', 'registration_count')
    search_fields = ('name', 'username')

    def save_model(self, request, obj, form, change):
        # Hash password if it's been changed or set for the first time
        if obj.password and not obj.password.startswith('pbkdf2_sha256$'):
            obj.password = make_password(obj.password)
        super().save_model(request, obj, form, change)

@admin.register(Registration)
class RegistrationAdmin(admin.ModelAdmin):
    list_display = ('name', 'college', 'prn', 'department', 'created_at')
    list_filter = ('college', 'department')
    search_fields = ('name', 'prn')
