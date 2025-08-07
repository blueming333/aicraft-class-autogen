#!/usr/bin/env python3
"""
MySQL MCP Web演示启动脚本
"""

import os
import sys
import webbrowser
import time
from threading import Timer

# 添加项目根目录到路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.join(current_dir, '../../..')
sys.path.append(project_root)

def open_browser():
    """延迟打开浏览器"""
    time.sleep(1.5)  # 等待Flask服务启动
    webbrowser.open('http://localhost:5001')

def main():
    """主函数"""
    print("🚀 MySQL MCP Web演示启动器")
    print("=" * 50)
    
    # 检查依赖
    try:
        import flask
        import flask_cors
        print("✅ Flask依赖检查通过")
    except ImportError as e:
        print(f"❌ 缺少依赖: {e}")
        print("请运行: pip install flask flask-cors")
        return
    
    # 设置工作目录
    os.chdir(current_dir)
    print(f"📁 工作目录: {current_dir}")
    
    # 启动浏览器
    print("🌐 准备打开浏览器...")
    Timer(1.0, open_browser).start()
    
    # 导入并启动Flask应用
    try:
        from app import app
        print("🔧 启动Flask服务器...")
        print("📱 访问地址: http://localhost:5001")
        print("⏹️  按 Ctrl+C 停止服务器")
        print("=" * 50)
        
        # 运行Flask应用
        app.run(debug=False, host='0.0.0.0', port=5001)
        
    except KeyboardInterrupt:
        print("\n👋 服务器已停止")
    except Exception as e:
        print(f"❌ 启动失败: {e}")

if __name__ == '__main__':
    main()
