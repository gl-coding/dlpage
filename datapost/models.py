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

class VoiceData(models.Model):
    voice = models.TextField()
    outfile = models.CharField(max_length=500)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.outfile} - {self.created_at}"

class TypeContent(models.Model):
    type = models.CharField(max_length=200, verbose_name="类型")
    content = models.TextField(verbose_name="内容")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    
    class Meta:
        verbose_name = "类型内容"
        verbose_name_plural = "类型内容"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.type} - {self.content[:50]}..."
