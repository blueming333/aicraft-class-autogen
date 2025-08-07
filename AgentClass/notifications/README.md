# 通知系统重构说明

## 概述

本次重构将原有的单一通知服务文件重构为模块化、可扩展的通知系统，支持多种通知方式的统一管理。

## 目录结构

```
src/utils/notifications/
├── __init__.py                    # 模块初始化
├── notification_service.py       # 核心通知服务
├── rules_manager.py              # 通知规则管理器
├── template_manager.py           # 消息模板管理器
├── example_config.py             # 配置示例
├── types/                        # 类型定义
│   ├── __init__.py
│   ├── enums.py                  # 枚举定义
│   └── models.py                 # 数据模型
└── providers/                    # 通知提供商
    ├── __init__.py
    ├── base.py                   # 基础抽象类
    ├── in_app_provider.py        # 应用内通知
    ├── sms_provider.py           # 短信通知
    └── feishu_provider.py        # 飞书通知
```

## 主要特性

### 1. 多提供商支持
- **应用内通知**: 存储到数据库的系统通知
- **短信通知**: 通过阿里云短信服务发送
- **飞书通知**: 发送到飞书群聊的预警消息

### 2. 智能规则管理
- 根据通知类型和重要性自动选择发送方式
- 支持自定义规则配置
- 避免过度通知的智能过滤

### 3. 模板化消息
- 预定义的消息模板
- 支持中英文双语
- 参数化内容生成

### 4. 向后兼容
- 保持原有 API 接口不变
- 现有代码无需修改即可使用新功能

## 使用方式

### 基础使用（兼容旧版本）

```python
from src.utils.notification_service import NotificationService

# 原有代码无需修改
notification_service = NotificationService(supabase_client)
result = notification_service.create_notification(
    title="测试通知",
    content="这是一条测试通知",
    notification_type="system",
    importance="normal"
)
```

### 使用新功能

```python
from src.utils.notifications import (
    NotificationService,
    NotificationType,
    NotificationImportance,
    MessageTemplate
)

# 初始化新服务
service = NotificationService(supabase_client)

# 使用模板发送通知
result = service.send_notification_by_template(
    template=MessageTemplate.PROJECT_COMMIT_WARNING,
    params={
        "project_title": "AI项目",
        "days_without_commits": 5,
        "total_commit_count": 10,
        "warning_level": "高",
        "warning_level_en": "High"
    },
    target_user_id=123
)
```

### 访问新系统实例

```python
from src.utils.notification_service import NotificationService

# 通过兼容层访问新功能
old_service = NotificationService(supabase_client)
new_service = old_service.get_new_service()

# 使用新系统的所有功能
status = new_service.get_system_status()
```

## 通知规则

### 应用内通知
- ✅ 所有类型的通知都会发送应用内消息
- 📱 存储在 `system_notifications` 表中
- 🌐 支持中英文本地化

### 短信通知
- ⚠️ 仅发送最严重的项目逾期预警通知
- 📞 触发条件：`PROJECT` 类型 + `HIGH` 重要性 + 包含 "严重逾期" 和 "提交预警" 关键词
- 📅 天数阈值：连续无提交天数 ≥ 3天
- 🎯 目前仅 `git_commits_task.py` 中的严重项目逾期预警会触发

### 飞书通知
- 🚨 高重要性通知自动发送
- 💬 包含预警关键词的通知也会发送
- 🔧 可配置预警级别（all/high/critical）

## 业务场景通知配置

### 📊 当前各业务场景的提供商配置

| 业务场景 | 通知类型 | 重要性 | 应用内通知 | 短信通知 | 飞书通知 | 说明 |
|---------|---------|--------|----------|----------|----------|------|
| **📝 订单报名通知** | ORDER | NORMAL | ✅ | ❌ | ❌ | 仅应用内通知 |
| **💼 发送Offer邀请** | ORDER | HIGH | ✅ | ❌ | ✅ | 应用内+飞书 |
| **📋 合同签署通知** | ORDER | HIGH | ✅ | ❌ | ✅ | 应用内+飞书 |
| **🎯 里程碑完成通知** | PROJECT | HIGH | ✅ | ❌ | ✅ | 应用内+飞书 |
| **💰 里程碑托管通知** | PAYMENT | NORMAL | ✅ | ❌ | ❌ | 仅应用内通知 |
| **⚠️ 严重项目逾期预警** | PROJECT | HIGH | ✅ | ✅ | ✅ | 全部通知方式 |

### 🔍 配置说明

**高重要性业务通知 (HIGH)**：
- ✅ 应用内通知：实时显示在用户界面
- ✅ 飞书通知：发送到管理群进行监控
- ❌ 短信通知：除项目逾期预警外，其他业务不发短信

