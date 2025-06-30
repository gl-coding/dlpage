from django.urls import path
from .views import post_data, show_data, clear_data, delete_data, export_all_data, show_json_data, json_data_only, post_video_text, show_video_text, delete_video_text, update_video_text, export_video_text, clear_video_text, video_text_api, create_timestamp_file, delete_single_video, view_log_file, post_voice_data, get_voice_data, get_voice_data_by_id, clear_voice_data, delete_voice_data, post_type_content, get_type_content, get_type_content_by_id, delete_type_content, clear_type_content, links_display_page, custom_links_page, add_custom_link, delete_custom_link, click_custom_link, get_custom_links_api, edit_custom_link, get_custom_link_detail

urlpatterns = [
    path('', post_data, name='post_data'),
    path('show/', show_data, name='show_data'),
    path('clear/', clear_data, name='clear_data'),
    path('delete/', delete_data, name='delete_data'),
    path('delete-video/', delete_single_video, name='delete_single_video'),
    path('export/', export_all_data, name='export_all_data'),
    path('json/', show_json_data, name='show_json_data'),
    path('api/', json_data_only, name='json_data_only'),
    path('log/', view_log_file, name='view_log_file'),
    path('video-text/', post_video_text, name='post_video_text'),
    path('video-text/show/', show_video_text, name='show_video_text'),
    path('video-text/delete/', delete_video_text, name='delete_video_text'),
    path('video-text/update/', update_video_text, name='update_video_text'),
    path('video-text/export/', export_video_text, name='export_video_text'),
    path('video-text/clear/', clear_video_text, name='clear_video_text'),
    path('video-text/api/', video_text_api, name='video_text_api'),
    path('create-timestamp-file/', create_timestamp_file, name='create_timestamp_file'),
    path('voice/', post_voice_data, name='post_voice_data'),
    path('voice/list/', get_voice_data, name='get_voice_data'),
    path('voice/<int:voice_id>/', get_voice_data_by_id, name='get_voice_data_by_id'),
    path('voice/clear/', clear_voice_data, name='clear_voice_data'),
    path('voice/delete/<int:voice_id>/', delete_voice_data, name='delete_voice_data'),
    # TypeContent 相关路由
    path('type-content/', post_type_content, name='post_type_content'),
    path('type-content/list/', get_type_content, name='get_type_content'),
    path('type-content/<int:content_id>/', get_type_content_by_id, name='get_type_content_by_id'),
    path('type-content/delete/<int:content_id>/', delete_type_content, name='delete_type_content'),
    path('type-content/clear/', clear_type_content, name='clear_type_content'),
    # CustomLink 相关路由
    path('links/', links_display_page, name='links_display_page'),  # 展示页面
    path('links/manage/', custom_links_page, name='custom_links_page'),  # 管理页面
    path('links/add/', add_custom_link, name='add_custom_link'),
    path('links/edit/<int:link_id>/', edit_custom_link, name='edit_custom_link'),
    path('links/detail/<int:link_id>/', get_custom_link_detail, name='get_custom_link_detail'),
    path('links/delete/<int:link_id>/', delete_custom_link, name='delete_custom_link'),
    path('links/click/<int:link_id>/', click_custom_link, name='click_custom_link'),
    path('links/api/', get_custom_links_api, name='get_custom_links_api'),
] 