from django.db import models
from django.core.exceptions import ValidationError

class Registration(models.Model):
    college = models.CharField(max_length=200) # Now stores the hardcoded college name
    name = models.CharField(max_length=100)
    prn = models.CharField(max_length=50, unique=True)
    department = models.CharField(max_length=100)
    photo = models.ImageField(upload_to='student_photos/')
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        # Limit check will be handled in the view since it's hardcoded and logic is simpler there
        pass

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.college})"
