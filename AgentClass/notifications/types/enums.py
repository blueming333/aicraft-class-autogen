"""
通知系统枚举定义
"""
from enum import Enum


class NotificationType(Enum):
    """通知类型枚举"""
    SYSTEM = "system"
    ORDER = "order"
    PAYMENT = "payment"
    PROJECT = "project"
    MESSAGE = "message"


class NotificationImportance(Enum):
    """通知重要性枚举"""
    HIGH = "high"
    NORMAL = "normal"
    LOW = "low"


class NotificationTargetRole(Enum):
    """通知目标角色枚举"""
    ALL = "all"
    CLIENT = "client"
    FREELANCER = "freelancer"
    ADMIN = "admin"


class NotificationStatus(Enum):
    """通知状态枚举"""
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"
    EXPIRED = "expired"


class ProviderType(Enum):
    """通知提供商类型枚举"""
    IN_APP = "in_app"
    SMS = "sms"
    FEISHU = "feishu"
    EMAIL = "email"
    PUSH = "push"


class MessageTemplate(Enum):
    """消息模板枚举"""
    PROJECT_COMMIT_WARNING = "project_commit_warning"
    ORDER_APPLICATION = "order_application"
    MILESTONE_COMPLETION = "milestone_completion"
    PAYMENT_SUCCESS = "payment_success"
    CONTRACT_SIGNED = "contract_signed"
    MILESTONE_ESCROW = "milestone_escrow"
    MILESTONE_ACCEPTANCE_REQUEST = "milestone_acceptance_request"
    MILESTONE_ACCEPTANCE_CONFIRMED = "milestone_acceptance_confirmed"
    OFFER_HIRE = "offer_hire"
