"""
重构后的通知服务 - 统一管理系统通知的创建和发送
支持应用内消息、短信、飞书等多种通知方式
"""
import logging
import asyncio
from typing import Dict, Any, List, Optional
from supabase import Client

from .types.enums import NotificationType, NotificationImportance, NotificationTargetRole, ProviderType, MessageTemplate
from .types.models import NotificationMessage, NotificationResult, SendRequest, BatchSendRequest
from .providers import InAppNotificationProvider, SmsNotificationProvider, FeishuNotificationProvider
from .rules_manager import NotificationRulesManager
from .template_manager import MessageTemplateManager

logger = logging.getLogger(__name__)


class NotificationService:
    """重构后的统一通知服务"""
    
    def __init__(self, supabase_client: Client, config: Dict[str, Any] = None):
        """
        初始化通知服务
        
        Args:
            supabase_client: Supabase客户端
            config: 服务配置
        """
        self.supabase = supabase_client
        self.config = config or {}
        
        # 初始化各个组件
        self._init_providers()
        self._init_managers()
    
    def _init_providers(self):
        """初始化通知提供商"""
        self.providers = {}
        
        # 应用内通知提供商
        in_app_config = self.config.get('providers', {}).get('in_app', {'enabled': True})
        self.providers[ProviderType.IN_APP] = InAppNotificationProvider(in_app_config, self.supabase)
        
        # 短信通知提供商
        sms_config = self.config.get('providers', {}).get('sms', {'enabled': True})
        self.providers[ProviderType.SMS] = SmsNotificationProvider(sms_config, self.supabase)
        
        # 飞书通知提供商
        feishu_config = self.config.get('providers', {}).get('feishu', {'enabled': True})
        self.providers[ProviderType.FEISHU] = FeishuNotificationProvider(feishu_config)
        
        logger.info(f"已初始化 {len(self.providers)} 个通知提供商")
    
    def _init_managers(self):
        """初始化管理器"""
        # 规则管理器
        self.rules_manager = NotificationRulesManager(self.config.get('rules'))
        
        # 模板管理器
        self.template_manager = MessageTemplateManager()
        
        logger.info("已初始化通知规则管理器和模板管理器")
    
    def get_provider(self, provider_type: ProviderType):
        """获取指定类型的提供商"""
        return self.providers.get(provider_type)
    
    def get_available_providers(self) -> List[ProviderType]:
        """获取所有可用的提供商"""
        available = []
        for provider_type, provider in self.providers.items():
            if provider.is_available():
                available.append(provider_type)
        return available
    
    def send_notification(
        self, 
        message: NotificationMessage, 
        providers: Optional[List[ProviderType]] = None,
        **kwargs
    ) -> Dict[str, NotificationResult]:
        """
        发送通知消息
        
        Args:
            message: 通知消息
            providers: 指定的提供商列表，如果为None则根据规则自动选择
            **kwargs: 额外参数
            
        Returns:
            各提供商的发送结果
        """
        results = {}
        
        # 如果没有指定提供商，根据规则自动选择
        if providers is None:
            providers = self.rules_manager.get_enabled_providers(
                message.notification_type,
                message.importance,
                message.title,
                message.content
            )
        
        logger.info(f"发送通知: {message.title}, 使用提供商: {[p.value for p in providers]}")
        
        # 逐个提供商发送
        for provider_type in providers:
            provider = self.providers.get(provider_type)
            if not provider or not provider.is_available():
                results[provider_type] = NotificationResult(
                    success=False,
                    message=f"{provider_type.value} 提供商不可用",
                    provider=provider_type,
                    error="Provider not available"
                )
                continue
            
            try:
                # 根据提供商类型准备特定参数
                provider_kwargs = self._prepare_provider_kwargs(provider_type, message, kwargs)
                
                # 发送消息
                result = provider.send_message(message, **provider_kwargs)
                results[provider_type] = result
                
                if result.success:
                    logger.info(f"{provider_type.value} 发送成功: {message.title}")
                else:
                    logger.warning(f"{provider_type.value} 发送失败: {result.error}")
                
            except Exception as e:
                error_msg = f"{provider_type.value} 发送异常: {str(e)}"
                logger.error(error_msg)
                results[provider_type] = NotificationResult(
                    success=False,
                    message=f"{provider_type.value} 发送失败",
                    provider=provider_type,
                    error=error_msg
                )
        
        return results
    
    def _prepare_provider_kwargs(
        self, 
        provider_type: ProviderType, 
        message: NotificationMessage, 
        kwargs: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        为指定提供商准备特定参数
        
        Args:
            provider_type: 提供商类型
            message: 通知消息
            kwargs: 原始参数
            
        Returns:
            提供商特定参数
        """
        provider_kwargs = kwargs.copy()
        
        if provider_type == ProviderType.IN_APP:
            # 应用内通知参数
            provider_kwargs['expiry_hours'] = message.extra_data.get('expiry_hours', 168) if message.extra_data else 168
        
        elif provider_type == ProviderType.SMS:
            # 短信通知参数
            # 如果需要发送短信但没有指定手机号，则跳过
            if not kwargs.get('phone') and message.target_user_id:
                # 从数据库获取用户手机号会在 provider 内部处理
                pass
        
        elif provider_type == ProviderType.FEISHU:
            # 飞书通知参数
            provider_kwargs['use_rich_text'] = kwargs.get('use_rich_text', False)
            provider_kwargs['extra_details'] = kwargs.get('extra_details', {})
            
            # 添加默认的额外详情
            if message.extra_data:
                provider_kwargs['extra_details'].update(message.extra_data)
        
        return provider_kwargs
    
    def send_notification_by_template(
        self,
        template: MessageTemplate,
        params: Dict[str, Any],
        target_user_id: Optional[int] = None,
        action_url: Optional[str] = None,
        providers: Optional[List[ProviderType]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        根据模板发送通知
        
        Args:
            template: 消息模板
            params: 模板参数
            target_user_id: 目标用户ID
            action_url: 跳转链接
            providers: 指定的提供商列表
            **kwargs: 其他参数
            
        Returns:
            发送结果
        """
        try:
            # 创建通知消息
            message = self.template_manager.create_message(
                template=template,
                params=params,
                target_user_id=target_user_id,
                action_url=action_url,
                **kwargs
            )
            
            # 发送通知
            results = self.send_notification(message, providers, **kwargs)
            
            # 统计结果
            success_count = sum(1 for result in results.values() if result.success)
            total_count = len(results)
            
            return {
                "success": success_count > 0,
                "message": f"通知发送完成，成功 {success_count}/{total_count} 个提供商",
                "template": template.value,
                "results": {provider.value: result.__dict__ for provider, result in results.items()},
                "notification_message": message.__dict__
            }
            
        except Exception as e:
            error_msg = f"模板通知发送失败: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg,
                "message": "模板通知发送失败"
            }
    
    async def send_project_commit_warning(
        self,
        project_id: int,
        order_id: int,
        project_title: str,
        client_id: int,
        developer_id: int,
        days_without_commits: int,
        total_commit_count: int
    ) -> Dict[str, Any]:
        """
        发送项目提交预警通知
        
        Args:
            project_id: 项目ID
            order_id: 订单ID
            project_title: 项目标题
            client_id: 客户ID
            developer_id: 开发者ID
            days_without_commits: 连续无提交天数
            total_commit_count: 历史提交总数
            
        Returns:
            发送结果
        """
        try:
            results = []
            
            # 发送给客户
            client_message = self.template_manager.create_project_commit_warning_message(
                project_id=project_id,
                order_id=order_id,
                project_title=project_title,
                client_id=client_id,
                developer_id=developer_id,
                days_without_commits=days_without_commits,
                total_commit_count=total_commit_count,
                target_role=NotificationTargetRole.CLIENT
            )
            
            client_results = self.send_notification(client_message)
            results.append(("client", client_results))
            
            # 发送给开发者
            developer_message = self.template_manager.create_project_commit_warning_message(
                project_id=project_id,
                order_id=order_id,
                project_title=project_title,
                client_id=client_id,
                developer_id=developer_id,
                days_without_commits=days_without_commits,
                total_commit_count=total_commit_count,
                target_role=NotificationTargetRole.FREELANCER
            )
            
            developer_results = self.send_notification(developer_message)
            results.append(("developer", developer_results))
            
            # 如果是严重级别，发送短信
            warning_level = client_message.extra_data.get('warning_level', '中等')
            if warning_level == "严重":
                # 准备短信参数
                sms_template_params = {
                    "project_title": project_title,
                    "days_without_commits": days_without_commits,
                    "warning_level": warning_level
                }
                
                # 发送短信给用户
                sms_provider = self.get_provider(ProviderType.SMS)
                if sms_provider and sms_provider.is_available():
                    sms_results = await sms_provider.send_to_users_by_ids(
                        user_ids=[client_id, developer_id],
                        message=client_message,
                        template_params=sms_template_params
                    )
                    results.append(("sms", sms_results))
            
            logger.info(f"项目 {project_id} 提交预警通知已发送给客户({client_id})和开发者({developer_id})")
            
            return {
                "success": True,
                "message": "项目提交预警通知已发送",
                "warning_level": warning_level,
                "results": results
            }
            
        except Exception as e:
            error_msg = f"项目提交预警通知发送失败: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg,
                "message": "项目提交预警通知发送失败"
            }
    
    def create_order_application_notification(
        self,
        order_id: int,
        client_id: int,
        developer_id: int,
        developer_name: str,
        order_title: str
    ) -> Dict[str, Any]:
        """
        创建订单报名通知
        
        Args:
            order_id: 订单ID
            client_id: 客户ID
            developer_id: 开发者ID
            developer_name: 开发者姓名
            order_title: 订单标题
            
        Returns:
            发送结果
        """
        message = self.template_manager.create_order_application_message(
            order_id=order_id,
            client_id=client_id,
            developer_id=developer_id,
            developer_name=developer_name,
            order_title=order_title
        )
        
        results = self.send_notification(message)
        
        success_count = sum(1 for result in results.values() if result.success)
        
        return {
            "success": success_count > 0,
            "message": f"订单报名通知发送完成，成功 {success_count}/{len(results)} 个提供商",
            "results": {provider.value: result.__dict__ for provider, result in results.items()}
        }
    
    # 应用内通知相关方法的委托
    def mark_notification_as_read(self, notification_id: int, user_id: int) -> Dict[str, Any]:
        """标记通知为已读"""
        in_app_provider = self.get_provider(ProviderType.IN_APP)
        if in_app_provider:
            return in_app_provider.mark_as_read(notification_id, user_id)
        return {"success": False, "message": "应用内通知提供商不可用"}
    
    def get_user_notifications(
        self,
        user_id: int,
        user_role: str,
        limit: int = 50,
        offset: int = 0,
        notification_type: Optional[str] = None,
        importance: Optional[str] = None,
        unread_only: bool = False,
        language: str = 'zh'
    ) -> Dict[str, Any]:
        """获取用户通知列表"""
        in_app_provider = self.get_provider(ProviderType.IN_APP)
        if in_app_provider:
            return in_app_provider.get_user_notifications(
                user_id, user_role, limit, offset, notification_type, importance, unread_only, language
            )
        return {"success": False, "notifications": [], "total": 0}
    
    def get_unread_count(self, user_id: int, user_role: str) -> int:
        """获取用户未读通知数量"""
        in_app_provider = self.get_provider(ProviderType.IN_APP)
        if in_app_provider:
            return in_app_provider.get_unread_count(user_id, user_role)
        return 0
    
    def get_system_status(self) -> Dict[str, Any]:
        """获取通知系统状态"""
        status = {
            "service": "NotificationService",
            "version": "2.0.0",
            "providers": {},
            "available_providers": [],
            "rules": self.rules_manager.get_all_rules()
        }
        
        # 获取各提供商状态
        for provider_type, provider in self.providers.items():
            provider_status = provider.get_status()
            status["providers"][provider_type.value] = provider_status
            
            if provider_status["available"]:
                status["available_providers"].append(provider_type.value)
        
        return status
    
    # 兼容性方法 - 保持与旧版本的接口兼容
    async def send_notification_with_extensions(self, notification_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        兼容旧版本的扩展通知发送方法
        
        Args:
            notification_data: 通知数据
            
        Returns:
            发送结果
        """
        try:
            # 检查是否是项目提交预警通知
            if all(key in notification_data for key in ["project_id", "order_id", "project_title", "client_id", "developer_id", "days_without_commits", "total_commit_count"]):
                return await self.send_project_commit_warning(
                    project_id=notification_data["project_id"],
                    order_id=notification_data["order_id"],
                    project_title=notification_data["project_title"],
                    client_id=notification_data["client_id"],
                    developer_id=notification_data["developer_id"],
                    days_without_commits=notification_data["days_without_commits"],
                    total_commit_count=notification_data["total_commit_count"]
                )
            else:
                # 基础通知创建
                message = NotificationMessage(
                    title=notification_data.get("title", ""),
                    content=notification_data.get("content", ""),
                    title_en=notification_data.get("title_en"),
                    content_en=notification_data.get("content_en"),
                    notification_type=NotificationType(notification_data.get("notification_type", "system")),
                    importance=NotificationImportance(notification_data.get("importance", "normal")),
                    target_role=NotificationTargetRole(notification_data.get("target_role", "all")),
                    target_user_id=notification_data.get("target_user_id"),
                    action_url=notification_data.get("action_url"),
                    extra_data=notification_data.get("extra_data")
                )
                
                results = self.send_notification(message)
                
                success_count = sum(1 for result in results.values() if result.success)
                
                return {
                    "success": success_count > 0,
                    "message": f"通知发送完成，成功 {success_count}/{len(results)} 个提供商",
                    "results": results
                }
                
        except Exception as e:
            logger.error(f"兼容性通知发送失败: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "message": "通知发送失败"
            }
