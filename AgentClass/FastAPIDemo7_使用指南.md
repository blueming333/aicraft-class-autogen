# FastAPIDemo7 使用指南

## 🎯 项目概述

FastAPIDemo7 是一个基于通知系统设计的飞书群组通知测试程序，演示了如何向飞书群组发送各种类型的结构化通知消息。

## 📁 文件结构

```
aicraft-class-autogen/                    # 项目根目录
├── .env.example                         # 环境变量配置示例
├── .env                                 # 环境变量配置文件（需手动创建）
└── AgentClass/
    ├── FastAPIDemo7_FeishuNotification.py  # 主程序文件
    ├── FastAPIDemo7_README.md             # 详细说明文档
    ├── FastAPIDemo7_使用指南.md             # 本使用指南
    ├── test_feishu_quick.py               # 快速连接测试
    └── notifications/                     # 通知系统模块（已存在）
        ├── notification_service.py
        ├── providers/
        │   └── feishu_provider.py
        └── types/
            └── enums.py
```

## 🚀 快速开始

### 1. 环境准备

```bash
# 1. 进入项目根目录
cd /path/to/aicraft-class-autogen

# 2. 安装依赖
pip install requests

# 3. 复制环境配置文件（如果不存在.env文件）
cp .env.example .env

# 4. 编辑项目根目录的.env文件，填入真实的飞书配置
nano .env
```

### 2. 飞书应用配置

