"""
通知提供商基础接口和抽象类
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional

from ..types.models import NotificationMessage, NotificationResult
from ..types.enums import ProviderType


class NotificationProvider(ABC):
    """通知提供商基础抽象类"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化通知提供商
        
        Args:
            config: 提供商配置
        """
        self.config = config
        self.enabled = config.get('enabled', True)
    
    @property
    @abstractmethod
    def provider_type(self) -> ProviderType:
        """获取提供商类型"""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """检查提供商是否可用"""
        pass
    
    @abstractmethod
    def send_message(self, message: NotificationMessage, **kwargs) -> NotificationResult:
        """
        发送单条消息
        
        Args:
            message: 通知消息
            **kwargs: 额外参数
            
        Returns:
            发送结果
        """
        pass
    
    def send_batch_messages(self, messages: List[NotificationMessage], **kwargs) -> List[NotificationResult]:
        """
        批量发送消息（默认实现为逐条发送）
        
        Args:
            messages: 通知消息列表
            **kwargs: 额外参数
            
        Returns:
            发送结果列表
        """
        results = []
        for message in messages:
            result = self.send_message(message, **kwargs)
            results.append(result)
        return results
    
    def validate_config(self) -> bool:
        """验证配置是否有效"""
        return True
    
    def get_status(self) -> Dict[str, Any]:
        """获取提供商状态信息"""
        return {
            'provider_type': self.provider_type.value,
            'enabled': self.enabled,
            'available': self.is_available(),
            'config_valid': self.validate_config()
        }
