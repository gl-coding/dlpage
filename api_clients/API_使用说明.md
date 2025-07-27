# 文章管理系统 JSON API 使用说明

## 概述

本文档介绍了文章管理系统提供的JSON API接口，主要包括获取文章列表和更新文章信息两个功能。

## API 接口列表

### 1. 获取所有文章信息列表

**接口地址：** `GET /datapost/article/api/json/`

**功能描述：** 获取所有文章信息的JSON列表，支持分页、筛选和搜索功能。

#### 请求参数（查询参数）

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| page | int | 否 | 1 | 页码，从1开始 |
| page_size | int | 否 | 10 | 每页显示数量 |
| type | string | 否 | - | 按文章类型筛选 |
| is_read | string | 否 | - | 已读状态筛选（true/false） |
| search | string | 否 | - | 搜索关键词（搜索标题、内容、备注） |

#### 请求示例

```bash
# 获取第一页文章（默认10条）
GET /datapost/article/api/json/

# 获取第2页，每页5条文章
GET /datapost/article/api/json/?page=2&page_size=5

# 筛选技术分享类型的文章
GET /datapost/article/api/json/?type=技术分享

# 搜索包含"Django"的文章
GET /datapost/article/api/json/?search=Django

# 组合查询：已读的技术分享文章，每页20条
GET /datapost/article/api/json/?type=技术分享&is_read=true&page_size=20
```

#### 响应格式

```json
{
    "status": "success",
    "data": {
        "articles": [
            {
                "id": 1,
                "title": "Django REST API 开发指南",
                "content": "本文介绍了如何使用Django开发REST API...",
                "article_type": "技术分享",
                "audio_url": "https://example.com/audio.mp3",
                "video_url": "https://www.youtube.com/watch?v=abc123",
                "remarks": "这是一篇很有用的技术文章",
                "is_read": false,
                "created_at": "2024-01-15 10:30:00",
                "updated_at": "2024-01-15 15:45:00"
            }
        ],
        "pagination": {
            "current_page": 1,
            "page_size": 10,
            "total_count": 25,
            "total_pages": 3,
            "has_next": true,
            "has_prev": false
        }
    }
}
```

### 2. 删除所有已读文章

**接口地址：** `POST /datapost/article/api/delete-all-read/`

**功能描述：** 批量删除所有标记为已读的文章，用于清理已处理的文章。

#### 请求示例

```bash
POST /datapost/article/api/delete-all-read/
Content-Type: application/json
```

#### 响应格式

##### 成功删除

```json
{
    "status": "success",
    "message": "成功删除 5 篇已读文章",
    "deleted_count": 5
}
```

##### 没有已读文章

```json
{
    "status": "warning",
    "message": "没有找到已读文章，无需删除"
}
```

### 3. 更新/获取单个文章信息

**接口地址：** 
- `PUT /datapost/article/api/json/<article_id>/` - 更新文章
- `GET /datapost/article/api/json/<article_id>/` - 获取单个文章信息

#### 3.1 更新文章信息 (PUT)

**功能描述：** 更新指定ID的文章信息，支持部分字段更新。

##### 请求体参数

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| title | string | 否 | 文章标题 |
| content | string | 否 | 文章内容 |
| article_type | string | 否 | 文章类型 |
| audio_url | string | 否 | 音频链接 |
| video_url | string | 否 | 视频链接 |
| remarks | string | 否 | 备注 |
| is_read | boolean | 否 | 是否已读 |

##### 请求示例

```bash
# 更新文章标题和已读状态
PUT /datapost/article/api/json/1/
Content-Type: application/json

{
    "title": "Django REST API 开发完整指南",
    "is_read": true
}

# 添加音频和视频链接
PUT /datapost/article/api/json/1/
Content-Type: application/json

{
    "audio_url": "https://example.com/new-audio.mp3",
    "video_url": "https://www.bilibili.com/video/BV123456",
    "remarks": "添加了音频朗读和视频演示"
}

# 完整更新所有字段
PUT /datapost/article/api/json/1/
Content-Type: application/json

{
    "title": "全新的文章标题",
    "content": "完全重写的文章内容...",
    "article_type": "教程指南",
    "audio_url": "https://example.com/audio.mp3",
    "video_url": "https://example.com/video.mp4",
    "remarks": "这是完整的更新示例",
    "is_read": false
}
```

##### 响应格式

```json
{
    "status": "success",
    "message": "文章更新成功",
    "data": {
        "id": 1,
        "title": "Django REST API 开发完整指南",
        "content": "本文介绍了如何使用Django开发REST API...",
        "article_type": "技术分享",
        "audio_url": "https://example.com/new-audio.mp3",
        "video_url": "https://www.bilibili.com/video/BV123456",
        "remarks": "添加了音频朗读和视频演示",
        "is_read": true,
        "created_at": "2024-01-15 10:30:00",
        "updated_at": "2024-01-15 16:20:00"
    }
}
```

