#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import json
import argparse
import sys
import os
import time

# 配置文件默认路径
DEFAULT_CONFIG_FILE = 'config.json'

# 加载配置文件
def load_config(config_path=DEFAULT_CONFIG_FILE):
    config = {}
    try:
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            print(f'已从 {config_path} 加载配置')
        else:
            print(f'警告：配置文件 {config_path} 不存在，将使用默认配置')
    except Exception as e:
        print(f'加载配置文件出错: {e}，将使用默认配置')
    
    return config

# 获取命令行参数中的配置文件路径
def get_config_path():
    # 创建一个临时的参数解析器，只用于提取配置文件路径
    temp_parser = argparse.ArgumentParser(add_help=False)
    temp_parser.add_argument('--config', type=str, default=DEFAULT_CONFIG_FILE,
                        help=f'指定配置文件路径 (默认: {DEFAULT_CONFIG_FILE})')
    # 解析已知参数，忽略未知参数
    temp_args, _ = temp_parser.parse_known_args()
    return temp_args.config

# 获取配置文件路径并加载配置
config_path = get_config_path()
config = load_config(config_path)

# 设置默认值和从配置文件加载的值
DEFAULT_API_URL = 'http://127.0.0.1:8000/datapost/video-text/'
# 优先使用VIDEO_TEXT_API_ENDPOINT配置项
VIDEO_TEXT_API = config.get('VIDEO_TEXT_API_ENDPOINT', DEFAULT_API_URL)
LOCAL_VIDEO_TEXT_API = config.get('LOCAL_VIDEO_TEXT_API_ENDPOINT', DEFAULT_API_URL)

def post_video_text(api_url, video_url, text_content):
    """
    向服务器发送视频URL和对应的文本内容
    
    Args:
        api_url: API端点URL，例如 http://127.0.0.1:8000/datapost/video-text/
        video_url: 视频的URL
        text_content: 视频对应的文本内容
    
    Returns:
        (success, result) 元组
    """
    # 准备请求数据
    payload = {
        "video_url": video_url,
        "text_content": text_content
    }
    
    # 设置请求头
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        # 发送POST请求
        response = requests.post(
            api_url, 
            data=json.dumps(payload), 
            headers=headers
        )
        
        # 检查响应状态
        if response.status_code == 200:
            result = response.json()
            return True, result
        else:
            return False, response.text
    
    except Exception as e:
        return False, str(e)

def process_file(file_path):
    """
    处理特定格式的文件：第一行是URL，后续行是文本内容
    
    Args:
        file_path: 文件路径
    
    Returns:
        (video_url, text_content) 元组，如果处理失败则返回 (None, None)
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        if not lines:
            print(f"错误: 文件 {file_path} 为空")
            return None, None
        
        # 第一行是URL
        video_url = lines[0].strip()
        if not video_url:
            print(f"错误: 文件 {file_path} 第一行不包含URL")
            return None, None
        
        # 从第二行到末尾是文本内容
        text_content = ''.join(lines[1:])
        
        return video_url, text_content
        
    except Exception as e:
        print(f"处理文件 {file_path} 时出错: {e}")
        return None, None

def process_directory(dir_path, api_url, delay=0.5):
    """
    处理目录中的所有文件
    
    Args:
        dir_path: 目录路径
        api_url: API端点URL
        delay: 请求间隔时间(秒)
    
    Returns:
        (success_count, fail_count) 元组
    """
    if not os.path.isdir(dir_path):
        print(f"错误: {dir_path} 不是有效的目录")
        return 0, 0
    
    files = [f for f in os.listdir(dir_path) if os.path.isfile(os.path.join(dir_path, f))]
    if not files:
        print(f"警告: 目录 {dir_path} 中没有找到文件")
        return 0, 0
    
    success_count = 0
    fail_count = 0
    
    for i, file_name in enumerate(files):
        file_path = os.path.join(dir_path, file_name)
        print(f"[{i+1}/{len(files)}] 处理文件: {file_name}")
        
        video_url, text_content = process_file(file_path)
        if video_url:
            print(f"  URL: {video_url[:50]}...")
            print(f"  文本长度: {len(text_content)} 字符")
            
            success, result = post_video_text(api_url, video_url, text_content)
            
            if success:
                success_count += 1
                print(f"  上传成功: {result}")
            else:
                fail_count += 1
                print(f"  上传失败: {result}")
        else:
            fail_count += 1
        
        # 添加延迟，避免请求过于频繁
        if i < len(files) - 1:  # 最后一个请求不需要延迟
            time.sleep(delay)
    
    return success_count, fail_count

def main():
    parser = argparse.ArgumentParser(description='上传视频URL和文本到服务器')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--api', action='store_true', default=True,
                       help='使用远程API端点 (VIDEO_TEXT_API_ENDPOINT，默认)')
    group.add_argument('--local', action='store_true',
                       help='使用本地API端点 (LOCAL_VIDEO_TEXT_API_ENDPOINT)')
    parser.add_argument('--file', type=str, help='单个文件路径，第一行是URL，后续行是文本内容')
    parser.add_argument('--dir', type=str, help='目录路径，处理目录中的所有文件')
    parser.add_argument('--delay', type=float, default=0.5, 
                        help='处理多个文件时，每次请求间隔的延迟时间(秒) (默认: 0.5)')
    parser.add_argument('--url', type=str, 
                        help='手动指定API端点URL，覆盖配置文件设置')
    parser.add_argument('--config', type=str, default=DEFAULT_CONFIG_FILE,
                        help=f'指定配置文件路径 (默认: {DEFAULT_CONFIG_FILE})')
    
    args = parser.parse_args()
    
    # 检查参数
    if not args.file and not args.dir:
        print("错误: 必须提供--file或--dir参数")
        sys.exit(1)
    
    if args.file and args.dir:
        print("警告: 同时提供了--file和--dir参数，将只处理--file")
    
    # 确定API端点
    api_url = args.url if args.url else (LOCAL_VIDEO_TEXT_API if args.local else VIDEO_TEXT_API)
    
    # 显示使用的API端点
    api_type = "本地" if args.local else "远程"
    print(f"使用{api_type}API端点: {api_url}")
    
    # 处理单个文件
    if args.file:
        print(f"处理文件: {args.file}")
        video_url, text_content = process_file(args.file)
        
        if video_url:
            print(f"URL: {video_url}")
            print(f"文本长度: {len(text_content)} 字符")
            
            success, result = post_video_text(api_url, video_url, text_content)
            
            if success:
                print(f"上传成功: {result}")
                sys.exit(0)
            else:
                print(f"上传失败: {result}")
                sys.exit(1)
        else:
            sys.exit(1)
    
    # 处理目录
    elif args.dir:
        print(f"处理目录: {args.dir}")
        success_count, fail_count = process_directory(args.dir, api_url, args.delay)
        
        print(f"\n处理完成: 成功 {success_count} 个文件，失败 {fail_count} 个文件")
        
        if fail_count > 0:
            sys.exit(1)
        else:
            sys.exit(0)

if __name__ == "__main__":
    main() 