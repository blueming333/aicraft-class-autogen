"""
飞书通知提供商
"""
import logging
import os
from typing import Dict, Any

from .base import NotificationProvider
from ..types.models import NotificationMessage, NotificationResult
from ..types.enums import ProviderType

logger = logging.getLogger(__name__)


class FeishuNotificationProvider(NotificationProvider):
    """飞书通知提供商"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化飞书通知提供商
        
        Args:
            config: 配置信息
        """
        super().__init__(config)
        self.feishu_client = None
        self._init_feishu_client()
    
    @property
    def provider_type(self) -> ProviderType:
        return ProviderType.FEISHU
    
    def _init_feishu_client(self):
        """初始化飞书客户端"""
        try:
            from src.api.feishu_api import FeishuAPI
            
            # 从环境变量创建飞书客户端
            self.feishu_client = FeishuAPI.from_env()
            logger.info("飞书客户端初始化成功")
            
        except Exception as e:
            logger.warning(f"飞书客户端初始化失败: {str(e)}")
            self.feishu_client = None
    
    def is_available(self) -> bool:
        """检查是否可用"""
        return (
            self.enabled and 
            self.feishu_client is not None and 
            self.feishu_client.is_available()
        )
    
    def validate_config(self) -> bool:
        """验证配置"""
        app_id = os.getenv('FEISHU_APP_ID')
        app_secret = os.getenv('FEISHU_APP_SECRET')
        chat_id = os.getenv('FEISHU_CHAT_ID')
        
        return bool(
            app_id and app_id != 'your_feishu_app_id_here' and
            app_secret and app_secret != 'your_feishu_app_secret_here' and
            chat_id
        )
    
    def send_message(self, message: NotificationMessage, **kwargs) -> NotificationResult:
        """
        发送飞书消息
        
        Args:
            message: 通知消息
            **kwargs: 额外参数
                - use_rich_text: 是否使用富文本格式
                - extra_details: 额外详情信息
                
        Returns:
            发送结果
        """
        if not self.is_available():
            return NotificationResult(
                success=False,
                message="飞书通知提供商不可用",
                provider=self.provider_type,
                error="Provider not available"
            )
        
        try:
            use_rich_text = kwargs.get('use_rich_text', False)
            extra_details = kwargs.get('extra_details', {})
            
            # 构建预警详情
            details = {
                "通知类型": message.notification_type.value,
                "重要级别": message.importance.value,
                "内容": message.content[:200] + "..." if len(message.content) > 200 else message.content
            }
            
            # 添加额外详情
            if extra_details:
                details.update(extra_details)
            
            # 发送预警消息
            result = self.feishu_client.send_warning_message(
                warning_type="系统通知预警",
                title=message.title,
                details=details,
                level=message.importance.value,
                use_rich_text=use_rich_text
            )
            
            if result["success"]:
                logger.info(f"飞书预警发送成功: {message.title}")
                return NotificationResult(
                    success=True,
                    message="飞书消息发送成功",
                    provider=self.provider_type,
                    data=result.get("data")
                )
            else:
                error_msg = result.get('error', '未知错误')
                logger.error(f"飞书预警发送失败: {error_msg}")
                return NotificationResult(
                    success=False,
                    message="飞书消息发送失败",
                    provider=self.provider_type,
                    error=error_msg
                )
            
        except Exception as e:
            error_msg = f"飞书预警发送异常: {str(e)}"
            logger.error(error_msg)
            return NotificationResult(
                success=False,
                message="飞书消息发送失败",
                provider=self.provider_type,
                error=error_msg
            )
    
    def send_text_message(self, content: str) -> NotificationResult:
        """
        发送简单文本消息
        
        Args:
            content: 消息内容
            
        Returns:
            发送结果
        """
        if not self.is_available():
            return NotificationResult(
                success=False,
                message="飞书通知提供商不可用",
                provider=self.provider_type,
                error="Provider not available"
            )
        
        try:
            result = self.feishu_client.send_text_message(content)
            
            if result["success"]:
                logger.info(f"飞书文本消息发送成功: {content[:50]}...")
                return NotificationResult(
                    success=True,
                    message="飞书文本消息发送成功",
                    provider=self.provider_type,
                    data=result.get("data")
                )
            else:
                error_msg = result.get('error', '未知错误')
                logger.error(f"飞书文本消息发送失败: {error_msg}")
                return NotificationResult(
                    success=False,
                    message="飞书文本消息发送失败",
                    provider=self.provider_type,
                    error=error_msg
                )
                
        except Exception as e:
            error_msg = f"飞书文本消息发送异常: {str(e)}"
            logger.error(error_msg)
            return NotificationResult(
                success=False,
                message="飞书文本消息发送失败",
                provider=self.provider_type,
                error=error_msg
            )
    
    def get_status(self) -> Dict[str, Any]:
        """获取飞书提供商状态信息"""
        status = super().get_status()
        
        if self.feishu_client:
            status.update({
                'chat_id': self.feishu_client.config.chat_id,
                'app_id_configured': bool(os.getenv('FEISHU_APP_ID')),
                'app_secret_configured': bool(os.getenv('FEISHU_APP_SECRET'))
            })
        
        return status
