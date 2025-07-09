# FastAPI .env文件使用演示脚本 (Demo3)
# 本脚本在FastAPIDemo.py基础上新增演示：
# 1. .env文件作用与常见配置项
# 2. 如何在FastAPI项目中加载.env（使用python-dotenv或pydantic的Settings）
# 3. 环境变量的读取与管理

from fastapi import FastAPI, Query, Path, Body, HTTPException, status, Depends
from pydantic import BaseModel, Field, BaseSettings
from typing import Optional, List, Dict, Any
from datetime import datetime
import uvicorn
import os
from dotenv import load_dotenv

# ====================================================================
# 1. .env文件作用与常见配置项
# ====================================================================

"""
.env文件的作用：
- 存储应用程序的配置信息和环境变量
- 避免在代码中硬编码敏感信息（如数据库密码、API密钥等）
- 支持不同环境（开发、测试、生产）的配置管理
- 提高代码的可维护性和安全性

常见配置项：
- 数据库连接信息
- API密钥和令牌
- 服务器配置（端口、主机等）
- 第三方服务配置
- 调试模式开关
- 日志级别设置
"""

# ====================================================================
# 2. 使用python-dotenv加载.env文件
# ====================================================================

# 方法1：使用python-dotenv直接加载
load_dotenv()  # 加载项目根目录下的.env文件

# 也可以指定.env文件路径
# load_dotenv(dotenv_path="path/to/your/.env")

# 方法2：使用pydantic的BaseSettings类（推荐）
class Settings(BaseSettings):
    """
    应用程序设置类
    使用pydantic的BaseSettings自动从环境变量和.env文件加载配置
    """
    # 应用程序基础配置
    app_name: str = Field(default="FastAPI Demo3", description="应用程序名称")
    app_version: str = Field(default="1.0.0", description="应用程序版本")
    debug: bool = Field(default=False, description="调试模式")
    
    # 服务器配置
    host: str = Field(default="127.0.0.1", description="服务器主机")
    port: int = Field(default=8000, description="服务器端口")
    
    # 数据库配置
    database_url: str = Field(default="sqlite:///./test.db", description="数据库连接URL")
    database_host: str = Field(default="localhost", description="数据库主机")
    database_port: int = Field(default=5432, description="数据库端口")
    database_name: str = Field(default="fastapi_demo", description="数据库名称")
    database_user: str = Field(default="user", description="数据库用户名")
    database_password: str = Field(default="password", description="数据库密码")
    
    # API密钥配置
    secret_key: str = Field(default="your-secret-key-here", description="应用程序密钥")
    algorithm: str = Field(default="HS256", description="加密算法")
    access_token_expire_minutes: int = Field(default=30, description="访问令牌过期时间（分钟）")
    
    # 第三方服务配置
    redis_url: str = Field(default="redis://localhost:6379", description="Redis连接URL")
    email_smtp_host: str = Field(default="smtp.gmail.com", description="邮件SMTP主机")
    email_smtp_port: int = Field(default=587, description="邮件SMTP端口")
    email_username: str = Field(default="", description="邮件用户名")
    email_password: str = Field(default="", description="邮件密码")
    
    # 外部API配置
    weather_api_key: str = Field(default="", description="天气API密钥")
    payment_api_key: str = Field(default="", description="支付API密钥")
    
    # 日志配置
    log_level: str = Field(default="INFO", description="日志级别")
    log_file_path: str = Field(default="./logs/app.log", description="日志文件路径")
    
    # 其他配置
    max_upload_size: int = Field(default=10485760, description="最大上传文件大小（字节）")  # 10MB
    allowed_file_types: str = Field(default="jpg,jpeg,png,pdf", description="允许的文件类型")
    cors_origins: str = Field(default="http://localhost:3000,http://localhost:8080", description="CORS允许的源")

    class Config:
        # 指定.env文件名
        env_file = ".env"
        # 允许环境变量覆盖.env文件中的值
        env_file_encoding = 'utf-8'
        # 区分大小写
        case_sensitive = False

# 创建设置实例
settings = Settings()

# ====================================================================
# 3. 环境变量的读取与管理
# ====================================================================

