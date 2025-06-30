from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .models import DataPost, VideoText, VoiceData, TypeContent, CustomLink
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

@csrf_exempt
def delete_single_video(request):
    """删除单个视频链接"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            post_id = data.get('post_id')
            video_url = data.get('video_url')
            
            if post_id is None or video_url is None:
                return JsonResponse({'status': 'error', 'message': '缺少必要参数'}, status=400)
            
            try:
                post = DataPost.objects.get(id=post_id)
                try:
                    post_data = json.loads(post.data)
                    if isinstance(post_data, dict) and 'videos' in post_data:
                        if video_url in post_data['videos']:
                            # 移除指定的视频链接
                            post_data['videos'].remove(video_url)
                            # 如果视频列表为空，可以选择删除整条记录或保留空列表
                            if not post_data['videos']:
                                post.delete()
                                return JsonResponse({'status': 'success', 'message': '视频已删除，记录已清空'})
                            else:
                                # 更新数据库记录
                                post.data = json.dumps(post_data)
                                post.save()
                                return JsonResponse({'status': 'success', 'message': '视频已从列表中删除'})
                        else:
                            return JsonResponse({'status': 'error', 'message': '视频链接不存在'}, status=404)
                    else:
                        return JsonResponse({'status': 'error', 'message': '数据格式不正确'}, status=400)
                except json.JSONDecodeError:
                    return JsonResponse({'status': 'error', 'message': '数据不是有效的JSON格式'}, status=400)
            except DataPost.DoesNotExist:
                return JsonResponse({'status': 'error', 'message': '记录不存在'}, status=404)
                
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    else:
        return JsonResponse({'status': 'error', 'message': 'Only POST allowed'}, status=405)

def view_log_file(request):
    """查看log.run文件内容"""
    try:
        # 使用相对路径访问log.run文件
        log_file_path = 'log.run'
        
        # 检查是否为AJAX请求
        if request.GET.get('ajax') == '1':
            if os.path.exists(log_file_path):
                try:
                    with open(log_file_path, 'r', encoding='utf-8') as f:
                        log_content = f.read()
                    return JsonResponse({'content': log_content})
                except Exception as e:
                    return JsonResponse({'error': f'读取文件时出错: {str(e)}'})
            else:
                return JsonResponse({'error': f'文件 {log_file_path} 不存在'})
        
        # 非AJAX请求，返回HTML页面
        if os.path.exists(log_file_path):
            with open(log_file_path, 'r', encoding='utf-8') as f:
                log_content = f.read()
            
            # 准备模板上下文
            context = {
                'log_content': log_content,
                'file_path': log_file_path
            }
            
            # 渲染模板
            return render(request, 'datapost/view_log.html', context)
        else:
            return render(request, 'datapost/view_log.html', {
                'error_message': f'文件 {log_file_path} 不存在',
                'file_path': log_file_path
            })
    except Exception as e:
        if request.GET.get('ajax') == '1':
            return JsonResponse({'error': f'读取文件时出错: {str(e)}'})
        return render(request, 'datapost/view_log.html', {
            'error_message': f'读取文件时出错: {str(e)}',
            'file_path': log_file_path if 'log_file_path' in locals() else '未知'
        })

@csrf_exempt
def post_voice_data(request):
    """接收voice、outfile、content三个参数的POST接口"""
    if request.method == 'POST':
        try:
            # 解析JSON数据
            data = json.loads(request.body.decode('utf-8'))
            
            # 获取三个必需参数
            voice = data.get('voice')
            outfile = data.get('outfile')
            content = data.get('content')
            
            # 验证参数
            if voice is None or outfile is None or content is None:
                return JsonResponse({
                    'status': 'error',
                    'message': '缺少必需参数，需要voice、outfile、content三个参数'
                }, status=400)
            
            # 保存到数据库
            voice_data = VoiceData.objects.create(
                voice=voice,
                outfile=outfile,
                content=content
            )
            
            return JsonResponse({
                'status': 'success',
                'message': '数据保存成功',
                'id': voice_data.id,
                'created_at': voice_data.created_at.isoformat()
            })
            
        except json.JSONDecodeError:
            return JsonResponse({
                'status': 'error',
                'message': '请求数据格式错误，需要JSON格式'
            }, status=400)
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': f'保存数据失败: {str(e)}'
            }, status=500)
    else:
        return JsonResponse({
            'status': 'error',
            'message': 'Only POST method is allowed'
        }, status=405)

def get_voice_data(request):
    """获取voice数据的GET接口"""
    if request.method == 'GET':
        try:
            # 获取分页参数
            page = request.GET.get('page', '1')
            page_size = request.GET.get('page_size', '20')
            
            try:
                page = int(page)
                page_size = min(int(page_size), 100)  # 限制每页最大数量为100
            except ValueError:
                page = 1
                page_size = 20
            
            # 获取所有voice数据
            voice_data_list = VoiceData.objects.all().order_by('-created_at')
            
            # 计算总数
            total_count = voice_data_list.count()
            
            # 分页
            paginator = Paginator(voice_data_list, page_size)
            current_page = paginator.get_page(page)
            
            # 构建响应数据
            items = []
            for item in current_page:
                items.append({
                    'id': item.id,
                    'voice': item.voice,
                    'outfile': item.outfile,
                    'content': item.content,
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
                'message': f'获取数据失败: {str(e)}'
            }, status=500)
    else:
        return JsonResponse({
            'status': 'error',
            'message': 'Only GET method is allowed'
        }, status=405)

def get_voice_data_by_id(request, voice_id):
    """根据ID获取单条voice数据的GET接口"""
    if request.method == 'GET':
        try:
            voice_data = VoiceData.objects.get(id=voice_id)
            
            response_data = {
                'status': 'success',
                'data': {
                    'id': voice_data.id,
                    'voice': voice_data.voice,
                    'outfile': voice_data.outfile,
                    'content': voice_data.content,
                    'created_at': voice_data.created_at.isoformat()
                }
            }
            
            return JsonResponse(response_data, json_dumps_params={'ensure_ascii': False})
            
        except VoiceData.DoesNotExist:
            return JsonResponse({
                'status': 'error',
                'message': f'ID为{voice_id}的数据不存在'
            }, status=404)
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': f'获取数据失败: {str(e)}'
            }, status=500)
    else:
        return JsonResponse({
            'status': 'error',
            'message': 'Only GET method is allowed'
        }, status=405)

def clear_voice_data(request):
    """清空所有voice数据的GET接口"""
    if request.method == 'GET':
        try:
            # 获取删除前的数量
            count = VoiceData.objects.count()
            
            # 删除所有数据
            VoiceData.objects.all().delete()
            
            return JsonResponse({
                'status': 'success',
                'message': f'所有voice数据已清空，共删除 {count} 条记录'
            })
            
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': f'清空数据失败: {str(e)}'
            }, status=500)
    else:
        return JsonResponse({
            'status': 'error',
            'message': 'Only GET method is allowed'
        }, status=405)

@csrf_exempt
def delete_voice_data(request, voice_id):
    """通过ID删除单条voice数据的POST接口"""
    if request.method == 'POST':
        try:
            # 查找指定ID的数据
            voice_data = VoiceData.objects.get(id=voice_id)
            
            # 保存删除前的信息用于返回
            deleted_info = {
                'id': voice_data.id,
                'voice': voice_data.voice,
                'outfile': voice_data.outfile,
                'content': voice_data.content,
                'created_at': voice_data.created_at.isoformat()
            }
            
            # 删除数据
            voice_data.delete()
            
            return JsonResponse({
                'status': 'success',
                'message': f'ID为{voice_id}的voice数据已删除',
                'deleted_data': deleted_info
            })
            
        except VoiceData.DoesNotExist:
            return JsonResponse({
                'status': 'error',
                'message': f'ID为{voice_id}的数据不存在'
            }, status=404)
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': f'删除数据失败: {str(e)}'
            }, status=500)
    else:
        return JsonResponse({
            'status': 'error',
            'message': 'Only POST method is allowed'
        }, status=405)

# TypeContent 相关接口

@csrf_exempt
def post_type_content(request):
    """创建type和content数据的POST接口"""
    if request.method == 'POST':
        try:
            # 尝试解析JSON数据
            data = json.loads(request.body.decode('utf-8'))
            
            # 获取参数
            type_value = data.get('type')
            content_value = data.get('content')
            
            # 验证参数
            if not type_value or not content_value:
                return JsonResponse({
                    'status': 'error',
                    'message': '缺少必需参数，需要type和content两个参数'
                }, status=400)
            
            # 保存到数据库
            type_content = TypeContent.objects.create(
                type=type_value,
                content=content_value
            )
            
            return JsonResponse({
                'status': 'success',
                'message': '数据保存成功',
                'id': type_content.id,
                'type': type_content.type,
                'content': type_content.content,
                'created_at': type_content.created_at.isoformat()
            }, json_dumps_params={'ensure_ascii': False})
            
        except json.JSONDecodeError:
            return JsonResponse({
                'status': 'error',
                'message': '请求数据格式错误，需要JSON格式'
            }, status=400)
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': f'保存数据失败: {str(e)}'
            }, status=500)
    else:
        return JsonResponse({
            'status': 'error',
            'message': 'Only POST method is allowed'
        }, status=405)

def get_type_content(request):
    """获取type_content数据的GET接口"""
    if request.method == 'GET':
        try:
            # 获取分页参数
            page = request.GET.get('page', '1')
            page_size = request.GET.get('page_size', '20')
            
            # 获取筛选参数
            type_filter = request.GET.get('type', '')
            
            try:
                page = int(page)
                page_size = min(int(page_size), 100)  # 限制每页最大数量为100
            except ValueError:
                page = 1
                page_size = 20
            
            # 获取数据，支持按type筛选
            queryset = TypeContent.objects.all().order_by('-created_at')
            if type_filter:
                queryset = queryset.filter(type__icontains=type_filter)
            
            # 计算总数
            total_count = queryset.count()
            
            # 分页
            paginator = Paginator(queryset, page_size)
            current_page = paginator.get_page(page)
            
            # 构建响应数据
            items = []
            for item in current_page:
                items.append({
                    'id': item.id,
                    'type': item.type,
                    'content': item.content,
                    'created_at': item.created_at.isoformat(),
                    'updated_at': item.updated_at.isoformat()
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
                'message': f'获取数据失败: {str(e)}'
            }, status=500)
    else:
        return JsonResponse({
            'status': 'error',
            'message': 'Only GET method is allowed'
        }, status=405)

def get_type_content_by_id(request, content_id):
    """根据ID获取单条type_content数据的GET接口"""
    if request.method == 'GET':
        try:
            type_content = TypeContent.objects.get(id=content_id)
            
            response_data = {
                'status': 'success',
                'data': {
                    'id': type_content.id,
                    'type': type_content.type,
                    'content': type_content.content,
                    'created_at': type_content.created_at.isoformat(),
                    'updated_at': type_content.updated_at.isoformat()
                }
            }
            
            return JsonResponse(response_data, json_dumps_params={'ensure_ascii': False})
            
        except TypeContent.DoesNotExist:
            return JsonResponse({
                'status': 'error',
                'message': f'ID为{content_id}的数据不存在'
            }, status=404)
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': f'获取数据失败: {str(e)}'
            }, status=500)
    else:
        return JsonResponse({
            'status': 'error',
            'message': 'Only GET method is allowed'
        }, status=405)

@csrf_exempt
def delete_type_content(request, content_id):
    """通过ID删除单条type_content数据的POST接口"""
    if request.method == 'POST':
        try:
            # 查找指定ID的数据
            type_content = TypeContent.objects.get(id=content_id)
            
            # 保存删除前的信息用于返回
            deleted_info = {
                'id': type_content.id,
                'type': type_content.type,
                'content': type_content.content,
                'created_at': type_content.created_at.isoformat(),
                'updated_at': type_content.updated_at.isoformat()
            }
            
            # 删除数据
            type_content.delete()
            
            return JsonResponse({
                'status': 'success',
                'message': f'ID为{content_id}的数据已删除',
                'deleted_data': deleted_info
            }, json_dumps_params={'ensure_ascii': False})
            
        except TypeContent.DoesNotExist:
            return JsonResponse({
                'status': 'error',
                'message': f'ID为{content_id}的数据不存在'
            }, status=404)
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': f'删除数据失败: {str(e)}'
            }, status=500)
    else:
        return JsonResponse({
            'status': 'error',
            'message': 'Only POST method is allowed'
        }, status=405)

def clear_type_content(request):
    """清空所有type_content数据的GET接口"""
    if request.method == 'GET':
        try:
            # 获取删除前的数量
            count = TypeContent.objects.count()
            
            # 删除所有数据
            TypeContent.objects.all().delete()
            
            return JsonResponse({
                'status': 'success',
                'message': f'所有type_content数据已清空，共删除 {count} 条记录'
            }, json_dumps_params={'ensure_ascii': False})
            
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': f'清空数据失败: {str(e)}'
            }, status=500)
    else:
        return JsonResponse({
            'status': 'error',
            'message': 'Only GET method is allowed'
        }, status=405)

# CustomLink 相关接口

def links_display_page(request):
    """链接展示页面 - 专注于浏览和访问链接"""
    links = CustomLink.objects.filter(is_active=True).order_by('-created_at')
    
    # 按分类分组
    categories = {}
    for link in links:
        category = link.category or '未分类'
        if category not in categories:
            categories[category] = []
        categories[category].append(link)
    
    context = {
        'categories': categories,
        'total_links': links.count()
    }
    
    return render(request, 'datapost/links_display.html', context)

def custom_links_page(request):
    """自定义链接管理页面 - 专注于管理功能"""
    links = CustomLink.objects.filter(is_active=True).order_by('-created_at')
    
    # 按分类分组
    categories = {}
    for link in links:
        category = link.category or '未分类'
        if category not in categories:
            categories[category] = []
        categories[category].append(link)
    
    context = {
        'categories': categories,
        'total_links': links.count()
    }
    
    return render(request, 'datapost/custom_links.html', context)

@csrf_exempt
def add_custom_link(request):
    """添加自定义链接的API接口"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            
            title = data.get('title', '').strip()
            url = data.get('url', '').strip()
            description = data.get('description', '').strip()
            category = data.get('category', '').strip()
            
            # 验证必填参数
            if not title or not url:
                return JsonResponse({
                    'status': 'error',
                    'message': '标题和链接地址不能为空'
                }, status=400)
            
            # 验证URL格式
            if not (url.startswith('http://') or url.startswith('https://')):
                url = 'https://' + url
            
            # 创建链接
            custom_link = CustomLink.objects.create(
                title=title,
                url=url,
                description=description,
                category=category or '未分类'
            )
            
            return JsonResponse({
                'status': 'success',
                'message': '链接添加成功',
                'link': {
                    'id': custom_link.id,
                    'title': custom_link.title,
                    'url': custom_link.url,
                    'description': custom_link.description,
                    'category': custom_link.category,
                    'created_at': custom_link.created_at.isoformat()
                }
            }, json_dumps_params={'ensure_ascii': False})
            
        except json.JSONDecodeError:
            return JsonResponse({
                'status': 'error',
                'message': '请求数据格式错误'
            }, status=400)
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': f'添加失败: {str(e)}'
            }, status=500)
    else:
        return JsonResponse({
            'status': 'error',
            'message': 'Only POST method is allowed'
        }, status=405)

