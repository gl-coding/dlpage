from django.urls import path
from .views import post_data, show_data, clear_data, delete_data, export_all_data, show_json_data, json_data_only

urlpatterns = [
    path('', post_data, name='post_data'),
    path('show/', show_data, name='show_data'),
    path('clear/', clear_data, name='clear_data'),
    path('delete/', delete_data, name='delete_data'),
    path('export/', export_all_data, name='export_all_data'),
    path('json/', show_json_data, name='show_json_data'),
    path('api/', json_data_only, name='json_data_only'),
] 