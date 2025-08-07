"""
通知系统配置示例
展示如何配置和使用重构后的通知系统
"""

# 通知系统配置示例
NOTIFICATION_CONFIG = {
    # 提供商配置
    'providers': {
        'in_app': {
            'enabled': True,
            'description': '应用内通知，存储到数据库'
        },
        'sms': {
            'enabled': True,
            'description': '短信通知，使用阿里云短信服务',
            'rate_limit': {
                'max_per_minute': 10,
                'max_per_hour': 100
            }
        },
        'feishu': {
            'enabled': True,
            'description': '飞书群聊通知，用于系统预警',
            'warning_level': 'high'  # all, high, critical
        }
    },
    
    # 通知规则配置
    'rules': {
        # 可以在这里自定义规则，覆盖默认规则
        'custom_rules': {
            # 例：紧急情况下所有高重要性通知都发送短信
            'emergency_mode': False,
            # 例：工作时间外只发送应用内通知
            'work_hours_only_sms': False
        }
    },
    
    # 消息模板配置
    'templates': {
        # 可以在这里自定义或覆盖默认模板
    }
}

# 使用示例
def example_usage():
    """
    通知系统使用示例
    """
    from supabase import create_client
    from src.utils.notifications import (
        NotificationService,
        NotificationType,
        NotificationImportance,
        MessageTemplate,
        NotificationMessage
    )
    
    # 1. 初始化服务
    supabase = create_client("your_url", "your_key")
    notification_service = NotificationService(
        supabase_client=supabase,
        config=NOTIFICATION_CONFIG
    )
    
    # 2. 发送简单通知
    message = NotificationMessage(
        title="系统维护通知",
        content="系统将于今晚进行维护，预计停机2小时",
        notification_type=NotificationType.SYSTEM,
        importance=NotificationImportance.NORMAL,
        target_user_id=123
    )
    
    results = notification_service.send_notification(message)
    print("发送结果:", results)
    
    # 3. 使用模板发送通知
    template_result = notification_service.send_notification_by_template(
        template=MessageTemplate.PROJECT_COMMIT_WARNING,
        params={
            "project_title": "电商网站",
            "days_without_commits": 3,
            "total_commit_count": 10,
            "warning_level": "中等",
            "warning_level_en": "Medium"
        },
        target_user_id=456,
        action_url="/project/123"
    )
    print("模板通知结果:", template_result)
    
    # 4. 发送项目提交预警（完整流程）
    import asyncio
    async def send_warning():
        warning_result = await notification_service.send_project_commit_warning(
            project_id=789,
            order_id=101112,
            project_title="移动App开发",
            client_id=123,
            developer_id=456,
            days_without_commits=5,
            total_commit_count=2
        )
        print("项目预警结果:", warning_result)
    
    asyncio.run(send_warning())
    
    # 5. 获取用户通知
    notifications = notification_service.get_user_notifications(
        user_id=123,
        user_role="client",
        limit=20,
        unread_only=True
    )
    print("用户通知:", notifications)
    
    # 6. 获取系统状态
    status = notification_service.get_system_status()
    print("系统状态:", status)


if __name__ == "__main__":
    example_usage()
