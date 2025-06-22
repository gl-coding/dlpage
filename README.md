# Django 数据接收与展示系统

## 功能说明

- 提供 POST 接口，接收并存储任意数据（如 JSON），支持批量视频链接。
- 提供数据展示页面，自动解析并展示视频列表。
- 支持一键清空所有数据。
- 支持单条数据删除。
- 管理后台可查看和管理所有数据。
- 支持视频链接与文本内容的关联存储和展示。

## 接口说明

### 1. 数据上传接口
- **URL**：`/datapost/`
- **方法**：POST
- **请求体**：原始数据（推荐 JSON 格式）
- **示例**：
  ```json
  {
    "videos": [
      "https://example.com/video1.mp4",
      "https://example.com/video2.mp4"
    ]
  }
  ```
- **返回**：
  ```json
  {"status": "success"}
  ```

### 2. 数据展示页面
- **URL**：`/datapost/show/`
- **方法**：GET
- **功能**：展示所有已上传数据，自动识别并展示视频播放器。
- **页面功能**：
  - 清空所有数据按钮
  - 单条数据删除按钮

### 3. 清空所有数据接口
- **URL**：`/datapost/clear/`
- **方法**：POST
- **功能**：清空所有已存储数据
- **返回**：
  ```json
  {"status": "success", "message": "所有数据已清除"}
  ```

### 4. 删除单条数据接口
- **URL**：`/datapost/delete/`
- **方法**：POST
- **请求体**：JSON，包含要删除数据的id
  ```json
  {"id": 1}
  ```
- **返回**：
  ```json
  {"status": "success", "message": "id=1 已删除"}
  ```

### 5. 导出视频列表接口
- **URL**：`/datapost/export/`
- **方法**：GET
- **功能**：导出所有视频链接为JSON文件
- **返回**：JSON文件下载（文件名：video_list_export.json）
- **数据格式**：
  ```json
  {
    "total_videos": 5,
    "export_time": "2024-01-01T12:00:00.000000",
    "videos": [
      "https://example.com/video1.mp4",
      "https://example.com/video2.mp4"
    ]
  }
  ```

### 6. JSON数据展示页面
- **URL**：`/datapost/json/`
- **方法**：GET
- **功能**：在网页上美观展示JSON格式的视频数据
- **页面功能**：
  - 复制JSON数据按钮
  - 下载JSON文件链接
  - 返回数据列表链接

### 7. 纯JSON数据接口
- **URL**：`/datapost/api/`
- **方法**：GET
- **功能**：返回纯JSON格式的视频列表数据，适用于API调用
- **返回示例**：
  ```json
  {
    "total_videos": 5,
    "export_time": "2024-01-01T12:00:00.000000",
    "videos": [
      "https://example.com/video1.mp4",
      "https://example.com/video2.mp4"
    ]
  }
  ```

### 8. 视频文本数据接口

- **视频文本上传接口**
  - **URL**：`/datapost/video-text/`
  - **方法**：POST
  - **功能**：接收视频URL和对应的文本内容
  - **请求体**：JSON格式，包含video_url和text_content字段
  - **示例**：
    ```json
    {
      "video_url": "https://example.com/video1.mp4",
      "text_content": "这是视频的文本内容"
    }
    ```
  - **返回**：
    ```json
    {
      "status": "success",
      "message": "视频文本数据已保存"
    }
    ```

- **视频文本展示页面**
  - **URL**：`/datapost/video-text/show/`
  - **方法**：GET
  - **功能**：展示所有视频文本数据，包括视频播放器和对应文本内容
  - **页面功能**：
    - 复制文本内容按钮
    - 删除单条数据按钮
    - 清空所有数据按钮
    - 导出数据按钮
    - 创建时间戳文件按钮
    - API接口链接

- **视频文本删除接口**
  - **URL**：`/datapost/video-text/delete/`
  - **方法**：POST
  - **功能**：删除指定ID的视频文本数据
  - **请求体**：JSON，包含要删除数据的id
    ```json
    {"id": 1}
    ```
  - **返回**：
    ```json
    {"status": "success", "message": "id=1 已删除"}
    ```

- **视频文本清空接口**
  - **URL**：`/datapost/video-text/clear/`
  - **方法**：POST
  - **功能**：清空所有视频文本数据
  - **返回**：
    ```json
    {
      "status": "success", 
      "message": "所有视频文本数据已清除，共删除 X 条记录"
    }
    ```

- **视频文本导出接口**
  - **URL**：`/datapost/video-text/export/`
  - **方法**：GET
  - **功能**：导出所有视频文本数据为JSON文件
  - **返回**：JSON文件下载（文件名：video_text_export.json）
  - **数据格式**：
    ```json
    {
      "total": 5,
      "export_time": "2024-01-01T12:00:00.000000",
      "items": [
        {
          "video_url": "https://example.com/video1.mp4",
          "text_content": "这是视频1的文本内容",
          "created_at": "2024-01-01T12:00:00.000000"
        },
        {
          "video_url": "https://example.com/video2.mp4",
          "text_content": "这是视频2的文本内容",
          "created_at": "2024-01-01T12:00:00.000000"
        }
      ]
    }
    ```

