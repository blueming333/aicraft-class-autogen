# 第一节课大纲：Python基础 + FunctionCall基础

## 一、Python基础与FastAPI入门

### 1. Python语法基础回顾
- Python变量与数据类型（int、float、str、list、dict等）
- 基本控制结构（if、for、while）
- 函数定义与调用（def、参数、返回值）
- 模块与包的导入（import、from ... import ...）

### 2. FastAPI基础
- FastAPI简介与应用场景
- FastAPI项目结构与快速上手
- 路由与请求方法（GET、POST等）
- 请求参数与响应（Query、Path、Body、Response Model）

### 3. .env文件的使用
- .env文件作用与常见配置项
- 如何在FastAPI项目中加载.env（使用python-dotenv或pydantic的Settings）
- 环境变量的读取与管理

### 4. FastAPI启动与接口文档
- FastAPI项目的启动方式（uvicorn、命令行参数）
- 配置host、port、reload等参数
- Redoc与Swagger自动接口文档的生成与访问
- Redoc文档的定制与常见问题

---

## 二、FunctionCall基础与大模型工具调用

### 1. FunctionCall/Tools功能简介
- 什么是FunctionCall？为什么需要FunctionCall？
- 典型应用场景（如智能助手、自动化工具链等）

### 2. 支持FunctionCall的大模型介绍
- DeepSeek、Qwen3等主流支持tools/functioncall的大模型简介
- OpenAI function calling、Tool calling的基本原理

### 3. JSON输出与FunctionCall实践
- 如何让大模型输出结构化JSON数据
- FunctionCall的输入与输出格式
- 设计与注册自定义工具（function/tool schema设计）
- 通过API调用大模型实现FunctionCall（以DeepSeek/Qwen3为例）

### 4. 实战演示
- 现场演示：调用大模型实现基础的FunctionCall
- 让大模型根据指令自动调用工具并返回结构化结果
- 常见问题与调试技巧

---

## 课后建议
- 课后练习：用FastAPI实现一个简单的API，并让大模型通过FunctionCall调用该API
- 推荐阅读与资料：FastAPI官方文档、OpenAI Function Calling文档、DeepSeek/Qwen3官方文档
