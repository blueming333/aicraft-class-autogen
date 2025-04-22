# 基础测试案例

本目录包含AutoGen框架的基本功能测试案例。

## 环境变量设置

本项目使用`.env`文件管理API密钥和其他敏感配置。请按照以下步骤设置：

1. 复制`.env.example`文件并创建`.env`文件：
   ```bash
   cp .env.example .env
   ```

2. 编辑`.env`文件，填入您的API密钥和配置：
   ```
   # GitHub 配置
   GITHUB_TOKEN=your_actual_github_token
   
   # OpenAI 配置
   OPENAI_API_KEY=your_actual_api_key
   OPENAI_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
   ```

3. 安装dotenv库（如果尚未安装）：
   ```bash
   pip install python-dotenv
   # 或使用uv
   uv pip install python-dotenv
   ```

## 运行测试案例

1. **单智能体测试**
   ```bash
   python 1_BasicTest.py
   ```

2. **多智能体团队测试**
   ```bash
   python 2_RunTeam.py
   ```

3. **MCP GitHub工具测试**
   ```bash
   python 10_RunTeamStreamMcpGithub.py
   ```

## 注意事项

- 确保已安装所有必要的依赖（参见主README.md）
- 某些测试案例需要有效的API密钥
- GitHub API功能需要有效的GitHub令牌 