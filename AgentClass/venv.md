# Python 3.12 安装与虚拟环境（venv）使用教程

本教程详细介绍如何在本地安装 Python 3.12，并使用 `python -m venv` 创建和管理独立虚拟环境，适用于 macOS、Linux 和 Windows 用户。

---

## 一、安装 Python 3.12

### 1. macOS
- 推荐使用 [Homebrew](https://brew.sh/) 安装：
  ```bash
  brew install python@3.12
  ```
- 安装后可用 `python3.12 --version` 验证。

### 2. Linux（以 Ubuntu 为例）
- 添加 deadsnakes 源并安装：
  ```bash
  sudo add-apt-repository ppa:deadsnakes/ppa
  sudo apt update
  sudo apt install python3.12 python3.12-venv python3.12-dev
  ```
- 验证安装：
  ```bash
  python3.12 --version
  ```

### 3. Windows
- 访问 [Python 官网](https://www.python.org/downloads/release/python-3120/) 下载对应的安装包并安装。
- 安装时建议勾选“Add Python to PATH”。
- 安装后在命令行输入：
  ```cmd
  python --version
  # 或
  py -3.12 --version
  ```

---

## 二、使用 venv 创建独立虚拟环境

### 1. 创建虚拟环境
- 在项目根目录下执行：
  ```bash
  python3.12 -m venv venv
  ```
  这将在当前目录下创建一个名为 `venv` 的虚拟环境文件夹。

### 2. 激活虚拟环境
- **macOS/Linux**：
  ```bash
  source venv/bin/activate
  ```
- **Windows（CMD）**：
  ```cmd
  venv\Scripts\activate
  ```
- **Windows（PowerShell）**：
  ```powershell
  .\venv\Scripts\Activate.ps1
  ```
- 激活后命令行前面会出现 `(venv)`，表示已进入虚拟环境。

### 3. 退出虚拟环境
- 任何平台下都可输入：
  ```bash
  deactivate
  ```

---

## 三、可选方案：使用 conda 管理虚拟环境

如果你已安装 [Anaconda](https://www.anaconda.com/products/distribution) 或 [Miniconda](https://docs.conda.io/en/latest/miniconda.html)，可以用 conda 管理 Python 版本和虚拟环境。

### 1. 创建并激活 Python 3.12 虚拟环境
```bash
conda create -n myenv python=3.12
conda activate myenv
```
- `myenv` 为虚拟环境名称，可自定义。
- 激活后，环境前会出现 `(myenv)`。

### 2. 安装依赖
```bash
pip install -r requirements.txt
```
- conda 环境中同样可以用 pip 安装 requirements.txt。
- 也可用 conda 安装部分常用包，例如：
  ```bash
  conda install numpy pandas
  ```

### 3. 退出环境
```bash
conda deactivate
```

---

## 四、安装依赖（requirements.txt）

1. 确保已激活虚拟环境。
2. 在项目根目录下执行：
   ```bash
   pip install -r requirements.txt
   ```
3. 安装完成后，所有依赖包都只会安装在当前虚拟环境中，不影响全局 Python。

---

## 五、常见问题
- 如果 `python3.12` 命令不存在，可尝试 `python3` 或 `python`，并用 `python --version` 检查版本。
- pip 未安装或不可用时，可用 `python3.12 -m ensurepip` 安装。
- requirements.txt 文件需提前准备好，格式为每行一个包名及可选版本号。

---

## 参考资料
- [Python 官方文档](https://docs.python.org/zh-cn/3.12/library/venv.html)
- [pip 官方文档](https://pip.pypa.io/zh/stable/)
- [conda 官方文档](https://docs.conda.io/projects/conda/zh-cn/latest/index.html) 