#### 3.2 获取单个文章信息 (GET)

**功能描述：** 获取指定ID的文章详细信息。

##### 请求示例

```bash
GET /datapost/article/api/json/1/
```

##### 响应格式

```json
{
    "status": "success",
    "data": {
        "id": 1,
        "title": "Django REST API 开发指南",
        "content": "本文介绍了如何使用Django开发REST API...",
        "article_type": "技术分享",
        "audio_url": "https://example.com/audio.mp3",
        "video_url": "https://www.youtube.com/watch?v=abc123",
        "remarks": "这是一篇很有用的技术文章",
        "is_read": false,
        "created_at": "2024-01-15 10:30:00",
        "updated_at": "2024-01-15 15:45:00"
    }
}
```

## 错误响应格式

当请求发生错误时，API会返回以下格式的错误信息：

```json
{
    "status": "error",
    "message": "错误描述信息"
}
```

### 常见错误代码

| HTTP状态码 | 错误说明 |
|-----------|----------|
| 400 | 请求参数错误 |
| 404 | 文章不存在 |
| 405 | 请求方法不允许 |
| 500 | 服务器内部错误 |

## 使用示例

### Python 示例

```python
import requests
import json

# 基础URL
BASE_URL = "http://localhost:8000/datapost/article/api/json/"

# 1. 获取文章列表
def get_articles():
    response = requests.get(BASE_URL)
    return response.json()

# 2. 搜索文章
def search_articles(keyword):
    params = {'search': keyword, 'page_size': 20}
    response = requests.get(BASE_URL, params=params)
    return response.json()

# 3. 获取单个文章
def get_article(article_id):
    response = requests.get(f"{BASE_URL}{article_id}/")
    return response.json()

# 4. 更新文章
def update_article(article_id, data):
    headers = {'Content-Type': 'application/json'}
    response = requests.put(f"{BASE_URL}{article_id}/", 
                          data=json.dumps(data), headers=headers)
    return response.json()

# 5. 删除所有已读文章
def delete_all_read_articles():
    response = requests.post("http://localhost:8000/datapost/article/api/delete-all-read/",
                           headers={'Content-Type': 'application/json'})
    return response.json()

# 使用示例
if __name__ == "__main__":
    # 获取所有文章
    articles = get_articles()
    print("文章总数:", articles['data']['pagination']['total_count'])
    
    # 搜索包含"Django"的文章
    search_results = search_articles("Django")
    print("搜索结果:", len(search_results['data']['articles']))
    
    # 更新文章状态
    update_data = {"is_read": True, "remarks": "已经仔细阅读过了"}
    result = update_article(1, update_data)
    print("更新结果:", result['message'])
    
    # 删除所有已读文章
    delete_result = delete_all_read_articles()
    print("删除结果:", delete_result['message'])
```

### JavaScript 示例

```javascript
const BASE_URL = "http://localhost:8000/datapost/article/api/json/";

// 1. 获取文章列表
async function getArticles(page = 1, pageSize = 10) {
    const url = `${BASE_URL}?page=${page}&page_size=${pageSize}`;
    const response = await fetch(url);
    return response.json();
}

// 2. 更新文章
async function updateArticle(articleId, data) {
    const response = await fetch(`${BASE_URL}${articleId}/`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data)
    });
    return response.json();
}

// 3. 筛选已读文章
async function getReadArticles() {
    const url = `${BASE_URL}?is_read=true`;
    const response = await fetch(url);
    return response.json();
}

// 4. 删除所有已读文章
async function deleteAllReadArticles() {
    const response = await fetch('http://localhost:8000/datapost/article/api/delete-all-read/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        }
    });
    return response.json();
}

// 使用示例
getArticles().then(data => {
    console.log('文章列表:', data.data.articles);
});

// 标记文章为已读
updateArticle(1, { is_read: true }).then(result => {
    console.log('更新成功:', result.message);
});

// 删除所有已读文章
deleteAllReadArticles().then(result => {
    console.log('删除结果:', result.message);
});
```

## 注意事项

1. **CSRF保护**: 这些API接口已经添加了`@csrf_exempt`装饰器，无需CSRF令牌。

2. **数据验证**: 
   - 必填字段：title, content, article_type 在更新时如果提供则不能为空
   - URL字段会自动验证格式
   - 所有字符串字段会自动去除首尾空白

3. **分页**: 建议使用分页来避免一次性获取过多数据，默认每页10条记录。

4. **搜索功能**: 搜索会在文章标题、内容和备注中查找，不区分大小写。

5. **时间格式**: 所有时间字段返回格式为 "YYYY-MM-DD HH:MM:SS"。

6. **部分更新**: PUT请求支持部分字段更新，只需要传递需要更新的字段即可。 