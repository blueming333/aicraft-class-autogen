"""
通知系统类型模块初始化
"""

from .enums import (
    NotificationType,
    NotificationImportance,
    NotificationTargetRole,
    NotificationStatus,
    ProviderType,
    MessageTemplate
)
from .models import (
    NotificationMessage,
    NotificationResult,
    NotificationConfig,
    SendRequest,
    BatchSendRequest,
    NotificationRecord
)

__all__ = [
    'NotificationType',
    'NotificationImportance',
    'NotificationTargetRole',
    'NotificationStatus',
    'ProviderType',
    'MessageTemplate',
    'NotificationMessage',
    'NotificationResult',
    'NotificationConfig',
    'SendRequest',
    'BatchSendRequest',
    'NotificationRecord'
]
