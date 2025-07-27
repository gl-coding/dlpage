#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文章管理API客户端脚本
功能：
1. 获取所有未读文章数据
2. 根据ID更新文章的各个字段数据

使用说明：
python article_manager.py
"""

import time, os, sys, json, requests, datetime
from typing import Dict, List, Optional, Any

# 全局配置
BASE_URL = "https://aliyun.ideapool.club/"


class ArticleManager:
    """文章管理API客户端"""
    
    def __init__(self, base_url: str = None):
        """
        初始化客户端
        
        Args:
            base_url: Django服务器基础URL，默认使用全局变量BASE_URL
        """
        self.base_url = (base_url or BASE_URL).rstrip('/')
        self.session = requests.Session()
        # 设置请求头
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'ArticleManager/1.0'
        })
    
    def get_unread_articles(self, page: int = 1, page_size: int = 50) -> Dict[str, Any]:
        """
        获取所有未读文章数据
        
        Args:
            page: 页码，默认第1页
            page_size: 每页数量，默认50条
            
        Returns:
            包含文章列表和分页信息的字典
        """
        try:
            url = f"{self.base_url}/api/datapost/article/api/json/"
            params = {
                'is_read': 'false',  # 只获取未读文章
                'page': page,
                'page_size': page_size
            }
            
            response = self.session.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('status') == 'success':
                return data['data']
            else:
                print(f"❌ 获取文章失败: {data.get('message', '未知错误')}")
                return {}
                
        except requests.exceptions.RequestException as e:
            print(f"❌ 网络请求错误: {e}")
            return {}
        except json.JSONDecodeError as e:
            print(f"❌ JSON解析错误: {e}")
            return {}
        except Exception as e:
            print(f"❌ 未知错误: {e}")
            return {}
    
    def update_article(self, article_id: int, update_data: Dict[str, Any]) -> bool:
        """
        根据ID更新文章的各个字段数据
        
        Args:
            article_id: 文章ID
            update_data: 要更新的字段数据
            
        Returns:
            更新是否成功
        """
        try:
            url = f"{self.base_url}/api/datapost/article/api/json/{article_id}/"
            
            response = self.session.put(url, data=json.dumps(update_data))
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('status') == 'success':
                return True
            else:
                print(f"❌ 更新失败: {data.get('message', '未知错误')}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"❌ 网络请求错误: {e}")
            return False
        except json.JSONDecodeError as e:
            print(f"❌ JSON解析错误: {e}")
            return False
        except Exception as e:
            print(f"❌ 未知错误: {e}")
            return False
    
    def get_article_by_id(self, article_id: int) -> Dict[str, Any]:
        """
        根据ID获取单篇文章详情
        
        Args:
            article_id: 文章ID
            
        Returns:
            文章详情字典
        """
        try:
            url = f"{self.base_url}/api/datapost/article/api/json/{article_id}/"
            
            response = self.session.get(url)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('status') == 'success':
                return data.get('data', {})
            else:
                print(f"❌ 获取文章失败: {data.get('message', '未知错误')}")
                return {}
                
        except requests.exceptions.RequestException as e:
            print(f"❌ 网络请求错误: {e}")
            return {}
        except json.JSONDecodeError as e:
            print(f"❌ JSON解析错误: {e}")
            return {}
        except Exception as e:
            print(f"❌ 未知错误: {e}")
            return {}


def write_articles_to_files(field_file_mapping: Dict[str, str], articles_data: List[Dict[str, Any]]):
    """
    根据传入的文章数据写入文件，不同字段写入不同文件
    
    Args:
        field_file_mapping: 字段到文件名的映射，格式: {'字段名': '文件名'}
                          特殊字段 'all' 将写入文章的全部内容
        articles_data: 文章数据列表
    
    Returns:
        bool: 写入是否成功
    """
    if not field_file_mapping:
        print("❌ 请指定要写入的字段和文件映射")
        return False
    
    if not articles_data:
        print("❌ 没有文章数据，跳过写入")
        return False
    
    print(f"📊 开始写入 {len(articles_data)} 篇文章")
    
    try:
        import os
        
        # 为每个字段写入对应的文件
        for field_name, file_name in field_file_mapping.items():
            print(f"📝 正在写入字段 '{field_name}' 到文件 '{file_name}'...")
            
            try:
                with open(file_name, 'w', encoding='utf-8') as f:
                    written_count = 0
                    
                    if field_name == 'all':
                        # 写入文章的全部内容
                        for article in articles_data:
                            f.write(f"文章ID: {article.get('id', 'N/A')}\n")
                            f.write(f"标题: {article.get('title', 'N/A')}\n")
                            f.write(f"类型: {article.get('article_type', 'N/A')}\n")
                            f.write(f"内容: {article.get('content', 'N/A')}\n")
                            f.write(f"音频链接: {article.get('audio_url', 'N/A')}\n")
                            f.write(f"视频链接: {article.get('video_url', 'N/A')}\n")
                            f.write(f"备注: {article.get('remarks', 'N/A')}\n")
                            f.write(f"已读状态: {'已读' if article.get('is_read') else '未读'}\n")
                            f.write(f"创建时间: {article.get('created_at', 'N/A')}\n")
                            f.write(f"更新时间: {article.get('updated_at', 'N/A')}\n")
                            f.write("-" * 80 + "\n")
                            written_count += 1
                    else:
                        # 写入指定字段内容
                        for article in articles_data:
                            field_value = article.get(field_name, '')
                            
                            if field_value:  # 只写入非空字段
                                if isinstance(field_value, str):
                                    f.write(field_value)
                                else:
                                    f.write(str(field_value))
                                
                                f.write("\n")
                                written_count += 1
                    
                    print(f"✅ 成功写入 {written_count} 条记录到 '{file_name}'")
                    
            except Exception as e:
                print(f"❌ 写入文件 '{file_name}' 失败: {e}")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ 处理失败: {e}")
        return False


def process_oldest_unread_article(base_dir):
    """
    获取时间戳最老的一篇未标记已读文章，打印文章id，
    根据文章id设置文章视频链接、备注、标记为已读
    """
    if not os.path.exists(base_dir):
        os.makedirs(base_dir)

    # 初始化管理器
    manager = ArticleManager()
    
    try:
        oldest_article = None
        oldest_time = None
        page = 1
        total_checked = 0
        
        while True:
            print("🔍 正在搜索最老的未读文章...")
            oldest_article = None
            while True:
                result = manager.get_unread_articles(page=page, page_size=50)
                if not result or not result.get('articles'):
                    print("没有找到未读文章，等待10秒后继续")
                    time.sleep(10)
                    continue
                
                articles = result['articles']
                total_checked += len(articles)
                print(f"📄 正在检查第{page}页，找到 {len(articles)} 篇文章")
                
                for article in articles:
                    created_time = article.get('created_at')
                    if created_time:
                        # 比较时间戳找到最老的
                        if oldest_time is None or created_time < oldest_time:
                            oldest_time = created_time
                            oldest_article = article
                
                # 检查是否还有下一页
                if not result['pagination']['has_next']:
                    break
                    
                page += 1
            
            print(f"📊 总共检查了 {total_checked} 篇未读文章")

            print(f"\n📍 找到最老的未读文章:")
            if oldest_article:
                article_id = oldest_article['id']
                print(f"   文章ID: {article_id}")
                print(f"   标题: {oldest_article.get('title', 'N/A')}")
                print(f"   类型: {oldest_article.get('article_type', 'N/A')}")
                print(f"   创建时间: {oldest_article.get('created_at', 'N/A')}")
                print(f"   当前状态: {'已读' if oldest_article.get('is_read') else '未读'}")

            print(f"文章内容写入本地文件：")
            field_mapping = {
                'title': os.path.join(base_dir, 'file_title.txt'),
                'content': os.path.join(base_dir, 'file_content.txt'),
                'all': os.path.join(base_dir, 'file_all.txt')
            }

            # 传入查询到的文章数据
            success = write_articles_to_files(field_mapping, [oldest_article])
            if success:
                print("文章内容写入本地文件成功")
                open(os.path.join(base_dir, 'finish.download'), 'w').close()
            else:
                print("文章内容写入本地文件失败")
                break

            # 等待视频生成完成
            while not os.path.exists(os.path.join(base_dir, 'finish.generate')):
                print("没有找到处理完成标志文文件，等待10秒后继续")
                time.sleep(10)
            
            #upd_dict = json.loads(open(os.path.join(base_dir, 'finish.generate'), 'r').read()) 

            # 准备更新数据
            current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            #update_data = upd_dict
            update_data = {
                'video_url': 'https://example.com/processed_video.mp4',
                'remarks': f'最老文章自动处理 - {current_time}',
                'is_read': True
            }
            
            print(f"\n🔄 准备更新数据:")
            print(f"   视频链接: {update_data['video_url']}")
            print(f"   备注: {update_data['remarks']}")
            print(f"   标记为已读: {update_data['is_read']}")
            
            # 执行更新
            print(f"\n📝 正在更新文章ID: {article_id}")
            success = manager.update_article(article_id, update_data)
            
            if success:
                print(f"✅ 文章 {article_id} 更新成功！")
                
                # 验证更新结果
                updated_article = manager.get_article_by_id(article_id)
                if updated_article:
                    print(f"\n📄 更新后状态:")
                    print(f"   视频链接: {updated_article.get('video_url', 'N/A')}")
                    print(f"   备注: {updated_article.get('remarks', 'N/A')}")
                    print(f"   已读状态: {'已读' if updated_article.get('is_read') else '未读'}")
                    print(f"   更新时间: {updated_article.get('updated_at', 'N/A')}")
            else:
                print(f"❌ 文章 {article_id} 更新失败")
        else:
            print("📭 没有找到未读文章")
    except Exception as e:
        print(f"❌ 处理失败: {e}")

if __name__ == "__main__":
    process_oldest_unread_article("test")