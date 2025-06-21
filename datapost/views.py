from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .models import DataPost, VideoText
import json
import os
import time
from django.utils.html import escape
from django.core.paginator import Paginator
from django.utils import timezone

# Create your views here.

@csrf_exempt
def post_data(request):
    if request.method == 'POST':
        try:
            data = request.body.decode('utf-8')
            DataPost.objects.create(data=data)
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    else:
        return JsonResponse({'status': 'error', 'message': 'Only POST allowed'}, status=405)

def show_data(request):
    page_num = int(request.GET.get('page', 1))
    posts = DataPost.objects.all().order_by('-created_at')
    paginator = Paginator(posts, 20)
    page = paginator.get_page(page_num)
    html = '''<h2>已接收数据列表</h2>
    <button onclick="clearData()" style="margin-bottom:1em;">清空所有数据</button>
    <a href="/datapost/export/" style="margin-left:1em;padding:5px 10px;background:#007cba;color:white;text-decoration:none;border-radius:3px;">导出视频列表(JSON)</a>
    <a href="/datapost/json/" style="margin-left:1em;padding:5px 10px;background:#28a745;color:white;text-decoration:none;border-radius:3px;">查看 JSON 数据</a>
    <a href="/datapost/video-text/show/" style="margin-left:1em;padding:5px 10px;background:#6c757d;color:white;text-decoration:none;border-radius:3px;">视频文本数据</a>
    <script>
    function clearData() {
        if(confirm('确定要清空所有数据吗？')){
            fetch('/datapost/clear/', {method: 'POST'}).then(r => r.json()).then(d => {window.location.reload();});
        }
    }
    function gotoPage(p) {
        window.location.search = '?page=' + p;
    }
    </script>
    '''
    for post in page:
        try:
            data_json = json.loads(post.data)
        except Exception:
            data_json = None
        html += f'<div style="margin-bottom:2em;">'
        html += f'<div><b>接收时间：</b>{post.created_at}</div>'
        html += f'<button onclick="deleteData({post.id})" style=\'color:red;margin-bottom:0.5em;\'>删除本条</button>'
        if data_json and isinstance(data_json, dict) and 'videos' in data_json:
            html += '<div><b>视频列表：</b></div><ul>'
            for vurl in data_json['videos']:
                html += f'<li><video src="{escape(vurl)}" controls width="320"></video><br><a href="{escape(vurl)}" target="_blank">{escape(vurl)}</a></li>'
            html += '</ul>'
        else:
            html += f'<pre>{escape(post.data)}</pre>'
        html += '</div>'
    # 分页导航
    html += '<div style="margin:2em 0;">'
    if page.has_previous():
        html += f'<button onclick="gotoPage({page.previous_page_number()})">上一页</button>'
    html += f' 第 {page.number} / {paginator.num_pages} 页 '
    if page.has_next():
        html += f'<button onclick="gotoPage({page.next_page_number()})">下一页</button>'
    html += '</div>'
    html += '''<script>
    function deleteData(id) {
        if(confirm('确定要删除本条数据吗？')){
            fetch('/datapost/delete/', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({id: id})
            }).then(r => r.json()).then(d => {window.location.reload();});
        }
    }
    </script>'''
    return HttpResponse(html)

@csrf_exempt
def clear_data(request):
    if request.method == 'POST':
        DataPost.objects.all().delete()
        return JsonResponse({'status': 'success', 'message': '所有数据已清除'})
    else:
        return JsonResponse({'status': 'error', 'message': 'Only POST allowed'}, status=405)

