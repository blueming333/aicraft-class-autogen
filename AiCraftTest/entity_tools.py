import json
from pydantic import BaseModel, Field
from typing import List, Optional
from autogen_core.function_utils import OpenaiFunction


# 定义实体类
class TaskEntity(BaseModel):
    title: str = Field(..., description="任务标题")
    description: str = Field(..., description="任务详细描述")
    priority: str = Field(..., description="任务优先级：高/中/低")
    deadline: Optional[str] = Field(None, description="任务截止日期，格式YYYY-MM-DD")
    tags: List[str] = Field(default_factory=list, description="任务标签列表")


# 定义工具类
class EntityTools:
    """
    实体操作工具类
    
    提供各种实体的格式化和操作功能
    """
    
    @OpenaiFunction(
        name="format_task",
        description="将用户输入的任务信息格式化为标准的任务实体格式",
        parameters=TaskEntity.model_json_schema()
    )
    def format_task(self, title: str, description: str, priority: str, deadline: Optional[str] = None, tags: List[str] = None) -> str:
        """将用户输入的任务信息格式化为标准的任务实体格式"""
        task = TaskEntity(
            title=title,
            description=description,
            priority=priority,
            deadline=deadline,
            tags=tags or []
        )
        return f"任务已格式化:\n{json.dumps(task.model_dump(), ensure_ascii=False, indent=2)}" 