在飞书开放平台 (https://open.feishu.cn) 创建应用：

1. **创建应用**
   - 登录飞书开放平台
   - 创建企业自建应用
   - 获取 App ID 和 App Secret

2. **配置权限**
   - 机器人 > 消息与群组 > 获取与发送单聊、群聊消息
   - 发布应用版本

3. **添加到群聊**
   - 在目标群聊中添加机器人
   - 获取群聊ID（格式：oc_xxxxxxxxx）

4. **配置环境变量**
   ```bash
   FEISHU_APP_ID=cli_xxxxxxxxx
   FEISHU_APP_SECRET=xxxxxxxxxxxxxxx
   FEISHU_CHAT_ID=oc_xxxxxxxxx
   ```

### 3. 运行测试

```bash
# 进入项目根目录（确保能访问根目录的.env文件）
cd /path/to/aicraft-class-autogen

# 快速连接测试
python AgentClass/test_feishu_quick.py

# 完整功能测试
python AgentClass/FastAPIDemo7_FeishuNotification.py
```

## 🧪 测试场景

### 场景1: 快速连接测试
```bash
cd /path/to/aicraft-class-autogen
python AgentClass/test_feishu_quick.py
```

**功能**：
- 检查环境变量配置
- 获取访问令牌
- 发送简单测试消息

**预期输出**：
```
🚀 飞书连接快速测试
==============================
🔍 检查飞书配置...
✓ 配置检查完成

🔑 获取访问令牌...
✓ 访问令牌获取成功

📤 发送测试消息...
✅ 测试消息发送成功！
消息ID: om_xxxxxxxxx

==============================
🎉 飞书连接测试成功！
✅ 可以运行完整的Demo7测试程序
```

### 场景2: 完整功能测试
```bash
cd /path/to/aicraft-class-autogen
python AgentClass/FastAPIDemo7_FeishuNotification.py
```

**测试内容**：
1. 简单文本消息
2. 项目预警通知
3. 订单报名通知
4. 里程碑完成通知
5. 系统维护通知
6. 批量通知发送

**消息示例**：

**项目预警通知**：
```
🔴 【项目提交预警】项目进度预警 - AI聊天机器人开发

• 项目名称: AI聊天机器人开发
• 开发者: 张三
• 连续无提交天数: 5天
• 历史提交总数: 12次
• 预警级别: 高
• 订单ID: ORDER-2024-001
• 预警原因: 项目进度严重滞后，需要及时关注

⏰ 发送时间: 2024-01-10 14:30:25
```

## 🔧 代码结构分析

### 核心类设计

#### 1. FeishuAPI 类
```python
class FeishuAPI:
    """飞书API客户端"""
    
    def __init__(self, app_id: str, app_secret: str, chat_id: str)
    def get_access_token(self) -> str
    def send_text_message(self, text: str) -> Dict[str, Any]
    def send_warning_message(self, warning_type: str, title: str, details: Dict[str, Any], level: str) -> Dict[str, Any]
    def is_available(self) -> bool
```

**特点**：
- 自动管理访问令牌
- 支持多种消息格式
- 完善的错误处理
- 状态检查功能

#### 2. FeishuNotificationDemo 类
```python
class FeishuNotificationDemo:
    """飞书通知演示类"""
    
    def test_simple_text(self) -> Dict[str, Any]
    def test_project_warning(self) -> Dict[str, Any]
    def test_order_notification(self) -> Dict[str, Any]
    def test_milestone_notification(self) -> Dict[str, Any]
    def test_system_notification(self) -> Dict[str, Any]
    def test_batch_notifications(self) -> Dict[str, Any]
    def run_all_tests(self)
```

**特点**：
- 模拟各种业务场景
- 结构化的测试方法
- 详细的结果统计
- 易于扩展新场景

### 消息格式设计

#### 预警级别标识
- 🔴 高重要性 (high) - 紧急问题，需立即处理
- 🟡 普通重要性 (normal) - 常规通知，需要关注
- 🟢 低重要性 (low) - 信息通知，可延后处理

#### 消息结构
```
[级别图标] 【通知类型】消息标题

• 字段1: 值1
• 字段2: 值2
• 字段3: 值3
...

⏰ 发送时间: YYYY-MM-DD HH:MM:SS
```

## 🔍 故障排除

### 常见问题及解决方案

#### 1. Token获取失败
**现象**：
```
❌ 获取令牌失败: {'code': 99991663, 'msg': 'App not found'}
```

**解决方案**：
- 检查 `FEISHU_APP_ID` 是否正确
- 确认应用状态为"已启用"
- 检查应用是否已发布版本

#### 2. 消息发送失败
**现象**：
```
❌ 消息发送失败: {'code': 230002, 'msg': 'bot not in chat'}
```

**解决方案**：
- 确认机器人已加入目标群聊
- 检查 `FEISHU_CHAT_ID` 格式是否正确（应以 `oc_` 开头）
- 确认群聊未被解散或机器人未被移除

#### 3. 权限不足
**现象**：
```
❌ 消息发送失败: {'code': 19001, 'msg': 'param invalid: no permission'}
```

**解决方案**：
- 在飞书开放平台检查应用权限配置
- 确认已申请"获取与发送单聊、群聊消息"权限
- 重新发布应用版本

#### 4. 环境变量问题
**现象**：
```
⚠️ 飞书配置不完整，请设置以下环境变量:
- FEISHU_APP_ID
- FEISHU_APP_SECRET  
- FEISHU_CHAT_ID
```

**解决方案**：
```bash
# 方法1: 编辑项目根目录的.env文件
cd /path/to/aicraft-class-autogen
echo "FEISHU_APP_ID=your_app_id" >> .env
echo "FEISHU_APP_SECRET=your_secret" >> .env
echo "FEISHU_CHAT_ID=your_chat_id" >> .env

# 方法2: 直接export（临时有效）
export FEISHU_APP_ID="your_app_id"
export FEISHU_APP_SECRET="your_secret"
export FEISHU_CHAT_ID="your_chat_id"
```

## 🎨 自定义扩展

### 添加新的通知类型

```python
def test_custom_notification(self) -> Dict[str, Any]:
    """自定义通知类型"""
    logger.info("=== 测试自定义通知 ===")
    
    custom_data = {
        "业务字段1": "业务值1",
        "业务字段2": "业务值2",
        "创建时间": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "处理状态": "待处理"
    }
    
    result = self.feishu_client.send_warning_message(
        warning_type="自定义业务通知",
        title="自定义通知标题",
        details=custom_data,
        level="normal"
    )
    
    return result
```

### 集成到现有系统

```python
# 导入Demo7的FeishuAPI
from FastAPIDemo7_FeishuNotification import FeishuAPI

class CustomNotificationService:
    def __init__(self):
        self.feishu_client = FeishuAPI(
            app_id=os.getenv('FEISHU_APP_ID'),
            app_secret=os.getenv('FEISHU_APP_SECRET'),
            chat_id=os.getenv('FEISHU_CHAT_ID')
        )
    
    def send_business_alert(self, title: str, details: dict, level: str = "normal"):
        """发送业务预警"""
        return self.feishu_client.send_warning_message(
            warning_type="业务预警",
            title=title,
            details=details,
            level=level
        )
```

## 📊 性能建议

### 1. 频率限制
- 飞书API有频率限制，建议在批量发送时添加延时
- 单个应用每分钟最多100条消息

```python
import time

# 批量发送时添加延时
for notification in notifications:
    result = send_notification(notification)
    time.sleep(0.6)  # 600ms延时，确保不超过频率限制
```

### 2. 错误重试
- 网络异常时实现重试机制
- 使用指数退避策略

```python
import time
import random

def send_with_retry(func, max_retries=3):
    for attempt in range(max_retries):
        try:
            return func()
        except Exception as e:
            if attempt == max_retries - 1:
                raise e
            
            # 指数退避
            delay = (2 ** attempt) + random.uniform(0, 1)
            time.sleep(delay)
```

### 3. 异步处理
- 对于大量通知，考虑使用异步处理
- 可以集成消息队列系统

## 🔗 相关资源

- [飞书开放平台](https://open.feishu.cn/)
- [飞书机器人开发指南](https://open.feishu.cn/document/ukTMukTMukTM/uYjNwUjL2YDM14iN2ATN)
- [消息卡片设计器](https://open.feishu.cn/tool/cardbuilder)
- [通知系统文档](./notifications/README.md)

## 📝 总结

FastAPIDemo7 演示了如何构建一个完整的飞书群组通知系统，包括：

✅ **完整的API封装** - 处理认证、消息发送、错误处理
✅ **多种消息格式** - 文本消息、预警消息、富文本消息  
✅ **业务场景模拟** - 项目预警、订单通知、系统通知等
✅ **结构化设计** - 清晰的类设计和模块化架构
✅ **详细的文档** - 使用指南、故障排除、扩展方案
✅ **测试友好** - 快速测试工具和完整测试套件

这个Demo可以作为学习飞书开放平台API的起点，也可以作为实际项目中通知系统的参考实现。
