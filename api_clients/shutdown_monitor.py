#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Shutdown 接口监控脚本
监控 shutdown 接口，当有数据时创建本地 shutdown 文件并清除接口数据
"""

import requests
import json
import time
import os
import logging
import shutil
from datetime import datetime

# 默认配置
DEFAULT_CONFIG = {
    "base_url": "http://localhost:8000/datapost",
    "check_interval": 5,
    "shutdown_file": "shutdown.txt",
    "log_file": "shutdown_monitor.log",
    "enable_logging": True,
    "backup_old_files": True,
    "max_backup_files": 10
}

class ShutdownMonitor:
    def __init__(self, config_file="shutdown_monitor_config.json"):
        self.config = self.load_config(config_file)
        self.cleanup_on_startup()
        self.setup_logging()
    
    def load_config(self, config_file):
        """加载配置文件"""
        try:
            if os.path.exists(config_file):
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    # 合并默认配置
                    for key, value in DEFAULT_CONFIG.items():
                        if key not in config:
                            config[key] = value
                    return config
            else:
                print(f"⚠️  配置文件 {config_file} 不存在，使用默认配置")
                return DEFAULT_CONFIG
        except Exception as e:
            print(f"⚠️  加载配置文件失败: {e}，使用默认配置")
            return DEFAULT_CONFIG
    
    def cleanup_on_startup(self):
        """启动时清理文件"""
        try:
            # 删除 shutdown 文件
            shutdown_file = self.config['shutdown_file']
            if os.path.exists(shutdown_file):
                os.remove(shutdown_file)
                print(f"🗑️  已删除旧文件: {shutdown_file}")
            
            # 删除日志文件
            log_file = self.config.get('log_file', 'shutdown_monitor.log')
            if os.path.exists(log_file):
                os.remove(log_file)
                print(f"🗑️  已删除旧日志: {log_file}")
            
            print("✅ 启动清理完成")
            
        except Exception as e:
            print(f"⚠️  清理文件时出错: {e}")
    
    def setup_logging(self):
        """设置日志"""
        if self.config.get('enable_logging', True):
            logging.basicConfig(
                level=logging.INFO,
                format='%(asctime)s - %(levelname)s - %(message)s',
                handlers=[
                    logging.FileHandler(self.config['log_file'], encoding='utf-8'),
                    logging.StreamHandler()
                ]
            )
            self.logger = logging.getLogger(__name__)
        else:
            self.logger = None
    
    def log(self, message, level='info'):
        """记录日志"""
        if self.logger:
            if level == 'info':
                self.logger.info(message)
            elif level == 'warning':
                self.logger.warning(message)
            elif level == 'error':
                self.logger.error(message)
        print(message)
    
    def backup_old_file(self):
        """备份旧文件"""
        if not self.config.get('backup_old_files', True):
            return
        
        shutdown_file = self.config['shutdown_file']
        if os.path.exists(shutdown_file):
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"{shutdown_file}.{timestamp}"
            
            try:
                shutil.copy2(shutdown_file, backup_name)
                self.log(f"📦 已备份旧文件: {backup_name}")
                
                # 清理过多的备份文件
                self.cleanup_old_backups()
            except Exception as e:
                self.log(f"❌ 备份文件失败: {e}", 'error')
    
    def cleanup_old_backups(self):
        """清理旧的备份文件"""
        max_backups = self.config.get('max_backup_files', 10)
        shutdown_file = self.config['shutdown_file']
        
        try:
            # 获取所有备份文件
            backup_files = []
            for file in os.listdir('.'):
                if file.startswith(shutdown_file + '.') and file != shutdown_file:
                    backup_files.append(file)
            
            # 按修改时间排序
            backup_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
            
            # 删除多余的备份文件
            if len(backup_files) > max_backups:
                for old_file in backup_files[max_backups:]:
                    os.remove(old_file)
                    self.log(f"🗑️  删除旧备份: {old_file}")
        except Exception as e:
            self.log(f"❌ 清理备份文件失败: {e}", 'error')
    
    def get_shutdown_commands(self):
        """获取所有关机命令"""
        try:
            response = requests.get(f"{self.config['base_url']}/shutdown/list/")
            if response.status_code == 200:
                result = response.json()
                if result.get('status') == 'success':
                    return result.get('data', [])
            return []
        except Exception as e:
            self.log(f"获取关机命令失败: {e}", 'error')
            return []
    
    def clear_all_commands(self):
        """清空所有关机命令"""
        try:
            response = requests.post(f"{self.config['base_url']}/shutdown/clear/")
            if response.status_code == 200:
                result = response.json()
                if result.get('status') == 'success':
                    self.log(f"✅ 已清空接口数据: {result.get('message')}")
                    return True
            return False
        except Exception as e:
            self.log(f"清空命令失败: {e}", 'error')
            return False
    
    def create_shutdown_file(self, commands):
        """创建本地shutdown文件"""
        try:
            # 备份旧文件
            self.backup_old_file()
            
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            shutdown_file = self.config['shutdown_file']
            
            with open(shutdown_file, 'w', encoding='utf-8') as f:
                f.write(f"# Shutdown 命令文件\n")
                f.write(f"# 生成时间: {timestamp}\n")
                f.write(f"# 命令数量: {len(commands)}\n")
                f.write("=" * 50 + "\n\n")
                
                for i, cmd in enumerate(commands, 1):
                    f.write(f"# 命令 {i}\n")
                    f.write(f"# ID: {cmd['id']}\n")
                    f.write(f"# 创建时间: {cmd['created_at']}\n")
                    f.write(f"{cmd['command']}\n\n")
            
            self.log(f"✅ 已创建本地文件: {shutdown_file}")
            return True
        except Exception as e:
            self.log(f"创建shutdown文件失败: {e}", 'error')
            return False
    
    def check_and_process(self):
        """检查并处理关机命令"""
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.log(f"🔍 检查时间: {current_time}")
        
        # 获取所有命令
        commands = self.get_shutdown_commands()
        
        if commands:
            self.log(f"📋 发现 {len(commands)} 条关机命令:")
            for cmd in commands:
                self.log(f"   - ID {cmd['id']}: {cmd['command']}")
            
            # 创建本地文件
            if self.create_shutdown_file(commands):
                # 清空接口数据
                if self.clear_all_commands():
                    self.log("✅ 处理完成！")
                else:
                    self.log("❌ 清空接口数据失败", 'error')
            else:
                self.log("❌ 创建本地文件失败", 'error')
        else:
            self.log("📭 暂无关机命令")
    
    def run_monitor(self):
        """运行监控"""
        self.log("🚀 启动 Shutdown 接口监控")
        self.log(f"📡 监控地址: {self.config['base_url']}/shutdown/list/")
        self.log(f"📁 本地文件: {self.config['shutdown_file']}")
        self.log(f"⏰ 检查间隔: {self.config['check_interval']} 秒")
        if self.config.get('enable_logging'):
            self.log(f"📝 日志文件: {self.config['log_file']}")
        self.log("=" * 50)
        
        try:
            while True:
                self.check_and_process()
                self.log(f"⏳ 等待 {self.config['check_interval']} 秒后再次检查...")
                self.log("-" * 30)
                time.sleep(self.config['check_interval'])
                
        except KeyboardInterrupt:
            self.log("\n🛑 监控已停止")
        except Exception as e:
            self.log(f"❌ 监控出错: {e}", 'error')

def main():
    """主函数"""
    monitor = ShutdownMonitor()
    monitor.run_monitor()

if __name__ == "__main__":
    main() 