def get_settings() -> Settings:
    """
    获取应用程序设置的依赖函数
    这种方式便于在测试时模拟配置
    """
    return settings

# 演示直接从os.environ读取环境变量
def get_env_variable(var_name: str, default_value: str = None) -> str:
    """
    安全地获取环境变量
    如果变量不存在，返回默认值或抛出异常
    """
    value = os.getenv(var_name, default_value)
    if value is None:
        raise ValueError(f"环境变量 {var_name} 未设置且无默认值")
    return value

# 创建FastAPI实例，使用配置中的信息
app = FastAPI(
    title=settings.app_name,
    description="FastAPI .env文件使用演示",
    version=settings.app_version,
    debug=settings.debug,
    docs_url="/docs",
    redoc_url="/redoc"
)

# ====================================================================
# 配置信息展示接口
# ====================================================================

@app.get("/config/info")
async def get_config_info(current_settings: Settings = Depends(get_settings)):
    """
    获取当前应用程序配置信息
    注意：敏感信息（如密码）不应该在生产环境中暴露
    """
    # 安全地返回配置信息，隐藏敏感数据
    safe_config = {
        "app_name": current_settings.app_name,
        "app_version": current_settings.app_version,
        "debug": current_settings.debug,
        "host": current_settings.host,
        "port": current_settings.port,
        "database_host": current_settings.database_host,
        "database_port": current_settings.database_port,
        "database_name": current_settings.database_name,
        "algorithm": current_settings.algorithm,
        "access_token_expire_minutes": current_settings.access_token_expire_minutes,
        "log_level": current_settings.log_level,
        "max_upload_size": current_settings.max_upload_size,
        "allowed_file_types": current_settings.allowed_file_types.split(","),
        "cors_origins": current_settings.cors_origins.split(","),
        # 敏感信息用星号替代
        "database_user": current_settings.database_user,
        "database_password": "*" * len(current_settings.database_password) if current_settings.database_password else "",
        "secret_key": "*" * 10 if current_settings.secret_key != "your-secret-key-here" else "未设置",
        "email_username": current_settings.email_username or "未设置",
        "weather_api_key": "*" * 10 if current_settings.weather_api_key else "未设置",
        "payment_api_key": "*" * 10 if current_settings.payment_api_key else "未设置"
    }
    
    return {
        "message": "应用程序配置信息",
        "config": safe_config,
        "environment_source": "从.env文件和环境变量加载"
    }

@app.get("/config/database")
async def get_database_config(current_settings: Settings = Depends(get_settings)):
    """
    获取数据库配置信息示例
    """
    return {
        "database_url": current_settings.database_url,
        "host": current_settings.database_host,
        "port": current_settings.database_port,
        "database": current_settings.database_name,
        "user": current_settings.database_user,
        "connection_status": "配置已加载，实际连接需要数据库驱动"
    }

@app.get("/config/external-apis")
async def get_external_apis_config(current_settings: Settings = Depends(get_settings)):
    """
    获取外部API配置状态
    """
    apis_status = {
        "weather_api": {
            "configured": bool(current_settings.weather_api_key),
            "key_length": len(current_settings.weather_api_key) if current_settings.weather_api_key else 0
        },
        "payment_api": {
            "configured": bool(current_settings.payment_api_key),
            "key_length": len(current_settings.payment_api_key) if current_settings.payment_api_key else 0
        },
        "email_service": {
            "smtp_host": current_settings.email_smtp_host,
            "smtp_port": current_settings.email_smtp_port,
            "username_configured": bool(current_settings.email_username),
            "password_configured": bool(current_settings.email_password)
        }
    }
    
    return {
        "message": "外部API配置状态",
        "apis": apis_status
    }

# ====================================================================
# 环境变量验证接口
# ====================================================================