@csrf_exempt
def delete_custom_link(request, link_id):
    """删除自定义链接"""
    if request.method == 'POST':
        try:
            link = CustomLink.objects.get(id=link_id)
            link_info = {
                'title': link.title,
                'url': link.url
            }
            link.delete()
            
            return JsonResponse({
                'status': 'success',
                'message': f'链接 "{link_info["title"]}" 已删除'
            }, json_dumps_params={'ensure_ascii': False})
            
        except CustomLink.DoesNotExist:
            return JsonResponse({
                'status': 'error',
                'message': '链接不存在'
            }, status=404)
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': f'删除失败: {str(e)}'
            }, status=500)
    else:
        return JsonResponse({
            'status': 'error',
            'message': 'Only POST method is allowed'
        }, status=405)

@csrf_exempt
def click_custom_link(request, link_id):
    """点击链接统计"""
    if request.method == 'POST':
        try:
            link = CustomLink.objects.get(id=link_id, is_active=True)
            link.click_count += 1
            link.save()
            
            return JsonResponse({
                'status': 'success',
                'url': link.url,
                'click_count': link.click_count
            })
            
        except CustomLink.DoesNotExist:
            return JsonResponse({
                'status': 'error',
                'message': '链接不存在或已禁用'
            }, status=404)
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': f'操作失败: {str(e)}'
            }, status=500)
    else:
        return JsonResponse({
            'status': 'error',
            'message': 'Only POST method is allowed'
        }, status=405)

