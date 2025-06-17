# Django 数据接收与展示系统

## 功能说明

- 提供 POST 接口，接收并存储任意数据（如 JSON），支持批量视频链接。
- 提供数据展示页面，自动解析并展示视频列表。
- 支持一键清空所有数据。
- 支持单条数据删除。
- 管理后台可查看和管理所有数据。

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

## 其它说明
- 支持任意格式数据存储，推荐JSON格式，页面会自动解析`videos`字段。
- 如需扩展其它字段或功能，请修改`datapost/models.py`和相关视图。

---
如有问题或定制需求，请联系开发者。