@app.get("/env/validate")
async def validate_environment():
    """
    验证关键环境变量是否正确设置
    """
    validation_results = []
    
    # 检查必要的环境变量
    required_vars = {
        "SECRET_KEY": "应用程序密钥",
        "DATABASE_URL": "数据库连接URL"
    }
    
    for var_name, description in required_vars.items():
        value = os.getenv(var_name)
        validation_results.append({
            "variable": var_name,
            "description": description,
            "is_set": value is not None,
            "is_default": value == getattr(settings, var_name.lower(), None) if value else False,
            "recommendation": "建议在.env文件中设置" if not value else "已正确设置"
        })
    
    # 检查可选但重要的环境变量
    optional_vars = {
        "WEATHER_API_KEY": "天气API密钥",
        "PAYMENT_API_KEY": "支付API密钥",
        "EMAIL_USERNAME": "邮件服务用户名",
        "EMAIL_PASSWORD": "邮件服务密码"
    }
    
    for var_name, description in optional_vars.items():
        value = os.getenv(var_name)
        validation_results.append({
            "variable": var_name,
            "description": description,
            "is_set": value is not None and value != "",
            "is_optional": True,
            "recommendation": "可选配置，根据需要设置" if not value else "已设置"
        })
    
    # 统计结果
    total_vars = len(validation_results)
    set_vars = sum(1 for result in validation_results if result["is_set"])
    required_set = sum(1 for result in validation_results if result["is_set"] and not result.get("is_optional", False))
    
    return {
        "message": "环境变量验证结果",
        "summary": {
            "total_checked": total_vars,
            "correctly_set": set_vars,
            "required_set": required_set,
            "completion_rate": f"{(set_vars/total_vars)*100:.1f}%"
        },
        "details": validation_results,
        "recommendations": [
            "在项目根目录创建.env文件",
            "将敏感信息（如密钥、密码）存储在.env文件中",
            "不要将.env文件提交到版本控制系统",
            "为不同环境（开发、测试、生产）创建不同的.env文件"
        ]
    }

# ====================================================================
# 动态配置更新示例
# ====================================================================

class ConfigUpdate(BaseModel):
    """
    配置更新模型
    """
    log_level: Optional[str] = Field(None, description="日志级别")
    debug: Optional[bool] = Field(None, description="调试模式")
    max_upload_size: Optional[int] = Field(None, ge=1, description="最大上传大小")

@app.put("/config/update")
async def update_config(
    config_update: ConfigUpdate,
    current_settings: Settings = Depends(get_settings)
):
    """
    动态更新配置（演示用途）
    注意：在生产环境中，配置更新需要更严格的权限控制
    """
    updated_fields = []
    
    if config_update.log_level is not None:
        current_settings.log_level = config_update.log_level
        updated_fields.append("log_level")
    
    if config_update.debug is not None:
        current_settings.debug = config_update.debug
        updated_fields.append("debug")
    
    if config_update.max_upload_size is not None:
        current_settings.max_upload_size = config_update.max_upload_size
        updated_fields.append("max_upload_size")
    
    return {
        "message": "配置更新成功",
        "updated_fields": updated_fields,
        "current_config": {
            "log_level": current_settings.log_level,
            "debug": current_settings.debug,
            "max_upload_size": current_settings.max_upload_size
        },
        "note": "配置更改在应用程序重启前有效"
    }

# ====================================================================
# 环境变量使用示例接口
# ====================================================================

@app.get("/demo/weather")
async def demo_weather_api(current_settings: Settings = Depends(get_settings)):
    """
    演示使用环境变量中的API密钥
    """
    if not current_settings.weather_api_key:
        return {
            "error": "天气API密钥未配置",
            "solution": "请在.env文件中设置 WEATHER_API_KEY=your_api_key"
        }
    
    # 这里只是演示，实际应用中会调用真实的天气API
    return {
        "message": "天气API调用成功（模拟）",
        "api_key_configured": True,
        "api_key_length": len(current_settings.weather_api_key),
        "weather_data": {
            "city": "北京",
            "temperature": "25°C",
            "description": "晴天",
            "note": "这是模拟数据，实际应用需要调用真实API"
        }
    }

