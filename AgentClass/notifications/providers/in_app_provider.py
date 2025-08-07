"""
应用内消息通知提供商
"""
import logging
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from supabase import Client

from .base import NotificationProvider
from ..types.models import NotificationMessage, NotificationResult
from ..types.enums import ProviderType

logger = logging.getLogger(__name__)


class InAppNotificationProvider(NotificationProvider):
    """应用内消息通知提供商"""
    
    def __init__(self, config: Dict[str, Any], supabase_client: Client):
        """
        初始化应用内通知提供商
        
        Args:
            config: 配置信息
            supabase_client: Supabase客户端
        """
        super().__init__(config)
        self.supabase = supabase_client
    
    @property
    def provider_type(self) -> ProviderType:
        return ProviderType.IN_APP
    
    def is_available(self) -> bool:
        """检查是否可用"""
        return self.enabled and self.supabase is not None
    
    def validate_config(self) -> bool:
        """验证配置"""
        return True  # 应用内通知不需要额外配置
    
    def send_message(self, message: NotificationMessage, **kwargs) -> NotificationResult:
        """
        发送应用内消息
        
        Args:
            message: 通知消息
            **kwargs: 额外参数
                - expiry_hours: 过期时间（小时）
                
        Returns:
            发送结果
        """
        if not self.is_available():
            return NotificationResult(
                success=False,
                message="应用内通知提供商不可用",
                provider=self.provider_type,
                error="Provider not available"
            )
        
        try:
            # 准备数据库记录数据
            notification_data = {
                "title": message.title,
                "content": message.content,
                "title_en": message.title_en,
                "content_en": message.content_en,
                "notification_type": message.notification_type.value,
                "importance": message.importance.value,
                "target_role": message.target_role.value,
                "target_user_id": message.target_user_id,
                "action_url": message.action_url,
                "is_read": {}  # 初始化为空的JSON对象
            }
            
            # 设置过期时间
            expiry_hours = kwargs.get('expiry_hours')
            if expiry_hours:
                expiry_date = datetime.now() + timedelta(hours=expiry_hours)
                notification_data["expiry_date"] = expiry_date.isoformat()
            
            # 插入到数据库
            response = self.supabase.table('system_notifications').insert(notification_data).execute()
            
            if not response.data:
                raise Exception("创建通知失败：数据库返回为空")
            
            notification = response.data[0]
            logger.info(f"应用内通知创建成功: ID={notification['notification_id']}, 标题='{message.title}'")
            
            return NotificationResult(
                success=True,
                message="应用内通知发送成功",
                provider=self.provider_type,
                data={"notification_id": notification['notification_id']}
            )
            
        except Exception as e:
            error_msg = f"应用内通知发送失败: {str(e)}"
            logger.error(error_msg)
            return NotificationResult(
                success=False,
                message="应用内通知发送失败",
                provider=self.provider_type,
                error=error_msg
            )
    
    def mark_as_read(self, notification_id: int, user_id: int) -> Dict[str, Any]:
        """
        标记通知为已读
        
        Args:
            notification_id: 通知ID
            user_id: 用户ID
            
        Returns:
            操作结果
        """
        try:
            # 获取当前通知
            response = self.supabase.table('system_notifications').select('is_read').eq('notification_id', notification_id).execute()
            
            if not response.data:
                raise Exception("通知不存在")
            
            # 获取当前已读状态
            current_is_read = response.data[0]['is_read'] or {}
            
            # 添加当前用户的已读时间戳
            current_is_read[str(user_id)] = datetime.now().isoformat()
            
            # 更新数据库
            update_response = self.supabase.table('system_notifications').update({
                'is_read': current_is_read
            }).eq('notification_id', notification_id).execute()
            
            if not update_response.data:
                raise Exception("更新已读状态失败")
            
            logger.info(f"用户 {user_id} 已标记通知 {notification_id} 为已读")
            
            return {
                "success": True,
                "message": "已标记为已读"
            }
            
        except Exception as e:
            logger.error(f"标记通知为已读失败: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "message": "标记为已读失败"
            }
    
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
        """
        获取用户的通知列表
        
        Args:
            user_id: 用户ID
            user_role: 用户角色
            limit: 限制数量
            offset: 偏移量
            notification_type: 通知类型筛选
            importance: 重要性筛选
            unread_only: 是否只获取未读通知
            language: 语言偏好（'zh' 中文，'en' 英文）
            
        Returns:
            通知列表
        """
        try:
            # 构建查询
            query = self.supabase.table('system_notifications').select('*')
            
            # 筛选目标用户或角色
            query = query.or_(f"target_user_id.eq.{user_id},and(target_role.eq.{user_role},target_user_id.is.null),and(target_role.eq.all,target_user_id.is.null)")
            
            # 筛选未过期的通知
            query = query.or_('expiry_date.is.null,expiry_date.gte.now()')
            
            # 按类型筛选
            if notification_type:
                query = query.eq('notification_type', notification_type)
            
            # 按重要性筛选
            if importance:
                query = query.eq('importance', importance)
            
            # 排序和分页
            query = query.order('created_at', desc=True).range(offset, offset + limit - 1)
            
            response = query.execute()
            notifications = response.data or []
            
            # 如果只要未读通知，过滤已读的
            if unread_only:
                filtered_notifications = []
                for notification in notifications:
                    is_read = notification.get('is_read', {})
                    if str(user_id) not in is_read:
                        filtered_notifications.append(notification)
                notifications = filtered_notifications
            
            # 根据语言偏好本地化通知内容
            localized_notifications = []
            for notification in notifications:
                localized_notification = self._get_localized_notification(notification, language)
                localized_notifications.append(localized_notification)
            
            logger.info(f"获取用户 {user_id} 的通知列表，共 {len(localized_notifications)} 条，语言: {language}")
            
            return {
                "success": True,
                "notifications": localized_notifications,
                "total": len(localized_notifications)
            }
            
        except Exception as e:
            logger.error(f"获取用户通知列表失败: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "notifications": [],
                "total": 0
            }
    
    def get_unread_count(self, user_id: int, user_role: str) -> int:
        """
        获取用户未读通知数量
        
        Args:
            user_id: 用户ID
            user_role: 用户角色
            
        Returns:
            未读通知数量
        """
        try:
            # 获取所有相关通知
            result = self.get_user_notifications(
                user_id=user_id,
                user_role=user_role,
                limit=1000,  # 获取足够多的通知
                unread_only=True
            )
            
            if result["success"]:
                return len(result["notifications"])
            else:
                return 0
                
        except Exception as e:
            logger.error(f"获取用户未读通知数量失败: {str(e)}")
            return 0
    
    def _get_localized_notification(self, notification: Dict[str, Any], language: str = 'zh') -> Dict[str, Any]:
        """
        根据语言偏好获取本地化的通知内容
        
        Args:
            notification: 通知数据
            language: 语言代码（'zh' 中文，'en' 英文）
            
        Returns:
            本地化的通知数据
        """
        localized_notification = notification.copy()
        
        if language == 'en':
            # 优先使用英文版本，如果没有则使用中文版本
            localized_notification['title'] = notification.get('title_en') or notification.get('title')
            localized_notification['content'] = notification.get('content_en') or notification.get('content')
        else:
            # 默认使用中文版本
            localized_notification['title'] = notification.get('title')
            localized_notification['content'] = notification.get('content')
        
        return localized_notification
