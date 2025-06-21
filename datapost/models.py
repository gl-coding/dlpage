from django.db import models

# Create your models here.

class DataPost(models.Model):
    data = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

class VideoText(models.Model):
    video_url = models.URLField(max_length=500)
    text_content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.video_url[:30]}... - {self.text_content[:30]}..."