- **视频文本API接口**
  - **URL**：`/datapost/video-text/api/`
  - **方法**：GET
  - **功能**：返回视频文本数据的JSON格式，支持分页
  - **参数**：
    - `page`：页码，默认为1
    - `page_size`：每页条数，默认为50，最大为200
  - **返回示例**：
    ```json
    {
      "status": "success",
      "total_count": 10,
      "page": 1,
      "page_size": 50,
      "total_pages": 1,
      "has_next": false,
      "has_previous": false,
      "items": [
        {
          "id": 1,
          "video_url": "https://example.com/video1.mp4",
          "text_content": "这是视频1的文本内容",
          "created_at": "2024-01-01T12:00:00.000000"
        }
      ]
    }
    ```

- **创建时间戳文件接口**
  - **URL**：`/datapost/create-timestamp-file/`
  - **方法**：POST
  - **功能**：在服务器当前目录创建或更新一个包含时间戳的文件
  - **返回**：
    ```json
    {
      "status": "success",
      "message": "已更新文件: timestamp.txt",
      "file_path": "/path/to/timestamp.txt",
      "timestamp": 1625097600
    }
    ```

## 管理后台
- **URL**：`/admin/`
- **说明**：可在Django后台管理所有数据（需创建超级用户）

## 部署说明

1. **安装依赖**
   ```bash
   pip install django
   ```

2. **初始化数据库**
   ```bash
   python3 manage.py makemigrations
   python3 manage.py migrate
   ```

3. **创建超级用户（可选，用于后台管理）**
   ```bash
   python3 manage.py createsuperuser
   ```

4. **启动服务**
   ```bash
   python3 manage.py runserver
   ```
   默认访问地址：http://127.0.0.1:8000/

5. **接口测试示例**
   - 上传数据：
     ```bash
     curl -X POST http://127.0.0.1:8000/datapost/ -d '{"videos": ["https://example.com/video1.mp4"]}' -H "Content-Type: application/json"
     ```
   - 上传视频文本数据：
     ```bash
     curl -X POST http://127.0.0.1:8000/datapost/video-text/ -d '{"video_url": "https://example.com/video1.mp4", "text_content": "这是视频的文本内容"}' -H "Content-Type: application/json"
     ```
   - 清空数据：
     ```bash
     curl -X POST http://127.0.0.1:8000/datapost/clear/
     ```
   - 删除单条：
     ```bash
     curl -X POST http://127.0.0.1:8000/datapost/delete/ -d '{"id": 1}' -H "Content-Type: application/json"
     ```
   - 获取纯JSON数据：
     ```bash
     curl http://127.0.0.1:8000/datapost/api/
     ```
   - 下载JSON文件：
     ```bash
     curl -O -J -L http://127.0.0.1:8000/datapost/export/
     ```

## 目录结构简述

- `backend/`         Django主项目目录
- `datapost/`        业务app，包含模型、视图、路由
- `manage.py`        Django管理脚本
- `download_videos.py` 视频下载工具脚本
- `upload_video_text.py` 视频文本上传工具脚本
- `config.json`      配置文件，包含API地址等设置

## 配置文件

项目使用`config.json`文件存储配置信息，主要包括：

```json
{
  "API_ENDPOINT": "https://aliyun.ideapool.club/datapost/api/",
  "LOCAL_API_ENDPOINT": "http://127.0.0.1:8000/datapost/api/",
  "VIDEO_TEXT_API_ENDPOINT": "https://aliyun.ideapool.club/datapost/video-text/",
  "LOCAL_VIDEO_TEXT_API_ENDPOINT": "http://127.0.0.1:8000/datapost/video-text/",
  "OUTPUT_DIR": "downloaded_videos",
  "DB_PATH": "db.sqlite3",
  "OUTPUT_TXT": "output_videos.txt"
}
```

可以根据需要修改配置文件中的值，程序会自动加载这些设置。

### 切换API地址

如果需要在本地开发环境和生产环境之间切换API地址，可以：

1. 直接修改`config.json`文件中的相应配置项
2. 使用命令行参数临时指定API地址

## 视频下载工具

项目提供了一个 `download_videos.py` 脚本，用于从不同来源获取视频链接并下载视频：

### 功能选项

1. **从数据库导出数据**
   ```bash
   python download_videos.py --export
   ```

2. **从数据库导出视频链接**
   ```bash
   python download_videos.py --export-links
   ```

3. **从文本文件下载视频**
   ```bash
   python download_videos.py --download --input video_links.txt
   ```

4. **从JSON文件下载视频**
   ```bash
   python download_videos.py --json video_list_export.json
   ```

