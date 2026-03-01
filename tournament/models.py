from django.db import models
from django.core.exceptions import ValidationError

class College(models.Model):
    name = models.CharField(max_length=200, unique=True)
    username = models.CharField(max_length=150, unique=True, null=True, blank=True)
    password = models.CharField(max_length=128, null=True, blank=True)

    def __str__(self):
        return self.name

    @property
    def registration_count(self):
        return self.registrations.count()

class Registration(models.Model):
    college = models.ForeignKey(College, on_delete=models.CASCADE, related_name='registrations')
    name = models.CharField(max_length=100)
    prn = models.CharField(max_length=50, unique=True)
    department = models.CharField(max_length=100)
    photo = models.ImageField(upload_to='student_photos/')
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        # Only check if college is assigned
        try:
            if not self.pk and self.college and self.college.registrations.count() >= 18:
                raise ValidationError(f"The 18 student registration for {self.college.name} is completed.")
        except (College.DoesNotExist, AttributeError):
            pass

    def save(self, *args, **kwargs):
        # self.full_clean() # We'll skip call here to avoid double check if view handles it
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.college.name})"
