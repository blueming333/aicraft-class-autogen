"""
短信通知提供商
"""
import logging
import os
from typing import Dict, Any, List, Optional
from supabase import Client

from .base import NotificationProvider
from ..types.models import NotificationMessage, NotificationResult
from ..types.enums import ProviderType

logger = logging.getLogger(__name__)


class SmsNotificationProvider(NotificationProvider):
    """短信通知提供商"""
    
    def __init__(self, config: Dict[str, Any], supabase_client: Client):
        """
        初始化短信通知提供商
        
        Args:
            config: 配置信息
            supabase_client: Supabase客户端
        """
        super().__init__(config)
        self.supabase = supabase_client
        self._sms_sender = None
        self._init_sms_sender()
    
    @property
    def provider_type(self) -> ProviderType:
        return ProviderType.SMS
    
    def _init_sms_sender(self):
        """动态导入短信发送功能"""
        try:
            from src.routes.thirdpart.aliyun_sms import send_project_commit_warning
            self._sms_sender = send_project_commit_warning
        except ImportError:
            logger.warning("短信发送模块导入失败，短信功能将不可用")
            self._sms_sender = None
    
    def is_available(self) -> bool:
        """检查是否可用"""
        return (
            self.enabled and 
            self._sms_sender is not None and
            self._check_aliyun_config()
        )
    
    def _check_aliyun_config(self) -> bool:
        """检查阿里云短信配置"""
        access_key_id = os.getenv('ALIBABA_CLOUD_ACCESS_KEY_ID')
        access_key_secret = os.getenv('ALIBABA_CLOUD_ACCESS_KEY_SECRET')
        return bool(access_key_id and access_key_secret)
    
    def validate_config(self) -> bool:
        """验证配置"""
        return self._check_aliyun_config()
    
    def send_message(self, message: NotificationMessage, **kwargs) -> NotificationResult:
        """
        发送短信消息
        
        Args:
            message: 通知消息
            **kwargs: 额外参数
                - phone: 手机号
                - template_params: 短信模板参数
                
        Returns:
            发送结果
        """
        if not self.is_available():
            return NotificationResult(
                success=False,
                message="短信通知提供商不可用",
                provider=self.provider_type,
                error="Provider not available"
            )
        
        phone = kwargs.get('phone')
        if not phone:
            return NotificationResult(
                success=False,
                message="手机号不能为空",
                provider=self.provider_type,
                error="Phone number is required"
            )
        
        try:
            # 根据通知类型发送不同的短信
            template_params = kwargs.get('template_params', {})
            
            if message.notification_type.value == "project" and "project_commit_warning" in str(message.title).lower():
                # 项目提交预警短信
                result = self._send_project_commit_warning_sms(phone, template_params)
            else:
                # 通用短信（如果有其他模板）
                result = self._send_generic_sms(phone, message, template_params)
            
            if result:
                logger.info(f"短信发送成功: {phone}, 类型: {message.notification_type.value}")
                return NotificationResult(
                    success=True,
                    message="短信发送成功",
                    provider=self.provider_type,
                    data={"phone": phone}
                )
            else:
                logger.warning(f"短信发送失败: {phone}")
                return NotificationResult(
                    success=False,
                    message="短信发送失败",
                    provider=self.provider_type,
                    error="SMS send failed"
                )
            
        except Exception as e:
            error_msg = f"短信发送异常: {str(e)}"
            logger.error(error_msg)
            return NotificationResult(
                success=False,
                message="短信发送失败",
                provider=self.provider_type,
                error=error_msg
            )
    
    async def _send_project_commit_warning_sms(self, phone: str, template_params: Dict[str, Any]) -> bool:
        """
        发送项目提交预警短信
        
        Args:
            phone: 手机号
            template_params: 模板参数
                - project_title: 项目标题
                - days_without_commits: 连续无提交天数
                - warning_level: 预警级别
                
        Returns:
            发送是否成功
        """
        try:
            if self._sms_sender:
                return await self._sms_sender(
                    phone=phone,
                    project_title=template_params.get('project_title', ''),
                    days_without_commits=template_params.get('days_without_commits', 0),
                    warning_level=template_params.get('warning_level', '中等')
                )
            return False
        except Exception as e:
            logger.error(f"项目提交预警短信发送失败: {str(e)}")
            return False
    
    def _send_generic_sms(self, phone: str, message: NotificationMessage, template_params: Dict[str, Any]) -> bool:
        """
        发送通用短信
        
        Args:
            phone: 手机号
            message: 通知消息
            template_params: 模板参数
            
        Returns:
            发送是否成功
        """
        # TODO: 实现其他类型的短信发送
        logger.info(f"通用短信发送暂未实现: {message.notification_type.value}")
        return False
    
    async def send_to_users_by_ids(
        self, 
        user_ids: List[int], 
        message: NotificationMessage,
        template_params: Dict[str, Any]
    ) -> List[NotificationResult]:
        """
        根据用户ID列表发送短信
        
        Args:
            user_ids: 用户ID列表
            message: 通知消息
            template_params: 短信模板参数
            
        Returns:
            发送结果列表
        """
        results = []
        
        for user_id in user_ids:
            try:
                # 查询用户手机号
                user_response = self.supabase.table('user_info')\
                    .select('mobile, username')\
                    .eq('user_id', user_id)\
                    .execute()
                
                if not user_response.data or not user_response.data[0].get('mobile'):
                    logger.info(f"用户 {user_id} 没有手机号，跳过短信发送")
                    results.append(NotificationResult(
                        success=False,
                        message="用户没有手机号",
                        provider=self.provider_type,
                        error="no_mobile",
                        data={"user_id": user_id}
                    ))
                    continue
                
                mobile = user_response.data[0]['mobile']
                username = user_response.data[0].get('username', f'用户{user_id}')
                
                # 发送短信
                result = self.send_message(
                    message=message, 
                    phone=mobile, 
                    template_params=template_params
                )
                result.data = result.data or {}
                result.data.update({
                    "user_id": user_id,
                    "username": username
                })
                results.append(result)
                
            except Exception as e:
                logger.error(f"向用户 {user_id} 发送短信失败: {str(e)}")
                results.append(NotificationResult(
                    success=False,
                    message="短信发送失败",
                    provider=self.provider_type,
                    error=str(e),
                    data={"user_id": user_id}
                ))
        
        return results
