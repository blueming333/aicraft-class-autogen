# FastAPI 基础知识点演示脚本
# 本脚本详细演示：
# 1. FastAPI简介与应用场景
# 2. FastAPI项目结构与快速上手
# 3. 路由与请求方法（GET、POST等）
# 4. 请求参数与响应（Query、Path、Body、Response Model）

from fastapi import FastAPI, Query, Path, Body, HTTPException, status
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
import uvicorn

# ====================================================================
# 1. FastAPI简介与应用场景
# ====================================================================

"""
FastAPI 是一个现代、快速（高性能）的 Web 框架，用于构建 API。

主要特点：
- 高性能：基于 Starlette 和 Pydantic，性能可媲美 NodeJS 和 Go
- 快速开发：代码重复减少约40%，bug减少约40%
- 直观：强大的编辑器支持，自动补全
- 简易：易于使用和学习，阅读文档时间更短
- 标准化：基于并完全兼容 API 的开放标准：OpenAPI 和 JSON Schema

应用场景：
- RESTful API 开发
- 微服务架构
- 机器学习模型部署
- 数据处理服务
- 企业级后端服务
"""

# ====================================================================
# 2. FastAPI项目结构与快速上手
# ====================================================================

# 创建FastAPI实例 - 这是整个应用程序的核心
app = FastAPI(
    title="FastAPI Demo API",          # API标题
    description="FastAPI基础知识点演示",  # API描述
    version="1.0.0",                   # 版本号
    docs_url="/docs",                  # Swagger UI 文档路径
    redoc_url="/redoc"                 # ReDoc 文档路径
)

# 典型的FastAPI项目结构：
"""
project/
├── main.py              # 主应用程序文件
├── models/              # 数据模型
│   ├── __init__.py
│   └── user.py
├── routers/             # 路由模块
│   ├── __init__.py
│   ├── users.py
│   └── items.py
├── dependencies.py      # 依赖项
├── database.py          # 数据库配置
├── config.py           # 配置文件
└── requirements.txt    # 依赖包列表
"""

# ====================================================================
# 3. 路由与请求方法（GET、POST等）
# ====================================================================

# 3.1 GET 请求 - 用于获取数据
@app.get("/")
async def read_root():
    """
    根路径 GET 请求
    返回欢迎消息
    """
    return {"message": "欢迎使用 FastAPI Demo API"}

@app.get("/health")
async def health_check():
    """
    健康检查接口
    用于监控服务状态
    """
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

# 3.2 POST 请求 - 用于创建数据
@app.post("/items")
async def create_item(item_data: dict):
    """
    POST 请求示例
    创建新的物品
    """
    return {
        "message": "物品创建成功",
        "item": item_data,
        "created_at": datetime.now().isoformat()
    }

# 3.3 PUT 请求 - 用于更新数据
@app.put("/items/{item_id}")
async def update_item(item_id: int, item_data: dict):
    """
    PUT 请求示例
    更新指定ID的物品
    """
    return {
        "message": f"物品 {item_id} 更新成功",
        "item": item_data,
        "updated_at": datetime.now().isoformat()
    }

# 3.4 DELETE 请求 - 用于删除数据
@app.delete("/items/{item_id}")
async def delete_item(item_id: int):
    """
    DELETE 请求示例
    删除指定ID的物品
    """
    return {
        "message": f"物品 {item_id} 删除成功",
        "deleted_at": datetime.now().isoformat()
    }

# ====================================================================
# 4. 请求参数与响应（Query、Path、Body、Response Model）
# ====================================================================

# 4.1 定义响应模型（Response Model）
class User(BaseModel):
    """
    用户数据模型
    使用 Pydantic 进行数据验证和序列化
    """
    id: int = Field(..., description="用户ID", example=1)
    name: str = Field(..., min_length=1, max_length=100, description="用户姓名", example="张三")
    email: str = Field(..., description="邮箱地址", example="zhangsan@example.com")
    age: Optional[int] = Field(None, ge=0, le=150, description="年龄", example=25)
    is_active: bool = Field(True, description="是否激活", example=True)
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")

class UserCreate(BaseModel):
    """
    创建用户请求模型
    """
    name: str = Field(..., min_length=1, max_length=100, description="用户姓名")
    email: str = Field(..., description="邮箱地址")
    age: Optional[int] = Field(None, ge=0, le=150, description="年龄")

class UserResponse(BaseModel):
    """
    用户响应模型
    """
    id: int
    name: str
    email: str
    age: Optional[int]
    is_active: bool
    created_at: datetime

# 模拟数据库
fake_users_db: List[User] = [
    User(id=1, name="张三", email="zhangsan@example.com", age=25),
    User(id=2, name="李四", email="lisi@example.com", age=30),
    User(id=3, name="王五", email="wangwu@example.com", age=28)
]

# 4.2 Path 参数 - 路径参数
@app.get("/users/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int = Path(..., ge=1, description="用户ID，必须大于0")
):
    """
    通过用户ID获取用户信息
    
    Path 参数特点：
    - 是路径的一部分，用 {} 包围
    - 支持数据类型验证
    - 支持约束条件（如 ge=1 表示大于等于1）
    """
    user = next((user for user in fake_users_db if user.id == user_id), None)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"用户 {user_id} 不存在"
        )
    return user

