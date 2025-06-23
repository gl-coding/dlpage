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
    # 准备模板上下文
    context = {
        'page': page,
        'paginator': paginator
    }
    
    # 使用render函数渲染模板
    return render(request, 'datapost/show_data.html', context)
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
            
            export_time = timezone.now().strftime("%Y-%m-%d %H:%M:%S")
            
            json_data = {
                'total_videos': len(unique_videos),
                'export_time': export_time,
                'videos': unique_videos
            }
            
            # 格式化 JSON 为美观的字符串
            formatted_json = json.dumps(json_data, ensure_ascii=False, indent=2)
            
            context = {
                'total_videos': len(unique_videos),
                'export_time': export_time,
                'formatted_json': escape(formatted_json)
            }
            
            return render(request, 'datapost/json_data.html', context)
            
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
    
    context = {
        'page': page,
        'paginator': paginator,
        'total_count': VideoText.objects.count()
    }
    
    return render(request, 'datapost/video_text.html', context)

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