@app.get("/demo/database-connection")
async def demo_database_connection(current_settings: Settings = Depends(get_settings)):
    """
    演示使用环境变量中的数据库配置
    """
    connection_info = {
        "database_url": current_settings.database_url,
        "host": current_settings.database_host,
        "port": current_settings.database_port,
        "database": current_settings.database_name,
        "user": current_settings.database_user,
        "status": "配置已加载"
    }
    
    # 模拟数据库连接检查
    if current_settings.database_url == "sqlite:///./test.db":
        connection_info["type"] = "SQLite"
        connection_info["note"] = "使用默认SQLite配置，实际项目中请配置真实数据库"
    else:
        connection_info["type"] = "PostgreSQL/MySQL/Other"
        connection_info["note"] = "已配置外部数据库"
    
    return {
        "message": "数据库连接配置",
        "connection": connection_info
    }

# ====================================================================
# .env文件示例生成接口
# ====================================================================

@app.get("/demo/generate-env-template")
async def generate_env_template():
    """
    生成.env文件模板
    """
    env_template = """# FastAPI Demo3 环境配置文件
# 复制此内容到项目根目录的.env文件中，并根据实际情况修改配置值

# 应用程序基础配置
APP_NAME=FastAPI Demo3
APP_VERSION=1.0.0
DEBUG=false

# 服务器配置
HOST=127.0.0.1
PORT=8000

# 数据库配置
DATABASE_URL=postgresql://user:password@localhost:5432/fastapi_demo
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_NAME=fastapi_demo
DATABASE_USER=your_db_user
DATABASE_PASSWORD=your_db_password

# 安全配置
SECRET_KEY=your-very-secret-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Redis配置
REDIS_URL=redis://localhost:6379

# 邮件服务配置
EMAIL_SMTP_HOST=smtp.gmail.com
EMAIL_SMTP_PORT=587
EMAIL_USERNAME=your_email@gmail.com
EMAIL_PASSWORD=your_email_password

# 外部API密钥
WEATHER_API_KEY=your_weather_api_key
PAYMENT_API_KEY=your_payment_api_key

# 日志配置
LOG_LEVEL=INFO
LOG_FILE_PATH=./logs/app.log

# 文件上传配置
MAX_UPLOAD_SIZE=10485760
ALLOWED_FILE_TYPES=jpg,jpeg,png,pdf

# CORS配置
CORS_ORIGINS=http://localhost:3000,http://localhost:8080
"""
    
    return {
        "message": ".env文件模板",
        "template": env_template,
        "instructions": [
            "1. 将上述内容保存为项目根目录下的.env文件",
            "2. 根据你的实际环境修改配置值",
            "3. 确保.env文件添加到.gitignore中",
            "4. 重启应用程序以加载新配置"
        ]
    }

# ====================================================================
# 启动应用程序
# ====================================================================

if __name__ == "__main__":
    """
    使用配置文件中的设置启动应用程序
    """
    print(f"正在启动 {settings.app_name} v{settings.app_version}")
    print(f"调试模式: {settings.debug}")
    print(f"服务器地址: {settings.host}:{settings.port}")
    print("配置来源: .env文件和环境变量")
    
    uvicorn.run(
        "FastAPIDemo3:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,  # 开发模式下启用热重载
        log_level=settings.log_level.lower()
    )

# ====================================================================
# 补充说明和最佳实践
# ====================================================================

"""
.env文件使用最佳实践：

1. 安全性：
   - 永远不要将.env文件提交到版本控制系统
   - 在.gitignore中添加.env文件
   - 敏感信息（密码、API密钥）只存储在.env文件中
   - 为不同环境使用不同的.env文件

2. 组织结构：
   - 按功能分组配置项
   - 使用描述性的变量名
   - 为每个配置项添加注释
   - 提供合理的默认值

3. 验证和错误处理：
   - 使用pydantic进行配置验证
   - 为必需的配置项设置验证规则
   - 提供清晰的错误信息
   - 实现配置检查接口

4. 开发流程：
   - 提供.env.example模板文件
   - 在项目文档中说明配置要求
   - 使用类型提示增强代码可读性
   - 实现配置的运行时验证

5. 部署考虑：
   - 支持从环境变量覆盖.env文件配置
   - 为生产环境提供安全的配置管理方案
   - 考虑使用配置管理服务（如AWS Parameter Store）
   - 实现配置更改的审计日志
""" 