5. **从API接口下载视频**
   ```bash
   python download_videos.py --api
   ```
   
   自定义API地址：
   ```bash
   python download_videos.py --api --api-url http://example.com/datapost/api/
   ```

6. **从API接口获取数据并保存到本地**
   ```bash
   python download_videos.py --api --save-json
   ```
   此命令会同时保存完整JSON数据和提取的视频列表到本地文件，并下载视频。

7. **仅保存API数据而不下载视频**
   ```bash
   python download_videos.py --api --only-save
   ```
   此命令会保存完整JSON数据和提取的视频列表到本地文件，但不会下载视频。

8. **保存下载映射关系**
   ```bash
   python download_videos.py --api --mapping download_map.txt
   ```
   此命令会在下载视频的同时，将视频URL、保存路径和下载状态以`url \t path \t 是否下载成功`的格式保存到指定文件。
   
   也可与其他命令组合使用：
   ```bash
   python download_videos.py --json video_list.json --mapping download_map.txt
   ```

## 视频文本上传工具

项目提供了 `upload_video_text.py` 脚本，用于上传视频URL和对应的文本内容。该脚本支持特定格式的文件，其中第一行是视频URL，后续行是文本内容。

### 功能选项

1. **上传单个文件**
   ```bash
   python upload_video_text.py --file video_text_file.txt
   ```
   
   文件格式示例：
   ```
   https://example.com/video1.mp4
   这是视频的文本内容，
   可以包含多行文本。
   这些文本将作为一个整体发送到服务器。
   ```

2. **处理整个目录中的文件**
   ```bash
   python upload_video_text.py --dir ./video_text_files/
   ```
   此命令会处理指定目录中的所有文件，每个文件的格式应与上述示例相同。

3. **使用远程API端点（默认）**
   ```bash
   python upload_video_text.py --api --file video_text_file.txt
   ```
   使用配置文件中的 `VIDEO_TEXT_API_ENDPOINT` 值作为API端点。

4. **使用本地API端点**
   ```bash
   python upload_video_text.py --local --file video_text_file.txt
   ```
   使用配置文件中的 `LOCAL_VIDEO_TEXT_API_ENDPOINT` 值作为API端点。

5. **手动指定API端点**
   ```bash
   python upload_video_text.py --url http://example.com/datapost/video-text/ --file video_text_file.txt
   ```

6. **设置请求间隔时间**
   ```bash
   python upload_video_text.py --dir ./video_text_files/ --delay 1.0
   ```
   处理多个文件时，每次请求之间的延迟时间（秒），默认为0.5秒。

### 配置文件集成

`upload_video_text.py` 脚本会自动从 `config.json` 文件中读取配置：

- `VIDEO_TEXT_API_ENDPOINT`：远程API端点地址（默认使用）
- `LOCAL_VIDEO_TEXT_API_ENDPOINT`：本地API端点地址（使用 `--local` 参数时）

## 其它说明
- 支持任意格式数据存储，推荐JSON格式，页面会自动解析`videos`字段。
- 如需扩展其它字段或功能，请修改`datapost/models.py`和相关视图。

## 语音转文字功能

项目提供了 `video_audio2txt/auto2text.py` 脚本，用于将音频文件转换为文本。该脚本使用Vosk语音识别引擎，根据系统平台自动选择合适的模型。

### 安装依赖

```bash
pip install vosk
pip install ffmpeg-python
```

### 使用方法

1. **基本用法**
   ```bash
   python video_audio2txt/auto2text.py -i audio.mp3
   ```
   此命令会将音频文件转换为文本，并将结果保存在 `transcriptions` 目录下。

2. **指定输出目录**
   ```bash
   python video_audio2txt/auto2text.py -i audio.mp3 -o my_transcriptions
   ```

3. **手动指定模型**
   ```bash
   python video_audio2txt/auto2text.py -i audio.mp3 -m ./models/my-custom-model
   ```

4. **强制使用小模型**
   ```bash
   python video_audio2txt/auto2text.py -i audio.mp3 --force-small
   ```

5. **强制使用大模型**
   ```bash
   python video_audio2txt/auto2text.py -i audio.mp3 --force-large
   ```

### 配置文件集成

`auto2text.py` 脚本会自动从 `config.json` 文件中读取配置：

- `VOSK_SMALL_MODEL_PATH`：小型语音识别模型路径（Linux系统默认使用）
- `VOSK_LARGE_MODEL_PATH`：大型语音识别模型路径（非Linux系统默认使用）

### 平台自适应

脚本会根据运行平台自动选择合适的模型：
- Linux系统：默认使用小型模型（资源占用较少）
- 其他系统（Windows、macOS等）：默认使用大型模型（识别效果更好）

可以通过 `--force-small` 或 `--force-large` 参数强制指定使用的模型类型。

---
如有问题或定制需求，请联系开发者。
