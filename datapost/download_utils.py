import requests
import os
import tempfile
import zipfile
from urllib.parse import urlparse

def download_and_zip(urls, zip_path):
    temp_dir = tempfile.mkdtemp()
    file_paths = []
    for url in urls:
        try:
            filename = os.path.basename(urlparse(url).path)
            if not filename:
                filename = 'video.mp4'
            local_path = os.path.join(temp_dir, filename)
            r = requests.get(url, stream=True, timeout=30)
            with open(local_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            file_paths.append(local_path)
        except Exception as e:
            continue
    with zipfile.ZipFile(zip_path, 'w') as zipf:
        for file in file_paths:
            zipf.write(file, os.path.basename(file))
    # 清理临时文件
    for file in file_paths:
        os.remove(file)
    os.rmdir(temp_dir)
    return zip_path