**普通重要性业务通知 (NORMAL)**：
- ✅ 应用内通知：保存到通知中心
- ❌ 飞书通知：避免过度打扰
- ❌ 短信通知：成本控制考虑

**项目逾期预警 (特殊规则)**：
- 🚨 严重程度判断：5天以上无提交 + 历史提交数少 = 严重逾期
- 📱 短信触发：仅严重逾期情况才发送短信提醒
- 💬 飞书同步：所有项目预警都会同步到管理群

## 环境变量配置

```bash
# 飞书配置
FEISHU_APP_ID=your_app_id
FEISHU_APP_SECRET=your_app_secret
FEISHU_CHAT_ID=your_chat_id
FEISHU_ENABLED=true

# 短信配置
ALIBABA_CLOUD_ACCESS_KEY_ID=your_access_key
ALIBABA_CLOUD_ACCESS_KEY_SECRET=your_secret

# 数据库配置
SUPABASE_URL=your_supabase_url
SUPABASE_ANON_KEY=your_supabase_key
```

## 测试

使用重构后的测试工具：

```bash
cd server
python test_feishu_usage.py
```

测试内容包括：
- 🔧 通知服务初始化
- 📱 飞书提供商测试
- 📋 模板通知测试
- 📏 通知规则测试
- ⚠️ 项目提交预警测试

### 业务场景测试

可以使用以下命令测试各业务场景的提供商配置：

```python
from src.utils.notifications.rules_manager import NotificationRulesManager
from src.utils.notifications.types.enums import NotificationType, NotificationImportance, ProviderType

rules_manager = NotificationRulesManager()

# 测试订单报名通知
should_send_sms = rules_manager.should_send_with_provider(
    ProviderType.SMS, 
    NotificationType.ORDER, 
    NotificationImportance.NORMAL, 
    "有新的开发者报名您的订单", 
    "开发者报名了订单"
)
print(f"订单报名是否发送短信: {should_send_sms}")  # False

# 测试合同签署通知  
should_send_feishu = rules_manager.should_send_with_provider(
    ProviderType.FEISHU, 
    NotificationType.ORDER, 
    NotificationImportance.HIGH, 
    "开发者已签署合同", 
    "开发者已接受并签署了合同"
)
print(f"合同签署是否发送飞书: {should_send_feishu}")  # True
```

## 扩展性

### 添加新的通知提供商

1. 继承 `NotificationProvider` 基类
2. 实现必要的抽象方法
3. 在 `NotificationService` 中注册
4. 在规则管理器中添加相应规则

### 添加新的消息模板

1. 在 `MessageTemplate` 枚举中添加新类型
2. 在 `MessageTemplateManager` 中添加模板配置
3. 可选：添加专门的创建方法

### 自定义通知规则

1. 修改 `NotificationRulesManager` 中的规则逻辑
2. 或在配置中传入自定义规则
3. 支持运行时动态修改规则

### 调整业务场景通知配置

如需为特定业务场景添加短信通知，可以修改 `rules_manager.py`：

```python
# 示例：为合同签署添加短信通知
elif provider_type == ProviderType.SMS:
    # 现有的严重项目逾期规则
    if notification_type == NotificationType.PROJECT and importance == NotificationImportance.HIGH:
        # ... 现有逻辑
    
    # 新增：合同签署也发送短信
    elif notification_type == NotificationType.ORDER and importance == NotificationImportance.HIGH:
        if "签署合同" in title or "合同签署" in content:
            return True
    
    return False
```

**建议的业务优先级调整**：
- 🔥 **极高优先级** (短信+飞书+应用内)：项目逾期预警、重大系统故障
- 📱 **高优先级** (飞书+应用内)：合同签署、Offer邀请、里程碑完成
- 📋 **中优先级** (仅应用内)：订单报名、里程碑托管、一般性通知

## 迁移建议

1. **立即可用**: 现有代码无需修改，直接享受新功能
2. **逐步迁移**: 新功能使用新的 API 接口
3. **配置优化**: 根据实际需求调整通知规则
4. **监控测试**: 观察新系统的运行状况和通知效果

## 故障排除

### 飞书通知失败
- 检查环境变量配置
- 确认机器人已加入目标群聊
- 验证 chat_id 格式正确

### 短信发送失败
- 检查阿里云短信配置
- 确认用户手机号格式正确
- 查看短信模板是否已审核通过

### 应用内通知问题
- 检查 Supabase 连接
- 确认数据库表结构正确
- 查看应用日志获取详细错误信息
