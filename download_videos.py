import os
import requests
from urllib.parse import urlparse
import sqlite3
import argparse
import json
import datetime

OUTPUT_DIR = 'downloaded_videos'
DB_PATH = 'db.sqlite3'  # 默认django数据库路径
SQL = "SELECT data FROM datapost_datapost ORDER BY id ASC"
OUTPUT_TXT = 'output_videos.txt'
INPUT_FILE = OUTPUT_TXT
API_ENDPOINT = 'https://aliyun.ideapool.club/datapost/api/'  # 默认API接口地址
#API_ENDPOINT = 'http://127.0.0.1:8000/datapost/api/'  # 默认API接口地址

def download_video(url, save_path):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Accept-Encoding": "identity",  # 不要gzip，方便写入
            "Connection": "keep-alive",
            "Referer": url,  # 伪装为自身页面跳转
            "Origin": "https://www.douyin.com",
            "Sec-Fetch-Dest": "video",
            "Sec-Fetch-Mode": "no-cors",
            "Sec-Fetch-Site": "cross-site"
        }
        with requests.get(url, stream=True, timeout=30, headers=headers) as r:
            r.raise_for_status()
            with open(save_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
        print(f'下载完成: {save_path}')
        return True
    except Exception as e:
        print(f'下载失败: {url}，原因: {e}')
        return False

def get_ext_from_url(url):
    path = urlparse(url).path
    ext = os.path.splitext(path)[-1]
    if ext:
        return ext.lstrip('.')
    else:
        return 'mp4'

def export_unique_videos_from_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    seen = set()
    ordered = []
    for row in cur.execute(SQL):
        data = row[0]
        if data not in seen:
            seen.add(data)
            ordered.append(data)
    with open(OUTPUT_TXT, 'w', encoding='utf-8') as f:
        for item in ordered:
            f.write(item.strip() + '\n')
    print(f'已导出去重数据到 {OUTPUT_TXT}')
    conn.close()

def export_unique_video_links_from_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    seen = set()
    ordered = []
    for row in cur.execute(SQL):
        data = row[0]
        try:
            data_json = json.loads(data)
            if isinstance(data_json, dict) and 'videos' in data_json:
                for vurl in data_json['videos']:
                    if vurl not in seen:
                        seen.add(vurl)
                        ordered.append(vurl)
        except Exception:
            continue
    with open(OUTPUT_TXT, 'w', encoding='utf-8') as f:
        for item in ordered:
            f.write(item.strip() + '\n')
    print(f'已导出去重视频链接到 {OUTPUT_TXT}')
    conn.close()

def read_video_list_json(json_file):
    """读取 video_list_export.json 格式的文件并返回视频链接列表"""
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if isinstance(data, dict) and 'videos' in data:
            videos = data['videos']
            print(f'从 {json_file} 读取到 {len(videos)} 个视频链接')
            return videos
        else:
            print(f'错误：{json_file} 格式不正确，缺少 videos 字段')
            return []
    except FileNotFoundError:
        print(f'错误：文件 {json_file} 不存在')
        return []
    except json.JSONDecodeError as e:
        print(f'错误：{json_file} 不是有效的JSON文件: {e}')
        return []
    except Exception as e:
        print(f'读取文件 {json_file} 时出错: {e}')
        return []

def save_download_mapping(mapping_data, filename=None):
    """保存下载映射关系到文件
    
    Args:
        mapping_data: 包含映射关系的列表，每项为 [url, path, success]
        filename: 保存的文件名，如果为None则使用时间戳生成
    
    Returns:
        保存的文件名
    """
    if not filename:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f'download_mapping_{timestamp}.txt'
    
    with open(filename, 'w', encoding='utf-8') as f:
        for url, path, success in mapping_data:
            success_str = "成功" if success else "失败"
            f.write(f"{url}\t{path}\t{success_str}\n")
    
    print(f'已保存下载映射关系到: {filename}')
    return filename

def download_from_json(json_file, mapping_file=None):
    """从JSON文件读取视频链接并下载"""
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
    
    videos = read_video_list_json(json_file)
    if not videos:
        print('没有找到可下载的视频链接')
        return
    
    mapping_data = []
    print(f'开始下载 {len(videos)} 个视频...')
    for idx, url in enumerate(videos, 1):
        if not url.strip():
            continue
        ext = get_ext_from_url(url)
        save_path = os.path.join(OUTPUT_DIR, f'video_{idx:04d}.{ext}')
        print(f'[{idx}/{len(videos)}] 下载: {url}')
        success = download_video(url, save_path)
        mapping_data.append([url, save_path, success])
    
    # 保存映射关系
    if mapping_file is None:
        mapping_file = f'download_mapping_{os.path.basename(json_file).split(".")[0]}.txt'
    save_download_mapping(mapping_data, mapping_file)

def fetch_videos_from_api(api_url, save_json=False):
    """从API接口获取JSON数据并提取视频链接"""
    try:
        print(f'正在从API接口获取数据: {api_url}')
        response = requests.get(api_url, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        
        # 保存完整的JSON数据到本地
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        json_filename = None
        video_list_filename = None
        
        if save_json:
            json_filename = f'api_data_{timestamp}.json'
            with open(json_filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f'已保存API返回的完整JSON数据到: {json_filename}')
        
        if isinstance(data, dict) and 'videos' in data:
            videos = data['videos']
            total = data.get('total_videos', len(videos))
            print(f'从API接口获取到 {total} 个视频链接')
            
            # 保存视频列表到本地
            if save_json:
                video_list_filename = f'video_list_export_{timestamp}.json'
                video_list_data = {'videos': videos}
                with open(video_list_filename, 'w', encoding='utf-8') as f:
                    json.dump(video_list_data, f, ensure_ascii=False, indent=2)
                print(f'已提取视频列表并保存到: {video_list_filename}')
                
            return videos, json_filename, video_list_filename
        else:
            print(f'错误：API返回格式不正确，缺少 videos 字段')
            print(f'API返回内容: {response.text[:200]}...')
            return [], None, None
    except requests.RequestException as e:
        print(f'API请求失败: {e}')
        return [], None, None
    except json.JSONDecodeError as e:
        print(f'API返回的不是有效的JSON数据: {e}')
        print(f'API返回内容: {response.text[:200]}...')
        return [], None, None
    except Exception as e:
        print(f'从API获取数据时出错: {e}')
        return [], None, None

def download_from_api(api_url, save_json=False, only_save=False, mapping_file=None):
    """从API接口获取视频链接并下载"""
    videos, json_filename, video_list_filename = fetch_videos_from_api(api_url, save_json)
    
    if only_save:
        if videos:
            print(f'已获取 {len(videos)} 个视频链接，根据 --only-save 选项设置，不进行下载')
        return
    
    if not videos:
        print('没有找到可下载的视频链接')
        return
    
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
    
    mapping_data = []
    print(f'开始下载 {len(videos)} 个视频...')
    for idx, url in enumerate(videos, 1):
        if not url.strip():
            continue
        ext = get_ext_from_url(url)
        save_path = os.path.join(OUTPUT_DIR, f'video_{idx:04d}.{ext}')
        print(f'[{idx}/{len(videos)}] 下载: {url}')
        success = download_video(url, save_path)
        mapping_data.append([url, save_path, success])
    
    # 保存映射关系
    if mapping_file is None and video_list_filename:
        mapping_file = f'download_mapping_{os.path.basename(video_list_filename).split(".")[0]}.txt'
    save_download_mapping(mapping_data, mapping_file)

def main(input_file=INPUT_FILE, mapping_file=None):
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
    
    mapping_data = []
    with open(input_file, 'r', encoding='utf-8') as f:
        lines = [line.strip() for line in f if line.strip()]
        
    print(f'开始下载 {len(lines)} 个视频...')
    for idx, url in enumerate(lines):
        ext = get_ext_from_url(url)
        save_path = os.path.join(OUTPUT_DIR, f'video_{idx+1:04d}.{ext}')
        print(f'[{idx+1}/{len(lines)}] 下载: {url}')
        success = download_video(url, save_path)
        mapping_data.append([url, save_path, success])
    
    # 保存映射关系
    if mapping_file is None:
        mapping_file = f'download_mapping_{os.path.basename(input_file).split(".")[0]}.txt'
    save_download_mapping(mapping_data, mapping_file)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='视频下载与数据导出工具')
    parser.add_argument('--export', action='store_true', help='从sqlite导出去重数据到output_videos.txt')
    parser.add_argument('--export-links', action='store_true', help='从sqlite导出去重视频链接到output_videos.txt')
    parser.add_argument('--download', action='store_true', help='下载视频（默认）')
    parser.add_argument('--json', type=str, help='从JSON文件读取视频链接并下载（如：video_list_export.json）')
    parser.add_argument('--api', action='store_true', help='从API接口读取视频链接并下载')
    parser.add_argument('--api-url', type=str, default=API_ENDPOINT, help=f'指定API接口地址，默认为 {API_ENDPOINT}')
    parser.add_argument('--input', type=str, default=INPUT_FILE, help='指定下载链接的输入文件，默认output_videos.txt')
    parser.add_argument('--save-json', action='store_true', help='使用--api选项时，保存API返回的JSON数据和视频列表到本地')
    parser.add_argument('--only-save', action='store_true', help='仅保存API返回的JSON数据和视频列表，不下载视频')
    parser.add_argument('--mapping', type=str, help='指定下载映射关系保存的文件名，默认使用自动生成的名称')
    args = parser.parse_args()

    if args.export:
        export_unique_videos_from_db()
    if args.export_links:
        export_unique_video_links_from_db()
    if args.api:
        # 如果指定了--only-save，则强制设置save_json为True
        if args.only_save:
            args.save_json = True
        download_from_api(args.api_url, args.save_json, args.only_save, args.mapping)
    elif args.json:
        download_from_json(args.json, args.mapping)
    elif args.download or not (args.export or args.export_links or args.json or args.api):
        main(args.input, args.mapping)
