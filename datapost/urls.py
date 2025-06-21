from django.urls import path
from .views import post_data, show_data, clear_data, delete_data, export_all_data, show_json_data, json_data_only, post_video_text, show_video_text, delete_video_text, export_video_text, clear_video_text, video_text_api, create_timestamp_file

urlpatterns = [
    path('', post_data, name='post_data'),
    path('show/', show_data, name='show_data'),
    path('clear/', clear_data, name='clear_data'),
    path('delete/', delete_data, name='delete_data'),
    path('export/', export_all_data, name='export_all_data'),
    path('json/', show_json_data, name='show_json_data'),
    path('api/', json_data_only, name='json_data_only'),
    path('video-text/', post_video_text, name='post_video_text'),
    path('video-text/show/', show_video_text, name='show_video_text'),
    path('video-text/delete/', delete_video_text, name='delete_video_text'),
    path('video-text/export/', export_video_text, name='export_video_text'),
    path('video-text/clear/', clear_video_text, name='clear_video_text'),
    path('video-text/api/', video_text_api, name='video_text_api'),
    path('create-timestamp-file/', create_timestamp_file, name='create_timestamp_file'),
] 