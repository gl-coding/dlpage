# Shutdown API 接口文档

## 概述
Shutdown API 提供了关机命令的管理功能，包括提交命令、查询命令列表、删除单个命令和清空所有命令。

## 接口列表

### 1. 提交关机命令
**POST** `/datapost/shutdown/`

提交一个新的关机命令到系统。

#### 请求参数
```json
{
    "command": "shutdown -h now"
}
```

#### 响应示例
```json
{
    "status": "success",
    "message": "命令已提交",
    "data": {
        "id": 1,
        "command": "shutdown -h now",
        "created_at": "2024-01-01T12:00:00Z"
    }
}
```

### 2. 获取命令列表
**GET** `/datapost/shutdown/list/`

获取所有已提交的关机命令列表。

#### 响应示例
```json
{
    "status": "success",
    "message": "获取成功",
    "data": [
        {
            "id": 1,
            "command": "shutdown -h now",
            "created_at": "2024-01-01T12:00:00Z",
            "updated_at": "2024-01-01T12:00:00Z"
        },
        {
            "id": 2,
            "command": "systemctl poweroff",
            "created_at": "2024-01-01T12:05:00Z",
            "updated_at": "2024-01-01T12:05:00Z"
        }
    ],
    "count": 2
}
```

### 3. 删除单个命令
**POST** `/datapost/shutdown/delete/{command_id}/`

删除指定ID的关机命令。

#### 路径参数
- `command_id`: 命令ID（整数）

#### 响应示例
```json
{
    "status": "success",
    "message": "命令已删除: shutdown -h now"
}
```

### 4. 清空所有命令
**POST** `/datapost/shutdown/clear/`

删除所有关机命令。

#### 响应示例
```json
{
    "status": "success",
    "message": "已清空所有 3 条命令"
}
```

## 错误响应

### 缺少command字段
```json
{
    "status": "error",
    "message": "缺少command字段"
}
```

### JSON格式错误
```json
{
    "status": "error",
    "message": "JSON格式错误"
}
```

### 命令不存在
```json
{
    "status": "error",
    "message": "命令ID 999 不存在"
}
```

## 使用示例

### Python 示例
```python
import requests

# 提交命令
response = requests.post(
    "http://localhost:8000/datapost/shutdown/",
    json={"command": "shutdown -h now"}
)
print(response.json())

# 获取列表
response = requests.get("http://localhost:8000/datapost/shutdown/list/")
commands = response.json()
print(commands)

# 删除命令
if commands['data']:
    command_id = commands['data'][0]['id']
    response = requests.post(f"http://localhost:8000/datapost/shutdown/delete/{command_id}/")
    print(response.json())
```

### cURL 示例
```bash
# 提交命令
curl -X POST http://localhost:8000/datapost/shutdown/ \
  -H "Content-Type: application/json" \
  -d '{"command": "shutdown -h now"}'

# 获取列表
curl http://localhost:8000/datapost/shutdown/list/

# 删除命令
curl -X POST http://localhost:8000/datapost/shutdown/delete/1/
```

## 数据库模型

```python
class Shutdown(models.Model):
    command = models.CharField(max_length=500, verbose_name="命令")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")
```

## 注意事项

1. 所有接口都支持JSON格式的数据交换
2. 命令字段最大长度为500个字符
3. 命令按创建时间倒序排列
4. 删除操作不可恢复，请谨慎使用
5. 清空操作会删除所有命令，请确认后再执行 