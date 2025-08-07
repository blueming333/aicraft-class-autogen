"""
通知系统数据模型定义
"""
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from datetime import datetime

from .enums import NotificationType, NotificationImportance, NotificationTargetRole, NotificationStatus, ProviderType


@dataclass
class NotificationMessage:
    """通知消息数据模型"""
    title: str
    content: str
    title_en: Optional[str] = None
    content_en: Optional[str] = None
    notification_type: NotificationType = NotificationType.SYSTEM
    importance: NotificationImportance = NotificationImportance.NORMAL
    target_role: NotificationTargetRole = NotificationTargetRole.ALL
    target_user_id: Optional[int] = None
    action_url: Optional[str] = None
    extra_data: Optional[Dict[str, Any]] = None


@dataclass
class NotificationResult:
    """通知发送结果"""
    success: bool
    message: str
    provider: ProviderType
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


@dataclass
class NotificationConfig:
    """通知配置"""
    enabled_providers: List[ProviderType]
    provider_configs: Dict[str, Dict[str, Any]]
    rules: Dict[str, Any]  # 发送规则配置


@dataclass
class SendRequest:
    """发送请求"""
    message: NotificationMessage
    providers: List[ProviderType]
    config: Optional[Dict[str, Any]] = None


@dataclass
class BatchSendRequest:
    """批量发送请求"""
    messages: List[NotificationMessage]
    providers: List[ProviderType]
    config: Optional[Dict[str, Any]] = None


@dataclass
class NotificationRecord:
    """通知记录"""
    id: Optional[int] = None
    title: str = ""
    content: str = ""
    title_en: Optional[str] = None
    content_en: Optional[str] = None
    notification_type: str = ""
    importance: str = ""
    target_role: str = ""
    target_user_id: Optional[int] = None
    action_url: Optional[str] = None
    status: NotificationStatus = NotificationStatus.PENDING
    provider_results: Dict[str, NotificationResult] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    expiry_date: Optional[datetime] = None
    is_read: Dict[str, str] = None  # user_id -> read_time
    
    def __post_init__(self):
        if self.provider_results is None:
            self.provider_results = {}
        if self.is_read is None:
            self.is_read = {}
