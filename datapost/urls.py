from django.urls import path
from .views import post_data, show_data, clear_data, delete_data, export_all_data

urlpatterns = [
    path('', post_data, name='post_data'),
    path('show/', show_data, name='show_data'),
    path('clear/', clear_data, name='clear_data'),
    path('delete/', delete_data, name='delete_data'),
    path('export/', export_all_data, name='export_all_data'),
] 