#!/usr/bin/env python3
"""
MySQL MCP Web演示启动脚本 (使用.venv环境)
"""

import os
import sys
import subprocess
import webbrowser
import time
from threading import Timer

def find_venv_python():
    """找到.venv环境的Python可执行文件"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.join(current_dir, '../../..')
    
    # 尝试不同的Python可执行文件路径
    python_paths = [
        os.path.join(project_root, '.venv/bin/python'),
        os.path.join(project_root, '.venv/bin/python3'),
        os.path.join(project_root, '.venv/bin/python3.12'),
    ]
    
    for python_path in python_paths:
        if os.path.exists(python_path):
            return python_path
    
    return None

def open_browser_delayed():
    """延迟打开浏览器"""
    time.sleep(3)
    print("🌐 打开浏览器...")
    webbrowser.open("http://localhost:5001")

def main():
    """主函数"""
    print("🗄️ MySQL MCP Web演示系统 (.venv环境)")
    print("=" * 60)
    
    # 找到Python可执行文件
    python_path = find_venv_python()
    if not python_path:
        print("❌ 未找到.venv环境中的Python可执行文件")
        print("请确保.venv目录存在且包含Python可执行文件")
        return
    
    print(f"✅ 使用Python: {python_path}")
    
    # 设置工作目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(current_dir)
    print(f"📁 工作目录: {current_dir}")
    
    # 准备启动Flask应用
    app_script = os.path.join(current_dir, "app.py")
    
    if not os.path.exists(app_script):
        print("❌ 未找到app.py文件")
        return
    
    print("🚀 启动Flask Web服务器...")
    print("📱 访问地址: http://localhost:5001")
    print("⏹️  按 Ctrl+C 停止服务器")
    print("=" * 60)
    
    # 延迟打开浏览器
    Timer(2.0, open_browser_delayed).start()
    
    try:
        # 启动Flask应用
        subprocess.run([python_path, app_script], cwd=current_dir)
    except KeyboardInterrupt:
        print("\n👋 服务器已停止")
    except Exception as e:
        print(f"❌ 启动失败: {e}")

if __name__ == '__main__':
    main()
