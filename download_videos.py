import os
import requests
from urllib.parse import urlparse

INPUT_FILE = '/Users/guolei/Downloads/all_videoss.txt'
OUTPUT_DIR = 'downloaded_videos'

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

def main():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        for idx, line in enumerate(f):
            url = line.strip()
            if not url:
                continue
            ext = get_ext_from_url(url)
            save_path = os.path.join(OUTPUT_DIR, f'video_{idx+1}.{ext}')
            download_video(url, save_path)

if __name__ == '__main__':
    main()