@csrf_exempt
def delete_data(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            post_id = data.get('id')
            if post_id is not None:
                DataPost.objects.filter(id=post_id).delete()
                return JsonResponse({'status': 'success', 'message': f'id={post_id} 已删除'})
            else:
                return JsonResponse({'status': 'error', 'message': '缺少id参数'}, status=400)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    else:
        return JsonResponse({'status': 'error', 'message': 'Only POST allowed'}, status=405)

def export_all_data(request):
    """导出所有数据中的视频列表"""
    if request.method == 'GET':
        try:
            posts = DataPost.objects.all().order_by('-created_at')
            all_videos = []
            
            for post in posts:
                # 尝试解析 JSON 数据，提取视频链接
                try:
                    parsed_data = json.loads(post.data)
                    if isinstance(parsed_data, dict) and 'videos' in parsed_data:
                        videos = parsed_data['videos']
                        if isinstance(videos, list):
                            all_videos.extend(videos)
                except json.JSONDecodeError:
                    # 如果不是JSON格式，跳过
                    continue
            
            # 去重，保持顺序
            unique_videos = []
            seen = set()
            for video in all_videos:
                if video not in seen:
                    unique_videos.append(video)
                    seen.add(video)
            
            response_data = {
                'total_videos': len(unique_videos),
                'export_time': DataPost.objects.first().created_at.isoformat() if DataPost.objects.exists() else None,
                'videos': unique_videos
            }
            
            # 设置响应头，支持文件下载
            response = JsonResponse(response_data, json_dumps_params={'ensure_ascii': False, 'indent': 2})
            response['Content-Disposition'] = 'attachment; filename="video_list_export.json"'
            return response
            
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    else:
        return JsonResponse({'status': 'error', 'message': 'Only GET allowed'}, status=405)

def show_json_data(request):
    """展示 JSON 格式的视频数据"""
    if request.method == 'GET':
        try:
            posts = DataPost.objects.all().order_by('-created_at')
            all_videos = []
            
            for post in posts:
                # 尝试解析 JSON 数据，提取视频链接
                try:
                    parsed_data = json.loads(post.data)
                    if isinstance(parsed_data, dict) and 'videos' in parsed_data:
                        videos = parsed_data['videos']
                        if isinstance(videos, list):
                            all_videos.extend(videos)
                except json.JSONDecodeError:
                    # 如果不是JSON格式，跳过
                    continue
            
            # 去重，保持顺序
            unique_videos = []
            seen = set()
            for video in all_videos:
                if video not in seen:
                    unique_videos.append(video)
                    seen.add(video)
            
            json_data = {
                'total_videos': len(unique_videos),
                'export_time': timezone.now().isoformat(),
                'videos': unique_videos
            }
            
            # 格式化 JSON 为美观的字符串
            formatted_json = json.dumps(json_data, ensure_ascii=False, indent=2)
            
            html = f'''
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <title>JSON 数据展示</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 20px; }}
                    .header {{ margin-bottom: 20px; }}
                    .stats {{ background: #f5f5f5; padding: 15px; border-radius: 5px; margin-bottom: 20px; }}
                    .json-container {{ 
                        background: #f8f8f8; 
                        border: 1px solid #ddd; 
                        border-radius: 5px; 
                        padding: 15px; 
                        max-height: 600px; 
                        overflow-y: auto; 
                    }}
                    pre {{ 
                        margin: 0; 
                        white-space: pre-wrap; 
                        word-wrap: break-word; 
                        font-size: 12px; 
                        line-height: 1.4; 
                    }}
                    .button {{ 
                        display: inline-block; 
                        padding: 8px 16px; 
                        margin: 5px; 
                        background: #007cba; 
                        color: white; 
                        text-decoration: none; 
                        border-radius: 3px; 
                    }}
                    .button:hover {{ background: #005a8b; }}
                    .copy-btn {{ 
                        background: #28a745; 
                        color: white; 
                        border: none; 
                        padding: 8px 16px; 
                        border-radius: 3px; 
                        cursor: pointer; 
                        margin-left: 10px; 
                    }}
                    .copy-btn:hover {{ background: #218838; }}
                </style>
            </head>
            <body>
                <div class="header">
                    <h2>JSON 数据展示</h2>
                    <a href="/datapost/show/" class="button">返回数据列表</a>
                    <a href="/datapost/export/" class="button">下载 JSON 文件</a>
                    <button class="copy-btn" onclick="copyJson()">复制 JSON</button>
                </div>
                
                <div class="stats">
                    <strong>统计信息：</strong><br>
                    总视频数量: {len(unique_videos)}<br>
                    导出时间: {timezone.now().strftime("%Y-%m-%d %H:%M:%S")}<br>
                    数据格式: video_list_export.json 兼容格式
                </div>
                
                <div class="json-container">
                    <pre id="jsonContent">{escape(formatted_json)}</pre>
                </div>
                
                <script>
                function copyJson() {{
                    const content = document.getElementById('jsonContent').textContent;
                    navigator.clipboard.writeText(content).then(function() {{
                        const btn = document.querySelector('.copy-btn');
                        const originalText = btn.textContent;
                        btn.textContent = '已复制!';
                        btn.style.background = '#28a745';
                        setTimeout(function() {{
                            btn.textContent = originalText;
                            btn.style.background = '#28a745';
                        }}, 2000);
                    }}).catch(function(err) {{
                        alert('复制失败，请手动选择复制');
                    }});
                }}
                </script>
            </body>
            </html>
            '''
            
            return HttpResponse(html)
            
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    else:
        return JsonResponse({'status': 'error', 'message': 'Only GET allowed'}, status=405)

def json_data_only(request):
    """只返回纯 JSON 数据，无任何其他内容"""
    if request.method == 'GET':
        try:
            posts = DataPost.objects.all().order_by('-created_at')
            all_videos = []
            
            for post in posts:
                # 尝试解析 JSON 数据，提取视频链接
                try:
                    parsed_data = json.loads(post.data)
                    if isinstance(parsed_data, dict) and 'videos' in parsed_data:
                        videos = parsed_data['videos']
                        if isinstance(videos, list):
                            all_videos.extend(videos)
                except json.JSONDecodeError:
                    # 如果不是JSON格式，跳过
                    continue
            
            # 去重，保持顺序
            unique_videos = []
            seen = set()
            for video in all_videos:
                if video not in seen:
                    unique_videos.append(video)
                    seen.add(video)
            
            json_data = {
                'total_videos': len(unique_videos),
                'export_time': timezone.now().isoformat(),
                'videos': unique_videos
            }
            
            return JsonResponse(json_data, json_dumps_params={'ensure_ascii': False, 'indent': 2})
            
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    else:
        return JsonResponse({'status': 'error', 'message': 'Only GET allowed'}, status=405)

@csrf_exempt
def post_video_text(request):
    """接收视频URL和对应的文本内容"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            video_url = data.get('video_url')
            text_content = data.get('text_content')
            
            if not video_url:
                return JsonResponse({'status': 'error', 'message': '缺少视频URL'}, status=400)
            
            # 创建新记录
            VideoText.objects.create(
                video_url=video_url,
                text_content=text_content or ''  # 文本内容可以为空
            )
            
            return JsonResponse({
                'status': 'success',
                'message': '视频文本数据已保存'
            })
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': '无效的JSON数据'}, status=400)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    else:
        return JsonResponse({'status': 'error', 'message': 'Only POST allowed'}, status=405)

def show_video_text(request):
    """展示视频URL和对应的文本内容"""
    page_num = int(request.GET.get('page', 1))
    video_texts = VideoText.objects.all().order_by('-created_at')
    paginator = Paginator(video_texts, 20)  # 每页20条
    page = paginator.get_page(page_num)
    
    html = '''<!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>视频文本数据</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                margin: 20px;
                line-height: 1.6;
            }
            h2 {
                color: #333;
                border-bottom: 1px solid #eee;
                padding-bottom: 10px;
            }
            .video-text-item {
                margin-bottom: 30px;
                padding: 15px;
                border: 1px solid #ddd;
                border-radius: 5px;
                background-color: #f9f9f9;
            }
            .video-container {
                margin-bottom: 15px;
            }
            video {
                max-width: 100%;
                border-radius: 5px;
            }
            .text-content {
                background-color: #fff;
                padding: 10px;
                border: 1px solid #eee;
                border-radius: 5px;
                white-space: pre-wrap;
            }
            .timestamp {
                color: #777;
                font-size: 0.9em;
                margin-top: 10px;
            }
            .pagination {
                margin-top: 30px;
                text-align: center;
            }
            .pagination button {
                padding: 5px 15px;
                margin: 0 5px;
                cursor: pointer;
            }
            .url-link {
                word-break: break-all;
                margin-bottom: 10px;
                font-size: 0.9em;
            }
            .header-buttons {
                margin-bottom: 20px;
            }
            .header-buttons a {
                display: inline-block;
                margin-right: 10px;
                padding: 8px 15px;
                background-color: #007bff;
                color: white;
                text-decoration: none;
                border-radius: 4px;
            }
            .delete-btn {
                background-color: #dc3545;
                color: white;
                border: none;
                padding: 5px 10px;
                border-radius: 3px;
                cursor: pointer;
                margin-top: 10px;
            }
            .clear-all-btn {
                background-color: #dc3545;
                color: white;
                border: none;
                padding: 8px 15px;
                border-radius: 4px;
                cursor: pointer;
                margin-right: 10px;
            }
            .stats {
                margin-bottom: 20px;
                padding: 10px;
                background-color: #f8f9fa;
                border-radius: 4px;
                border: 1px solid #e9ecef;
            }
            .text-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 5px;
            }
            .copy-btn {
                background-color: #28a745;
                color: white;
                border: none;
                padding: 3px 10px;
                border-radius: 3px;
                cursor: pointer;
                font-size: 0.9em;
            }
            .copy-btn:hover {
                background-color: #218838;
            }
            .copy-success {
                background-color: #218838;
            }
            .api-link {
                background-color: #17a2b8;
            }
            .api-link:hover {
                background-color: #138496;
            }
            .timestamp-btn {
                background-color: #6c757d;
                color: white;
                border: none;
                padding: 8px 15px;
                border-radius: 4px;
                cursor: pointer;
                margin-right: 10px;
            }
            .timestamp-btn:hover {
                background-color: #5a6268;
            }
            .notification {
                position: fixed;
                top: 20px;
                right: 20px;
                padding: 15px 20px;
                background-color: #28a745;
                color: white;
                border-radius: 4px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.2);
                display: none;
                z-index: 1000;
                transition: opacity 0.3s;
                opacity: 0;
            }
            .notification.show {
                display: block;
                opacity: 1;
            }
        </style>
    </head>
    <body>
        <h2>视频文本数据</h2>
        <div class="header-buttons">
            <a href="/datapost/show/">返回数据列表</a>
            <a href="/datapost/video-text/export/">导出视频文本数据</a>
            <a href="/datapost/video-text/api/" class="api-link" target="_blank">API接口</a>
            <button class="timestamp-btn" onclick="createTimestampFile()">更新时间戳文件</button>
            <button class="clear-all-btn" onclick="clearAllData()">清空所有数据</button>
        </div>
        
        <div class="stats">
            总记录数: ''' + str(VideoText.objects.count()) + '''
        </div>
        
        <div id="notification" class="notification"></div>
    '''
    
    for item in page:
        html += f'''
        <div class="video-text-item">
            <div class="video-container">
                <video src="{escape(item.video_url)}" controls width="320"></video>
            </div>
            <div class="url-link">
                <strong>视频链接：</strong> <a href="{escape(item.video_url)}" target="_blank">{escape(item.video_url)}</a>
            </div>
            <div>
                <div class="text-header">
                    <strong>文本内容：</strong>
                    <button class="copy-btn" onclick="copyText(this, 'text-content-{item.id}')">复制文本</button>
                </div>
                <div class="text-content" id="text-content-{item.id}">{escape(item.text_content)}</div>
            </div>
            <div class="timestamp">添加时间：{item.created_at}</div>
            <button class="delete-btn" onclick="deleteVideoText({item.id})">删除</button>
        </div>
        '''
    
    # 分页导航
    html += '<div class="pagination">'
    if page.has_previous():
        html += f'<button onclick="gotoPage({page.previous_page_number()})">上一页</button>'
    html += f' 第 {page.number} / {paginator.num_pages} 页 '
    if page.has_next():
        html += f'<button onclick="gotoPage({page.next_page_number()})">下一页</button>'
    html += '</div>'
    
    html += '''
    <script>
    function gotoPage(p) {
        window.location.search = '?page=' + p;
    }
    
    function deleteVideoText(id) {
        if(confirm('确定要删除这条数据吗？')) {
            fetch('/datapost/video-text/delete/', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({id: id})
            }).then(r => r.json()).then(d => {
                if(d.status === 'success') {
                    window.location.reload();
                } else {
                    alert('删除失败: ' + d.message);
                }
            });
        }
    }
    
    function clearAllData() {
        if(confirm('确定要清空所有视频文本数据吗？此操作不可恢复！')) {
            fetch('/datapost/video-text/clear/', {
                method: 'POST'
            }).then(r => r.json()).then(d => {
                if(d.status === 'success') {
                    alert(d.message);
                    window.location.reload();
                } else {
                    alert('清空失败: ' + d.message);
                }
            });
        }
    }
    
    function copyText(button, elementId) {
        const text = document.getElementById(elementId).innerText;
        navigator.clipboard.writeText(text).then(function() {
            // 复制成功，改变按钮样式和文字
            button.textContent = '已复制';
            button.classList.add('copy-success');
            
            // 2秒后恢复按钮样式
            setTimeout(function() {
                button.textContent = '复制文本';
                button.classList.remove('copy-success');
            }, 2000);
        }).catch(function(err) {
            alert('复制失败: ' + err);
        });
    }
    
    function createTimestampFile() {
        fetch('/datapost/create-timestamp-file/', {
            method: 'POST'
        }).then(r => r.json()).then(d => {
            if(d.status === 'success') {
                showNotification(d.message);
            } else {
                alert('创建文件失败: ' + d.message);
            }
        }).catch(function(err) {
            alert('请求失败: ' + err);
        });
    }
    
    function showNotification(message) {
        const notification = document.getElementById('notification');
        notification.textContent = message;
        notification.classList.add('show');
        
        // 3秒后隐藏通知
        setTimeout(function() {
            notification.classList.remove('show');
        }, 3000);
    }
    </script>
    </body>
    </html>
    '''
    
    return HttpResponse(html)

@csrf_exempt
def delete_video_text(request):
    """删除视频文本数据"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            item_id = data.get('id')
            if item_id is not None:
                VideoText.objects.filter(id=item_id).delete()
                return JsonResponse({'status': 'success', 'message': f'id={item_id} 已删除'})
            else:
                return JsonResponse({'status': 'error', 'message': '缺少id参数'}, status=400)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    else:
        return JsonResponse({'status': 'error', 'message': 'Only POST allowed'}, status=405)

def export_video_text(request):
    """导出视频文本数据为JSON格式"""
    if request.method == 'GET':
        try:
            video_texts = VideoText.objects.all().order_by('-created_at')
            data = []
            
            for item in video_texts:
                data.append({
                    'video_url': item.video_url,
                    'text_content': item.text_content,
                    'created_at': item.created_at.isoformat()
                })
            
            response_data = {
                'total': len(data),
                'export_time': timezone.now().isoformat(),
                'items': data
            }
            
            # 设置响应头，支持文件下载
            response = JsonResponse(response_data, json_dumps_params={'ensure_ascii': False, 'indent': 2})
            response['Content-Disposition'] = 'attachment; filename="video_text_export.json"'
            return response
            
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    else:
        return JsonResponse({'status': 'error', 'message': 'Only GET allowed'}, status=405)

@csrf_exempt
def clear_video_text(request):
    """清空所有视频文本数据"""
    if request.method == 'POST':
        try:
            count = VideoText.objects.count()
            VideoText.objects.all().delete()
            return JsonResponse({
                'status': 'success', 
                'message': f'所有视频文本数据已清除，共删除 {count} 条记录'
            })
        except Exception as e:
            return JsonResponse({
                'status': 'error', 
                'message': f'清除数据失败: {str(e)}'
            }, status=500)
    else:
        return JsonResponse({
            'status': 'error', 
            'message': 'Only POST allowed'
        }, status=405)

def video_text_api(request):
    """返回所有视频文本数据的JSON格式API接口"""
    if request.method == 'GET':
        try:
            # 获取分页参数
            page = request.GET.get('page', '1')
            page_size = request.GET.get('page_size', '50')
            
            try:
                page = int(page)
                page_size = min(int(page_size), 200)  # 限制每页最大数量为200
            except ValueError:
                page = 1
                page_size = 50
            
            # 获取所有视频文本数据
            video_texts = VideoText.objects.all().order_by('-created_at')
            
            # 计算总数
            total_count = video_texts.count()
            
            # 分页
            paginator = Paginator(video_texts, page_size)
            current_page = paginator.get_page(page)
            
            # 构建响应数据
            items = []
            for item in current_page:
                items.append({
                    'id': item.id,
                    'video_url': item.video_url,
                    'text_content': item.text_content,
                    'created_at': item.created_at.isoformat()
                })
            
            response_data = {
                'status': 'success',
                'total_count': total_count,
                'page': page,
                'page_size': page_size,
                'total_pages': paginator.num_pages,
                'has_next': current_page.has_next(),
                'has_previous': current_page.has_previous(),
                'items': items
            }
            
            return JsonResponse(response_data, json_dumps_params={'ensure_ascii': False})
            
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=500)
    else:
        return JsonResponse({
            'status': 'error',
            'message': 'Only GET method is allowed'
        }, status=405)

@csrf_exempt
def create_timestamp_file(request):
    """创建一个包含秒级时间戳的文件，使用固定文件名"""
    if request.method == 'POST':
        try:
            # 获取当前时间戳
            timestamp = int(time.time())
            
            # 使用固定文件名
            filename = "timestamp.txt"
            
            # 获取当前工作目录
            current_dir = os.getcwd()
            
            # 文件完整路径
            file_path = os.path.join(current_dir, filename)
            
            # 写入文件
            with open(file_path, 'w') as f:
                f.write(f"时间戳: {timestamp}\n")
                f.write(f"更新时间: {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            
            return JsonResponse({
                'status': 'success',
                'message': f'已更新文件: {filename}',
                'file_path': file_path,
                'timestamp': timestamp
            })
            
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': f'更新文件失败: {str(e)}'
            }, status=500)
    else:
        return JsonResponse({
            'status': 'error',
            'message': 'Only POST method is allowed'
        }, status=405)
