#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Voice数据处理器
功能：
1. 通过接口获取voice数据
2. 解析并打印voice、outfile、content内容
3. 处理完成后清空所有数据
"""

import requests
import json
import sys

BASE_URL = "http://127.0.0.1:8000/datapost"

def get_voice_data():
    """获取所有voice数据"""
    print("正在获取voice数据...")
    
    try:
        url = f"{BASE_URL}/voice/list/"
        response = requests.get(url)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('status') == 'success':
                return result.get('items', [])
            else:
                print(f"获取数据失败: {result.get('message')}")
                return []
        else:
            print(f"请求失败，状态码: {response.status_code}")
            return []
            
    except Exception as e:
        print(f"获取数据异常: {e}")
        return []

def parse_and_print_data(data_list):
    """解析并打印voice数据"""
    if not data_list:
        print("没有找到任何数据")
        return
    
    print(f"\n找到 {len(data_list)} 条数据:")
    print("=" * 80)
    
    for i, item in enumerate(data_list, 1):
        print(f"\n【数据 {i}】")
        print(f"ID: {item.get('id')}")
        print(f"创建时间: {item.get('created_at')}")
        print("-" * 40)
        
        # 解析voice内容
        voice = item.get('voice', '')
        print(f"Voice内容: {voice}")
        
        # 解析outfile内容
        outfile = item.get('outfile', '')
        print(f"输出文件: {outfile}")
        
        # 解析content内容
        content = item.get('content', '')
        print(f"文本内容: {content}")
        
        print("-" * 40)

def clear_all_data():
    """清空所有voice数据"""
    print("\n开始清空数据...")
    
    try:
        url = f"{BASE_URL}/voice/clear/"
        response = requests.get(url)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('status') == 'success':
                print(f"✅ {result.get('message')}")
                return True
            else:
                print(f"❌ 清空失败: {result.get('message')}")
                return False
        else:
            print(f"❌ 清空请求失败，状态码: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 清空数据异常: {e}")
        return False

def verify_clear():
    """验证数据是否已清空"""
    print("\n验证清空结果...")
    
    data_list = get_voice_data()
    if not data_list:
        print("✅ 数据已成功清空")
    else:
        print(f"⚠️  仍有 {len(data_list)} 条数据未清空")

def main():
    """主处理函数"""
    print("Voice数据处理器启动")
    print("=" * 50)
    
    # 1. 获取数据
    data_list = get_voice_data()
    
    # 2. 解析并打印数据
    parse_and_print_data(data_list)
    
    # 3. 如果有数据，询问是否清空
    if data_list:
        print("\n" + "=" * 50)
        user_input = input("是否要清空所有数据？(y/n): ").strip().lower()
        
        if user_input in ['y', 'yes', '是']:
            # 4. 清空数据
            if clear_all_data():
                # 5. 验证清空结果
                verify_clear()
        else:
            print("已取消清空操作")
    
    print("\n处理完成！")

if __name__ == "__main__":
    main()