# 4.3 Query 参数 - 查询参数
@app.get("/users", response_model=List[UserResponse])
async def get_users(
    skip: int = Query(0, ge=0, description="跳过的记录数"),
    limit: int = Query(10, ge=1, le=100, description="返回的记录数，最多100条"),
    search: Optional[str] = Query(None, min_length=1, description="搜索关键词"),
    is_active: Optional[bool] = Query(None, description="是否只返回激活用户")
):
    """
    获取用户列表
    
    Query 参数特点：
    - 出现在 URL 的 ? 后面
    - 支持默认值
    - 支持可选参数（Optional）
    - 支持数据验证和约束
    """
    users = fake_users_db.copy()
    
    # 过滤激活状态
    if is_active is not None:
        users = [user for user in users if user.is_active == is_active]
    
    # 搜索功能
    if search:
        users = [user for user in users if search.lower() in user.name.lower()]
    
    # 分页
    return users[skip:skip + limit]

# 4.4 Body 参数 - 请求体参数
@app.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(user_data: UserCreate):
    """
    创建新用户
    
    Body 参数特点：
    - 通过请求体传递，通常是 JSON 格式
    - 使用 Pydantic 模型进行验证
    - 自动进行数据类型转换和验证
    """
    # 生成新的用户ID
    new_id = max([user.id for user in fake_users_db], default=0) + 1
    
    # 创建新用户
    new_user = User(
        id=new_id,
        name=user_data.name,
        email=user_data.email,
        age=user_data.age
    )
    
    fake_users_db.append(new_user)
    return new_user

# 4.5 混合参数类型示例
@app.put("/users/{user_id}/profile", response_model=UserResponse)
async def update_user_profile(
    user_id: int = Path(..., ge=1, description="用户ID"),
    force_update: bool = Query(False, description="是否强制更新"),
    profile_data: dict = Body(..., description="用户资料数据")
):
    """
    更新用户资料
    
    演示同时使用 Path、Query 和 Body 参数：
    - user_id: 路径参数
    - force_update: 查询参数
    - profile_data: 请求体参数
    """
    user = next((user for user in fake_users_db if user.id == user_id), None)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"用户 {user_id} 不存在"
        )
    
    # 更新用户信息
    if "name" in profile_data:
        user.name = profile_data["name"]
    if "email" in profile_data:
        user.email = profile_data["email"]
    if "age" in profile_data:
        user.age = profile_data["age"]
    
    return user

# 4.6 高级参数验证示例
class ItemFilter(BaseModel):
    """
    物品过滤器模型
    """
    category: Optional[str] = Field(None, description="物品分类")
    min_price: Optional[float] = Field(None, ge=0, description="最低价格")
    max_price: Optional[float] = Field(None, ge=0, description="最高价格")
    tags: Optional[List[str]] = Field(None, description="标签列表")

@app.post("/search/items")
async def search_items(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    filters: ItemFilter = Body(..., description="过滤条件")
):
    """
    高级物品搜索
    
    演示复杂的参数验证和嵌套模型使用
    """
    return {
        "message": "搜索执行成功",
        "page": page,
        "page_size": page_size,
        "filters": filters.dict(exclude_none=True),
        "total": 0,
        "items": []
    }

# 4.7 错误处理示例
@app.get("/demo/error/{error_type}")
async def demo_error_handling(error_type: str):
    """
    错误处理演示
    """
    if error_type == "400":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="这是一个 400 错误示例"
        )
    elif error_type == "404":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="这是一个 404 错误示例"
        )
    elif error_type == "500":
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="这是一个 500 错误示例"
        )
    else:
        return {"message": f"错误类型 {error_type} 演示完成"}

# ====================================================================
# 启动应用程序
# ====================================================================

if __name__ == "__main__":
    """
    运行 FastAPI 应用程序
    
    启动方式：
    1. 直接运行：python FastAPIDemo.py
    2. 使用 uvicorn：uvicorn FastAPIDemo:app --reload
    3. 指定端口：uvicorn FastAPIDemo:app --host 0.0.0.0 --port 8080 --reload
    
    访问方式：
    - API 文档：http://localhost:8000/docs
    - ReDoc 文档：http://localhost:8000/redoc
    - API 接口：http://localhost:8000/
    """
    uvicorn.run(
        "FastAPIDemo:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="info"
    )

# ====================================================================
# 补充说明和最佳实践
# ====================================================================

"""
FastAPI 最佳实践：

1. 数据模型设计：
   - 使用 Pydantic 模型进行数据验证
   - 分离请求模型和响应模型
   - 合理使用 Field 进行字段约束

2. 路由组织：
   - 使用 APIRouter 进行路由分组
   - 合理命名路由路径
   - 添加详细的文档字符串

3. 错误处理：
   - 使用 HTTPException 抛出标准HTTP错误
   - 自定义异常处理器
   - 提供有意义的错误信息

4. 性能优化：
   - 使用异步函数（async/await）
   - 合理使用依赖注入
   - 启用 GZIP 压缩

5. 安全性：
   - 使用 HTTPS
   - 实现身份验证和授权
   - 输入验证和数据清理

6. 测试：
   - 使用 pytest 进行单元测试
   - 使用 httpx 进行API测试
   - 测试覆盖率要求
""" 