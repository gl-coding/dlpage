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

class CustomLink(models.Model):
    title = models.CharField(max_length=200, verbose_name="链接标题")
    url = models.URLField(max_length=500, verbose_name="链接地址")
    description = models.TextField(blank=True, verbose_name="备注说明")
    category = models.CharField(max_length=100, blank=True, verbose_name="分类")
    is_active = models.BooleanField(default=True, verbose_name="是否启用")
    click_count = models.IntegerField(default=0, verbose_name="点击次数")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    
    class Meta:
        verbose_name = "自定义链接"
        verbose_name_plural = "自定义链接"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.url}"

class Article(models.Model):
    title = models.CharField(max_length=200, verbose_name="文章标题")
    content = models.TextField(verbose_name="文章内容")
    article_type = models.CharField(max_length=100, verbose_name="文章类型")
    audio_url = models.URLField(max_length=500, blank=True, verbose_name="音频链接")
    video_url = models.URLField(max_length=500, blank=True, verbose_name="视频链接")
    remarks = models.TextField(blank=True, verbose_name="备注")
    is_read = models.BooleanField(default=False, verbose_name="是否已读")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    
    class Meta:
        verbose_name = "文章"
        verbose_name_plural = "文章"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.article_type}"
