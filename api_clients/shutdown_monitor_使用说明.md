# Shutdown 监控脚本使用说明

## 概述
`shutdown_monitor.py` 是一个自动监控脚本，用于监控 shutdown 接口。当接口中有数据时，会自动创建本地 shutdown 文件并清除接口数据。

## 功能特性

### 🔍 **自动监控**
- 定期检查 shutdown 接口
- 发现数据时自动处理
- 支持自定义检查间隔

### 📁 **文件管理**
- 启动时自动清理旧文件
- 自动创建本地 shutdown 文件
- 备份旧文件（可选）
- 自动清理过多备份文件

### 📝 **日志记录**
- 详细的操作日志
- 支持文件和控制台输出
- 可配置日志级别

### ⚙️ **配置灵活**
- 支持 JSON 配置文件
- 可自定义各种参数
- 默认配置兜底

## 安装和运行

### 1. 安装依赖
```bash
pip install requests
```

### 2. 运行脚本
```bash
python shutdown_monitor.py
```

### 3. 后台运行
```bash
nohup python shutdown_monitor.py > monitor.log 2>&1 &
```

## 配置文件

### 默认配置
```json
{
    "base_url": "http://localhost:8000/datapost",
    "check_interval": 5,
    "shutdown_file": "shutdown.txt",
    "log_file": "shutdown_monitor.log",
    "enable_logging": true,
    "backup_old_files": true,
    "max_backup_files": 10
}
```

### 配置说明
| 参数 | 说明 | 默认值 |
|------|------|--------|
| `base_url` | Django 服务地址 | `http://localhost:8000/datapost` |
| `check_interval` | 检查间隔（秒） | `5` |
| `shutdown_file` | 本地 shutdown 文件名 | `shutdown.txt` |
| `log_file` | 日志文件名 | `shutdown_monitor.log` |
| `enable_logging` | 是否启用日志 | `true` |
| `backup_old_files` | 是否备份旧文件 | `true` |
| `max_backup_files` | 最大备份文件数 | `10` |

## 工作流程

### 1. 启动监控
```
🚀 启动 Shutdown 接口监控
🗑️  已删除旧文件: shutdown.txt
🗑️  已删除旧日志: shutdown_monitor.log
✅ 启动清理完成
📡 监控地址: http://localhost:8000/datapost/shutdown/list/
📁 本地文件: shutdown.txt
⏰ 检查间隔: 5 秒
```

### 2. 检查数据
```
🔍 检查时间: 2024-01-01 12:00:00
📭 暂无关机命令
⏳ 等待 5 秒后再次检查...
```

### 3. 发现数据
```
🔍 检查时间: 2024-01-01 12:00:05
📋 发现 2 条关机命令:
   - ID 1: shutdown -h now
   - ID 2: systemctl poweroff
📦 已备份旧文件: shutdown.txt.20240101_120005
✅ 已创建本地文件: shutdown.txt
✅ 已清空接口数据: 已清空所有 2 条命令
✅ 处理完成！
```

## 生成的文件

### shutdown.txt 示例
```
# Shutdown 命令文件
# 生成时间: 2024-01-01 12:00:05
# 命令数量: 2
==================================================

# 命令 1
# ID: 1
# 创建时间: 2024-01-01T12:00:00Z
shutdown -h now

# 命令 2
# ID: 2
# 创建时间: 2024-01-01T12:00:03Z
systemctl poweroff
```

### 备份文件
- 格式：`shutdown.txt.YYYYMMDD_HHMMSS`
- 自动清理：保留最新的 10 个备份文件

## 日志文件

### shutdown_monitor.log 示例
```
2024-01-01 12:00:00,123 - INFO - 🚀 启动 Shutdown 接口监控
2024-01-01 12:00:00,124 - INFO - 📡 监控地址: http://localhost:8000/datapost/shutdown/list/
2024-01-01 12:00:00,125 - INFO - 📁 本地文件: shutdown.txt
2024-01-01 12:00:00,126 - INFO - ⏰ 检查间隔: 5 秒
2024-01-01 12:00:00,127 - INFO - 📝 日志文件: shutdown_monitor.log
2024-01-01 12:00:00,128 - INFO - ==================================================
2024-01-01 12:00:00,129 - INFO - 🔍 检查时间: 2024-01-01 12:00:00
2024-01-01 12:00:00,130 - INFO - 📭 暂无关机命令
```

## 错误处理

### 常见错误
1. **网络连接失败**
   - 检查 Django 服务是否运行
   - 确认 `base_url` 配置正确

2. **权限错误**
   - 确保有写入文件的权限
   - 检查目录是否存在

3. **配置文件错误**
   - 检查 JSON 格式是否正确
   - 使用默认配置作为兜底

### 错误日志示例
```
2024-01-01 12:00:00,123 - ERROR - 获取关机命令失败: Connection refused
2024-01-01 12:00:00,124 - ERROR - 创建shutdown文件失败: Permission denied
```

## 停止监控

### 方法 1：Ctrl+C
```bash
# 在运行脚本的终端按 Ctrl+C
🛑 监控已停止
```

### 方法 2：杀死进程
```bash
# 查找进程 ID
ps aux | grep shutdown_monitor.py

# 杀死进程
kill <进程ID>
```

## 高级用法

### 自定义配置文件
```bash
# 创建自定义配置
cp shutdown_monitor_config.json my_config.json
# 编辑 my_config.json

# 使用自定义配置运行
python shutdown_monitor.py my_config.json
```

### 修改检查间隔
```json
{
    "check_interval": 10,
    "shutdown_file": "my_shutdown.txt"
}
```

### 禁用日志
```json
{
    "enable_logging": false
}
```

### 禁用备份
```json
{
    "backup_old_files": false
}
```

## 注意事项

1. **启动时清理**
   - 每次启动会自动删除旧的 shutdown.txt 和日志文件
   - 确保脚本有删除文件的权限

2. **确保 Django 服务运行**
   - 脚本需要访问 Django 的 shutdown 接口
   - 检查服务地址和端口

3. **文件权限**
   - 确保脚本有创建、写入和删除文件的权限
   - 检查目录是否存在

3. **网络连接**
   - 确保网络连接稳定
   - 考虑网络超时设置

4. **资源使用**
   - 监控脚本会持续运行
   - 注意 CPU 和内存使用

5. **数据安全**
   - 备份文件包含敏感信息
   - 注意文件权限设置 