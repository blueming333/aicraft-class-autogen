# AIAgent工作流架构设计

## 系统概述

本系统是一个基于PostgreSQL数据存储、MCP协议通信、多Agent协作处理和智能通知分发的完整AIAgent工作流架构。系统通过自然语言与数据库交互，实现复杂业务逻辑处理和多渠道通知分发。

## 架构流程图

![AIAgent架构图](image.png)

## 详细架构说明

### 1. 数据存储层 (PostgreSQL)

**核心组件**：
- PostgreSQL数据库作为主要数据存储
- 存储用户数据、项目数据、订单数据、通知记录等

**特点**：
- 🗄️ 大容量数据存储
- 🔍 支持复杂查询
- 📊 数据关系管理
- 🔒 事务一致性保证

### 2. MCP通信层 (Model Context Protocol)

**核心组件**：
```
PostgreSQL MCP Server ←→ 自然语言查询接口 ←→ SQL查询解析器
```

**功能特性**：
- 🤖 自然语言到SQL的智能转换
- 📡 MCP协议标准化通信
- 🔄 实时数据查询能力
- 🛡️ 查询安全性控制

**工作流程**：
1. Agent发送自然语言查询请求
2. MCP Server解析自然语言意图
3. 生成对应的SQL查询语句
4. 执行查询并返回结构化数据

### 3. 多Agent协作层

**协作架构**：
```
协调器Agent
    ├── 数据分析Agent (数据清洗、统计分析)
    ├── 业务逻辑Agent (业务规则处理)
    ├── 决策制定Agent (智能决策算法)
    └── 结果生成Agent (输出格式化)
```

**各Agent职责**：

| Agent类型 | 主要职责 | 输入 | 输出 |
|-----------|----------|------|------|
| **协调器Agent** | 任务分发、流程控制 | 用户请求 | 任务分配 |
| **数据分析Agent** | 数据清洗、统计分析 | 原始数据 | 分析报告 |
| **业务逻辑Agent** | 业务规则验证、处理 | 分析结果 | 业务结果 |
| **决策制定Agent** | 策略制定、风险评估 | 业务结果 | 决策方案 |
| **结果生成Agent** | 格式化输出、报告生成 | 决策方案 | 最终结果 |

**协作模式**：
- 🔄 **流水线模式**: 数据依次通过各Agent处理
- 🤝 **协作模式**: Agents之间可以相互咨询
- 🧠 **集体智能**: 多个视角综合决策

### 4. 消息中心 - 通知工厂

**架构组件**：
```
NotificationService (核心服务)
├── RulesManager (规则引擎)
├── TemplateManager (模板引擎)
└── Providers (通知提供商)
    ├── SMS Provider (短信通知)
    ├── InApp Provider (应用内通知)
    └── Feishu Provider (飞书通知)
```

**通知规则矩阵**：

| 业务场景 | 通知类型 | 重要性 | 应用内 | 短信 | 飞书 | 触发条件 |
|---------|---------|--------|-------|------|------|---------|
| 📝 **订单报名** | ORDER | NORMAL | ✅ | ❌ | ❌ | 有开发者报名 |
| 💼 **发送Offer** | ORDER | HIGH | ✅ | ❌ | ✅ | Offer邀请发送 |
| 📋 **合同签署** | ORDER | HIGH | ✅ | ❌ | ✅ | 开发者签署合同 |
| 🎯 **里程碑完成** | PROJECT | HIGH | ✅ | ❌ | ✅ | 项目节点达成 |
| 💰 **里程碑托管** | PAYMENT | NORMAL | ✅ | ❌ | ❌ | 资金托管确认 |
| ⚠️ **严重逾期预警** | PROJECT | HIGH | ✅ | ✅ | ✅ | 5天+无提交 |

### 5. 通知发送渠道

**短信通知 (SMS)**：
- 🚨 仅最严重的业务预警
- 📱 通过阿里云短信API
- ⚡ 实时触达用户

**应用内通知 (InApp)**：
- 📋 所有类型通知都发送
- 💾 持久化存储到数据库
- 🌐 支持中英文本地化

**飞书通知 (Feishu)**：
- 💬 管理层监控通道
- 🤖 通过飞书机器人API
- 📊 业务指标预警

## 数据流详解

### 完整业务流程