def get_custom_links_api(request):
    """获取链接列表的API接口"""
    if request.method == 'GET':
        try:
            category_filter = request.GET.get('category', '')
            
            queryset = CustomLink.objects.filter(is_active=True)
            if category_filter:
                queryset = queryset.filter(category__icontains=category_filter)
            
            queryset = queryset.order_by('-created_at')
            
            links = []
            for link in queryset:
                links.append({
                    'id': link.id,
                    'title': link.title,
                    'url': link.url,
                    'description': link.description,
                    'category': link.category,
                    'click_count': link.click_count,
                    'created_at': link.created_at.isoformat()
                })
            
            return JsonResponse({
                'status': 'success',
                'total_count': len(links),
                'links': links
            }, json_dumps_params={'ensure_ascii': False})
            
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': f'获取数据失败: {str(e)}'
            }, status=500)
    else:
        return JsonResponse({
            'status': 'error',
            'message': 'Only GET method is allowed'
        }, status=405)

@csrf_exempt
def edit_custom_link(request, link_id):
    """编辑自定义链接"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            
            # 查找链接
            link = CustomLink.objects.get(id=link_id)
            
            # 获取参数
            title = data.get('title', '').strip()
            url = data.get('url', '').strip()
            description = data.get('description', '').strip()
            category = data.get('category', '').strip()
            
            # 验证必填参数
            if not title or not url:
                return JsonResponse({
                    'status': 'error',
                    'message': '标题和链接地址不能为空'
                }, status=400)
            
            # 验证URL格式
            if not (url.startswith('http://') or url.startswith('https://')):
                url = 'https://' + url
            
            # 更新链接信息
            link.title = title
            link.url = url
            link.description = description
            link.category = category or '未分类'
            link.save()
            
            return JsonResponse({
                'status': 'success',
                'message': '链接更新成功',
                'link': {
                    'id': link.id,
                    'title': link.title,
                    'url': link.url,
                    'description': link.description,
                    'category': link.category,
                    'updated_at': link.updated_at.isoformat()
                }
            }, json_dumps_params={'ensure_ascii': False})
            
        except CustomLink.DoesNotExist:
            return JsonResponse({
                'status': 'error',
                'message': '链接不存在'
            }, status=404)
        except json.JSONDecodeError:
            return JsonResponse({
                'status': 'error',
                'message': '请求数据格式错误'
            }, status=400)
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': f'更新失败: {str(e)}'
            }, status=500)
    else:
        return JsonResponse({
            'status': 'error',
            'message': 'Only POST method is allowed'
        }, status=405)

def get_custom_link_detail(request, link_id):
    """获取单个链接的详细信息用于编辑"""
    if request.method == 'GET':
        try:
            link = CustomLink.objects.get(id=link_id, is_active=True)
            
            return JsonResponse({
                'status': 'success',
                'link': {
                    'id': link.id,
                    'title': link.title,
                    'url': link.url,
                    'description': link.description,
                    'category': link.category,
                    'click_count': link.click_count,
                    'created_at': link.created_at.isoformat(),
                    'updated_at': link.updated_at.isoformat()
                }
            }, json_dumps_params={'ensure_ascii': False})
            
        except CustomLink.DoesNotExist:
            return JsonResponse({
                'status': 'error',
                'message': '链接不存在'
            }, status=404)
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': f'获取链接信息失败: {str(e)}'
            }, status=500)
    else:
        return JsonResponse({
            'status': 'error',
            'message': 'Only GET method is allowed'
        }, status=405)
