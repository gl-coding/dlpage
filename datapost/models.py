from django.db import models

# Create your models here.

class DataPost(models.Model):
    data = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
