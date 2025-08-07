"""
消息模板管理器 - 负责生成标准化的通知消息
"""
import logging
from typing import Dict, Any, Optional
from datetime import datetime

from .types.models import NotificationMessage
from .types.enums import NotificationType, NotificationImportance, NotificationTargetRole, MessageTemplate

logger = logging.getLogger(__name__)


class MessageTemplateManager:
    """消息模板管理器"""
    
    def __init__(self):
        """初始化消息模板管理器"""
        self._load_templates()
    
    def _load_templates(self):
        """加载消息模板"""
        self.templates = {
            MessageTemplate.PROJECT_COMMIT_WARNING: {
                "title": "项目提交预警 - {warning_level}级别",
                "title_en": "Project Commit Warning - {warning_level_en} Level",
                "content": "项目「{project_title}」已连续{days_without_commits}天无代码提交。\n\n"
                          "📊 项目统计：\n"
                          "• 历史提交总数：{total_commit_count}次\n"
                          "• 连续无提交天数：{days_without_commits}天\n"
                          "• 预警级别：{warning_level}\n\n"
                          "{severity_message}"
                          "请开发者及时推进项目进度，确保按时交付。",
                "content_en": "Project '{project_title}' has had no code commits for {days_without_commits} consecutive days.\n\n"
                             "📊 Project Statistics:\n"
                             "• Total historical commits: {total_commit_count}\n"
                             "• Consecutive days without commits: {days_without_commits}\n"
                             "• Warning level: {warning_level_en}\n\n"
                             "{severity_message_en}"
                             "Please ensure timely project progress and on-time delivery.",
                "notification_type": NotificationType.PROJECT,
                "importance": NotificationImportance.HIGH,
                "expiry_hours": 168
            },
            
            MessageTemplate.ORDER_APPLICATION: {
                "title": "有新的开发者报名您的订单",
                "title_en": "New Developer Applied for Your Order",
                "content": "开发者 {developer_name} 报名了您的订单「{order_title}」，请及时查看并选择合适的开发者。",
                "content_en": "Developer {developer_name} has applied for your order '{order_title}'. Please review and select the appropriate developer.",
                "notification_type": NotificationType.ORDER,
                "importance": NotificationImportance.NORMAL,
                "target_role": NotificationTargetRole.CLIENT,
                "expiry_hours": 168
            },
            
            MessageTemplate.MILESTONE_COMPLETION: {
                "title": "项目里程碑已完成",
                "title_en": "Project Milestone Completed",
                "content": "开发者 {developer_name} 完成了里程碑「{milestone_title}」，请及时验收。",
                "content_en": "Developer {developer_name} has completed the milestone '{milestone_title}'. Please review and accept.",
                "notification_type": NotificationType.PROJECT,
                "importance": NotificationImportance.HIGH,
                "target_role": NotificationTargetRole.CLIENT,
                "expiry_hours": 72
            },
            
            MessageTemplate.PAYMENT_SUCCESS: {
                "title": "支付成功",
                "title_en": "Payment Successful",
                "content": "您的支付已成功完成，金额：${amount}。",
                "content_en": "Your payment of ${amount} has been completed successfully.",
                "notification_type": NotificationType.PAYMENT,
                "importance": NotificationImportance.HIGH,
                "expiry_hours": 72
            },
            
            MessageTemplate.CONTRACT_SIGNED: {
                "title": "开发者已签署合同",
                "title_en": "Developer Has Signed Contract",
                "content": "开发者 {developer_name} 已接受并签署了项目「{order_title}」的合同，合同正式生效。项目即将开始，您可以在项目管理页面查看进度。",
                "content_en": "Developer {developer_name} has accepted and signed the contract for project '{order_title}'. The contract is now effective and the project will begin soon. You can track progress in the project management page.",
                "notification_type": NotificationType.ORDER,
                "importance": NotificationImportance.HIGH,
                "target_role": NotificationTargetRole.CLIENT,
                "expiry_hours": 168
            },
            
            MessageTemplate.MILESTONE_ESCROW: {
                "title": "里程碑托管资金已创建",
                "title_en": "Milestone Escrow Created",
                "content": "项目「{order_title}」的里程碑「{milestone_title}」托管资金 ${escrow_amount:.2f} 已创建，您可以放心开始工作，完成后申请验收即可释放资金。",
                "content_en": "Escrow funds of ${escrow_amount:.2f} have been created for milestone '{milestone_title}' in project '{order_title}'. You can start working with confidence and request acceptance after completion to release the funds.",
                "notification_type": NotificationType.PAYMENT,
                "importance": NotificationImportance.NORMAL,
                "target_role": NotificationTargetRole.FREELANCER,
                "expiry_hours": 168
            },
            
            MessageTemplate.MILESTONE_ACCEPTANCE_REQUEST: {
                "title": "里程碑验收申请",
                "title_en": "Milestone Acceptance Request",
                "content": "开发者 {developer_name} 已完成项目「{order_title}」的里程碑「{milestone_title}」，请及时确认验收。验收后将自动释放托管资金。",
                "content_en": "Developer {developer_name} has completed milestone '{milestone_title}' in project '{order_title}'. Please confirm acceptance promptly. Escrow funds will be automatically released upon acceptance.",
                "notification_type": NotificationType.PROJECT,
                "importance": NotificationImportance.HIGH,
                "target_role": NotificationTargetRole.CLIENT,
                "expiry_hours": 72
            },
            
            MessageTemplate.MILESTONE_ACCEPTANCE_CONFIRMED: {
                "title": "里程碑验收成功",
                "title_en": "Milestone Accepted",
                "content": "恭喜！项目「{order_title}」的里程碑「{milestone_title}」验收通过，您获得收入 ${developer_income:.2f}（已扣除20%平台佣金）已到账。",
                "content_en": "Congratulations! Milestone '{milestone_title}' in project '{order_title}' has been accepted. You earned ${developer_income:.2f} (after 20% platform commission) has been credited to your account.",
                "notification_type": NotificationType.PAYMENT,
                "importance": NotificationImportance.HIGH,
                "target_role": NotificationTargetRole.FREELANCER,
                "expiry_hours": 168
            },
            
            MessageTemplate.OFFER_HIRE: {
                "title": "收到项目合作邀请",
                "title_en": "Project Collaboration Invitation Received",
                "content": "客户 {client_name} 向您发送了项目合作邀请！\n\n📋 项目：{order_title}\n💰 预算：${budget}\n\n请及时查看合同详情并确认签署，签署后即可开始合作。",
                "content_en": "Client {client_name} has sent you a project collaboration invitation!\n\n📋 Project: {order_title}\n💰 Budget: ${budget}\n\nPlease review the contract details and confirm signing to start collaboration.",
                "notification_type": NotificationType.ORDER,
                "importance": NotificationImportance.HIGH,
                "target_role": NotificationTargetRole.FREELANCER,
                "expiry_hours": 168
            }
        }
    
    def create_message(
        self, 
        template: MessageTemplate, 
        params: Dict[str, Any],
        target_user_id: Optional[int] = None,
        action_url: Optional[str] = None,
        **kwargs
    ) -> NotificationMessage:
        """
        根据模板创建通知消息
        
        Args:
            template: 消息模板
            params: 模板参数
            target_user_id: 目标用户ID
            action_url: 跳转链接
            **kwargs: 其他参数（用于覆盖模板默认值）
            
        Returns:
            通知消息对象
        """
        if template not in self.templates:
            raise ValueError(f"未找到模板: {template}")
        
        template_config = self.templates[template]
        
        # 格式化消息内容
        title = template_config["title"].format(**params)
        content = template_config["content"].format(**params)
        title_en = template_config.get("title_en", "").format(**params) if template_config.get("title_en") else None
        content_en = template_config.get("content_en", "").format(**params) if template_config.get("content_en") else None
        
        # 创建通知消息
        message = NotificationMessage(
            title=title,
            content=content,
            title_en=title_en,
            content_en=content_en,
            notification_type=kwargs.get("notification_type", template_config.get("notification_type", NotificationType.SYSTEM)),
            importance=kwargs.get("importance", template_config.get("importance", NotificationImportance.NORMAL)),
            target_role=kwargs.get("target_role", template_config.get("target_role", NotificationTargetRole.ALL)),
            target_user_id=target_user_id,
            action_url=action_url,
            extra_data=kwargs.get("extra_data")
        )
        
        # 添加模板相关的额外数据
        if not message.extra_data:
            message.extra_data = {}
        
        message.extra_data.update({
            "template": template.value,
            "expiry_hours": kwargs.get("expiry_hours", template_config.get("expiry_hours", 168)),
            "created_at": datetime.now().isoformat()
        })
        
        return message
    
    def create_project_commit_warning_message(
        self,
        project_id: int,
        order_id: int,
        project_title: str,
        client_id: int,
        developer_id: int,
        days_without_commits: int,
        total_commit_count: int,
        target_role: NotificationTargetRole
    ) -> NotificationMessage:
        """
        创建项目提交预警消息
        
        Args:
            project_id: 项目ID
            order_id: 订单ID
            project_title: 项目标题
            client_id: 客户ID
            developer_id: 开发者ID
            days_without_commits: 连续无提交天数
            total_commit_count: 历史提交总数
            target_role: 目标角色
            
        Returns:
            通知消息对象
        """
        # 根据天数和历史提交情况调整预警级别 - 更严格的SMS触发条件
        if days_without_commits >= 5:  # 连续5天以上无提交
            if total_commit_count == 0:
                warning_level = "严重逾期"
                warning_level_en = "Critical Overdue"
                importance = NotificationImportance.HIGH
            elif total_commit_count < 3:
                warning_level = "严重逾期"
                warning_level_en = "Critical Overdue"
                importance = NotificationImportance.HIGH
            else:
                warning_level = "高度逾期"
                warning_level_en = "High Overdue"
                importance = NotificationImportance.HIGH
        elif days_without_commits >= 3:  # 连续3-4天无提交
            if total_commit_count == 0:
                warning_level = "严重逾期"
                warning_level_en = "Critical Overdue"
                importance = NotificationImportance.HIGH
            else:
                warning_level = "中度预警"
                warning_level_en = "Medium Warning"
                importance = NotificationImportance.NORMAL
        else:  # 1-2天无提交
            warning_level = "轻度预警"
            warning_level_en = "Low Warning"
            importance = NotificationImportance.NORMAL
        
        # 生成跳转链接
        if target_role == NotificationTargetRole.CLIENT:
            action_url = f"/client/order/{order_id}/milestones"
            target_user_id = client_id
        else:  # FREELANCER
            action_url = f"/freelancer/milestones/{order_id}"
            target_user_id = developer_id
        
        # 生成严重程度消息
        if "严重逾期" in warning_level:
            severity_message = "⚠️ 这是严重逾期提交预警！项目进度严重滞后，可能影响交付时间。\n\n"
            severity_message_en = "⚠️ This is a critical overdue commit warning! Project progress is severely behind schedule.\n\n"
        elif days_without_commits >= 3:
            severity_message = "⚡ 项目已进入预警状态，请尽快更新代码进度。\n\n"
            severity_message_en = "⚡ Project has entered warning status, please update code progress soon.\n\n"
        else:
            severity_message = "📝 请保持项目代码的定期更新。\n\n"
            severity_message_en = "📝 Please maintain regular project code updates.\n\n"

        params = {
            "project_title": project_title,
            "days_without_commits": days_without_commits,
            "total_commit_count": total_commit_count,
            "warning_level": warning_level,
            "warning_level_en": warning_level_en,
            "severity_message": severity_message,
            "severity_message_en": severity_message_en
        }
        
        return self.create_message(
            template=MessageTemplate.PROJECT_COMMIT_WARNING,
            params=params,
            target_user_id=target_user_id,
            action_url=action_url,
            importance=importance,
            target_role=target_role,
            extra_data={
                "project_id": project_id,
                "order_id": order_id,
                "warning_level": warning_level
            }
        )
    
    def create_order_application_message(
        self,
        order_id: int,
        client_id: int,
        developer_id: int,
        developer_name: str,
        order_title: str
    ) -> NotificationMessage:
        """
        创建订单报名通知消息
        
        Args:
            order_id: 订单ID
            client_id: 客户ID
            developer_id: 开发者ID
            developer_name: 开发者姓名
            order_title: 订单标题
            
        Returns:
            通知消息对象
        """
        action_url = f"/client/hire-developer/{order_id}"
        
        params = {
            "developer_name": developer_name,
            "order_title": order_title
        }
        
        return self.create_message(
            template=MessageTemplate.ORDER_APPLICATION,
            params=params,
            target_user_id=client_id,
            action_url=action_url,
            extra_data={
                "order_id": order_id,
                "developer_id": developer_id
            }
        )
    
    def get_template_config(self, template: MessageTemplate) -> Dict[str, Any]:
        """
        获取模板配置
        
        Args:
            template: 消息模板
            
        Returns:
            模板配置
        """
        return self.templates.get(template, {}).copy()
    
    def update_template(self, template: MessageTemplate, config: Dict[str, Any]):
        """
        更新模板配置
        
        Args:
            template: 消息模板
            config: 新的配置
        """
        if template in self.templates:
            self.templates[template].update(config)
        else:
            self.templates[template] = config
        
        logger.info(f"已更新消息模板: {template.value}")
