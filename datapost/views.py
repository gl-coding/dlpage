from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .models import DataPost
import json
from django.utils.html import escape

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
    posts = DataPost.objects.all().order_by('-created_at')
    html = '''<h2>已接收数据列表</h2>
    <button onclick="clearData()" style="margin-bottom:1em;">清空所有数据</button>
    <script>
    function clearData() {
        if(confirm('确定要清空所有数据吗？')){
            fetch('/datapost/clear/', {method: 'POST'}).then(r => r.json()).then(d => {window.location.reload();});
        }
    }
    </script>
    '''
    for post in posts:
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
