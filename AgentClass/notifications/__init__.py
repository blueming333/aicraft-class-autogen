"""
通知系统模块 - 重构后的统一通知管理系统
支持应用内消息、短信、飞书等多种通知方式
"""

from .notification_service import NotificationService
from .types.enums import (
    NotificationType,
    NotificationImportance,
    NotificationTargetRole,
    NotificationStatus,
    ProviderType,
    MessageTemplate
)
from .types.models import (
    NotificationMessage,
    NotificationResult,
    NotificationConfig
)
from .template_manager import MessageTemplateManager
from .rules_manager import NotificationRulesManager

__all__ = [
    'NotificationService',
    'NotificationType',
    'NotificationImportance', 
    'NotificationTargetRole',
    'NotificationStatus',
    'ProviderType',
    'MessageTemplate',
    'NotificationMessage',
    'NotificationResult',
    'NotificationConfig',
    'MessageTemplateManager',
    'NotificationRulesManager'
]
