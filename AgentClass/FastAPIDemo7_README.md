# AgentClass Demo7 - 飞书群组通知测试

## 功能说明

这个演示程序展示了如何使用飞书API向群组发送各种类型的通知消息，基于通知系统的设计模式。

## 主要功能

### 🔧 核心功能
- **飞书API客户端**: 封装飞书开放平台API调用
- **访问令牌管理**: 自动获取和管理tenant_access_token
- **多种消息类型**: 支持文本消息、富文本消息、预警消息

### 📬 测试场景
1. **简单文本消息**: 基础的文本消息发送
2. **项目预警通知**: 模拟项目进度预警，包含详细信息
3. **订单通知**: 新订单报名通知
4. **里程碑通知**: 项目里程碑完成通知
5. **系统通知**: 系统维护、故障等通知
6. **批量通知**: 批量发送多种类型的通知

### 🎨 消息格式特色
- **预警级别标识**: 不同颜色的emoji标识重要级别
  - 🔴 高重要性 (high)
  - 🟡 普通重要性 (normal) 
  - 🟢 低重要性 (low)
- **结构化信息**: 清晰的键值对信息展示
- **时间戳**: 自动添加发送时间
- **详细信息**: 丰富的业务上下文信息

## 环境配置

### 1. 飞书应用配置

需要在飞书开放平台创建应用并获取以下信息：

```bash
# 飞书应用配置
FEISHU_APP_ID=cli_xxxxxxxxxx          # 应用ID
FEISHU_APP_SECRET=xxxxxxxxxxxxxxxx    # 应用密钥
FEISHU_CHAT_ID=oc_xxxxxxxxxxxxxxxx    # 目标群聊ID
```

### 2. 配置环境变量

**方法1**: 编辑项目根目录的 `.env` 文件
```bash
# 在项目根目录编辑 .env 文件
cd /path/to/aicraft-class-autogen
nano .env

# 添加以下配置
FEISHU_APP_ID=your_app_id_here
FEISHU_APP_SECRET=your_app_secret_here
FEISHU_CHAT_ID=your_chat_id_here
```

**方法2**: 直接设置环境变量（临时有效）
```bash
export FEISHU_APP_ID="your_app_id_here"
export FEISHU_APP_SECRET="your_app_secret_here"
export FEISHU_CHAT_ID="your_chat_id_here"
```

### 3. 获取飞书群聊ID的方法

1. **通过飞书客户端**:
   - 进入目标群聊
   - 点击群设置
   - 复制群ID（格式如: oc_xxxxx）

2. **通过API获取**:
   ```bash
   curl -X GET \
     "https://open.feishu.cn/open-apis/im/v1/chats" \
     -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
   ```

## 运行方法

### 1. 安装依赖
```bash
pip install requests
```

### 2. 配置环境变量
按照上面的环境配置步骤设置飞书应用信息。

### 3. 运行测试
```bash
# 进入项目根目录（确保能访问.env文件）
cd /path/to/aicraft-class-autogen

# 运行飞书通知测试
python AgentClass/FastAPIDemo7_FeishuNotification.py
```

### 4. 预期输出
```
🤖 AgentClass Demo7 - 飞书群组通知测试
🚀 开始飞书通知系统测试
==================================================

🔄 正在执行: 简单文本消息
=== 测试简单文本消息 ===
✅ 简单文本消息发送成功

🔄 正在执行: 项目预警通知
=== 测试项目预警通知 ===
✅ 项目预警通知发送成功

... (其他测试)

📊 测试结果统计:
✅ 成功: 6 项
❌ 失败: 0 项
🎉 成功的测试: 简单文本消息, 项目预警通知, 订单通知, 里程碑通知, 系统通知, 批量通知
🏁 飞书通知系统测试完成
```

## 消息示例

### 项目预警消息
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

### 订单通知消息
```
🟡 【订单报名通知】新订单报名 - 前端开发项目

• 订单类型: 前端开发
• 报名开发者: 李四
• 订单预算: ￥5000
• 项目周期: 2周
• 技术栈: Vue.js, Element-UI
• 客户要求: 响应式设计，兼容移动端

⏰ 发送时间: 2024-01-10 14:30:26
```

## 自定义扩展

### 1. 添加新的消息类型
```python
def test_custom_notification(self) -> Dict[str, Any]:
    """自定义通知测试"""
    custom_data = {
        "自定义字段1": "值1",
        "自定义字段2": "值2"
    }
    
    return self.feishu_client.send_warning_message(
        warning_type="自定义通知类型",
        title="自定义通知标题",
        details=custom_data,
        level="normal"
    )
```

### 2. 集成到通知系统
可以将此演示中的 `FeishuAPI` 类集成到现有的通知系统中：

```python
from AgentClass.FastAPIDemo7_FeishuNotification import FeishuAPI

# 在通知服务中使用
feishu_api = FeishuAPI(app_id, app_secret, chat_id)
result = feishu_api.send_warning_message("系统通知", "测试消息", details)
```

## 故障排除

### 常见问题

1. **Token获取失败**
   - 检查APP_ID和APP_SECRET是否正确
   - 确认应用状态为已启用

2. **消息发送失败**
   - 检查CHAT_ID是否正确
   - 确认机器人已加入目标群聊
   - 检查应用权限设置

3. **环境变量问题**
   - 确认环境变量已正确设置
   - 重启终端会话以加载新的环境变量

### 调试模式
程序内置了详细的日志输出，可以帮助诊断问题：
- INFO级别：正常操作信息
- WARNING级别：配置警告
- ERROR级别：错误详情

## 技术特点

### 架构设计
- **单一职责**: 每个类负责特定功能
- **错误处理**: 完善的异常处理机制
- **日志记录**: 详细的操作日志
- **配置管理**: 灵活的配置方式

### 扩展性
- **提供商模式**: 易于添加其他消息平台
- **模板系统**: 支持消息模板化
- **批量处理**: 支持批量消息发送
- **异步支持**: 可扩展为异步处理

### 安全性
- **环境变量**: 敏感信息通过环境变量管理
- **访问控制**: Token有效期管理
- **错误隐藏**: 避免敏感信息泄露

## 相关文档

- [飞书开放平台文档](https://open.feishu.cn/document/)
- [通知系统README](../AgentClass/notifications/README.md)
- [飞书机器人消息卡片](https://open.feishu.cn/document/ukTMukTMukTM/uYjNwUjL2YDM14iN2ATN)
