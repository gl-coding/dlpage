"""
URL configuration for backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect

# 根路径重定向函数
def redirect_to_links(request):
    return redirect('/datapost/links/')

# 原始URL配置
original_urlpatterns = [
    path('', redirect_to_links, name='home'),  # 根路径重定向到链接展示页
    path('admin/', admin.site.urls),
    path('datapost/', include('datapost.urls')),
]

# 添加API前缀的URL配置
api_urlpatterns = [
    path('api/admin/', admin.site.urls),
    path('api/datapost/', include('datapost.urls')),
]

# 同时支持原始URL和带API前缀的URL
urlpatterns = original_urlpatterns + api_urlpatterns