```mermaid
sequenceDiagram
    participant User as 用户/系统触发
    participant Coord as 协调器Agent
    participant MCP as MCP服务器
    participant PG as PostgreSQL
    participant Agents as 业务Agents
    participant NotifSvc as 通知服务
    participant Providers as 通知提供商

    User->>Coord: 发起业务请求
    Coord->>MCP: 自然语言查询
    MCP->>PG: SQL查询执行
    PG-->>MCP: 返回数据结果
    MCP-->>Coord: 结构化数据
    
    Coord->>Agents: 分发处理任务
    
    par 并行处理
        Agents->>Agents: 数据分析
    and
        Agents->>Agents: 业务逻辑
    and
        Agents->>Agents: 决策制定
    end
    
    Agents->>Coord: 汇总处理结果
    Coord->>NotifSvc: 生成通知请求
    
    NotifSvc->>NotifSvc: 规则匹配
    NotifSvc->>NotifSvc: 模板渲染
    
    par 多渠道发送
        NotifSvc->>Providers: SMS通知
    and
        NotifSvc->>Providers: 应用内通知
    and
        NotifSvc->>Providers: 飞书通知
    end
    
    Providers-->>User: 通知送达
```

### 关键技术特性

**🔄 异步处理**：
- Agent间采用异步协作模式
- 通知发送采用异步队列
- 提高系统响应性能

**🛡️ 容错机制**：
- MCP连接断线重连
- Agent异常自动恢复
- 通知发送失败重试

**📈 可扩展性**：
- 支持新增Agent类型
- 支持新增通知渠道
- 支持自定义业务规则

**🔍 可观测性**：
- 完整的日志追踪
- 性能监控指标
- 业务指标统计

## 部署配置

### 环境变量配置

```bash
# PostgreSQL配置
DATABASE_URL=postgresql://user:pass@localhost:5432/dbname

# MCP服务配置  
MCP_SERVER_URL=http://localhost:3000
MCP_PROTOCOL_VERSION=2024-11-05

# Agent配置
AGENT_CONCURRENCY_LIMIT=10
AGENT_TIMEOUT_SECONDS=30

# 飞书配置
FEISHU_APP_ID=cli_your_app_id
FEISHU_APP_SECRET=your_app_secret
FEISHU_CHAT_ID=oc_your_chat_id

# 短信配置
ALIBABA_CLOUD_ACCESS_KEY_ID=your_access_key
ALIBABA_CLOUD_ACCESS_KEY_SECRET=your_secret

# 通知配置
NOTIFICATION_BATCH_SIZE=100
NOTIFICATION_RETRY_COUNT=3
```

### 系统依赖

```txt
# 核心依赖
autogen>=0.2.0              # 多Agent框架
asyncpg>=0.29.0             # PostgreSQL异步连接
mcp>=1.0.0                  # Model Context Protocol
fastapi>=0.104.1            # API服务框架
pydantic>=2.5.0             # 数据验证

# 通知依赖
alibabacloud-dysmsapi20170525>=3.0.0  # 阿里云短信
httpx>=0.25.0               # HTTP客户端
jinja2>=3.1.2               # 模板引擎
```

## 监控与维护

### 关键监控指标

| 监控维度 | 指标名称 | 正常范围 | 告警阈值 |
|---------|---------|---------|---------|
| **数据库** | 查询响应时间 | < 100ms | > 500ms |
| **MCP** | 连接成功率 | > 99% | < 95% |
| **Agent** | 任务完成率 | > 95% | < 90% |
| **通知** | 发送成功率 | > 98% | < 95% |

### 维护建议

1. **定期数据清理**: 清理过期的通知记录
2. **性能调优**: 优化SQL查询和Agent算法
3. **安全更新**: 定期更新依赖库版本
4. **备份策略**: 实现数据库自动备份

## 扩展方向

### 短期扩展

- 🔄 **Agent动态扩容**: 根据负载自动调整Agent数量
- 📊 **实时监控面板**: 可视化系统运行状态
- 🌐 **多语言支持**: 扩展更多语言的通知模板

### 中期扩展

- 🧠 **AI决策优化**: 集成更先进的AI模型
- 📱 **移动端推送**: 支持iOS/Android推送通知
- 🔌 **插件系统**: 支持第三方扩展开发

### 长期规划

- ☁️ **云原生部署**: Kubernetes容器化部署
- 🌍 **多地域部署**: 支持全球化服务部署
- 🤖 **智能运维**: AI驱动的自动化运维体系

---

## 总结

本架构设计实现了从数据存储、自然语言交互、多Agent协作到智能通知分发的完整工作流。通过模块化设计和标准化接口，系统具备良好的可扩展性和可维护性，能够满足复杂业务场景的需求。

**核心优势**：
- 🔄 **端到端自动化**: 从数据查询到通知发送全流程自动化
- 🤖 **智能化处理**: 多Agent协作实现复杂业务逻辑
- 📢 **精准化通知**: 基于规则引擎的智能通知分发
- 🛠️ **高可扩展性**: 模块化架构支持灵活扩展
