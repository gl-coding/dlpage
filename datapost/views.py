from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .models import DataPost
import json
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
