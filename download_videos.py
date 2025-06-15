import os
import requests
from urllib.parse import urlparse
import sqlite3
import argparse
import json

OUTPUT_DIR = 'downloaded_videos'
DB_PATH = 'db.sqlite3'  # 默认django数据库路径
SQL = "SELECT data FROM datapost_datapost ORDER BY id ASC"
OUTPUT_TXT = 'output_videos.txt'
INPUT_FILE = OUTPUT_TXT

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
    except Exception as e:
        print(f'下载失败: {url}，原因: {e}')

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

def download_from_json(json_file):
    """从JSON文件读取视频链接并下载"""
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
    
    videos = read_video_list_json(json_file)
    if not videos:
        print('没有找到可下载的视频链接')
        return
    
    print(f'开始下载 {len(videos)} 个视频...')
    for idx, url in enumerate(videos, 1):
        if not url.strip():
            continue
        ext = get_ext_from_url(url)
        save_path = os.path.join(OUTPUT_DIR, f'video_{idx:04d}.{ext}')
        print(f'[{idx}/{len(videos)}] 下载: {url}')
        download_video(url, save_path)

def main(input_file=INPUT_FILE):
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
    with open(input_file, 'r', encoding='utf-8') as f:
        for idx, line in enumerate(f):
            url = line.strip()
            if not url:
                continue
            ext = get_ext_from_url(url)
            save_path = os.path.join(OUTPUT_DIR, f'video_{idx+1}.{ext}')
            download_video(url, save_path)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='视频下载与数据导出工具')
    parser.add_argument('--export', action='store_true', help='从sqlite导出去重数据到output_videos.txt')
    parser.add_argument('--export-links', action='store_true', help='从sqlite导出去重视频链接到output_videos.txt')
    parser.add_argument('--download', action='store_true', help='下载视频（默认）')
    parser.add_argument('--json', type=str, help='从JSON文件读取视频链接并下载（如：video_list_export.json）')
    parser.add_argument('--input', type=str, default=INPUT_FILE, help='指定下载链接的输入文件，默认output_videos.txt')
    args = parser.parse_args()

    if args.export:
        export_unique_videos_from_db()
    if args.export_links:
        export_unique_video_links_from_db()
    if args.json:
        download_from_json(args.json)
    elif args.download or not (args.export or args.export_links or args.json):
        main(args.input)
