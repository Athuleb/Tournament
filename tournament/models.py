from django.db import models
from django.core.exceptions import ValidationError

class College(models.Model):
    name = models.CharField(max_length=200, unique=True)

    def __str__(self):
        return self.name

    @property
    def registration_count(self):
        return self.registrations.count()

class Registration(models.Model):
    college = models.ForeignKey(College, on_delete=models.CASCADE, related_name='registrations')
    name = models.CharField(max_length=100)
    prn = models.CharField(max_length=50)
    department = models.CharField(max_length=100)
    photo = models.ImageField(upload_to='student_photos/')
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        # We handle this in the view for better UX with AJAX, 
        # but kept here for model-level safety.
        if self.college.registrations.count() >= 18:
            raise ValidationError(f"The 18 student registration for {self.college.name} is completed.")

    def save(self, *args, **kwargs):
        # self.full_clean() # We'll skip call here to avoid double check if view handles it
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.college.name})"
