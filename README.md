# Dinox API Python 客户端

[![PyPI version](https://badge.fury.io/py/dinox-api.svg)](https://badge.fury.io/py/dinox-api)
[![Python Version](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![Tests](https://github.com/JimEverest/DinoSync/actions/workflows/test.yml/badge.svg)](https://github.com/JimEverest/DinoSync/actions/workflows/test.yml)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

一个功能完整、易于使用的 Python 异步客户端库，用于与 Dinox AI 笔记服务进行交互。

---

## 📦 安装

### 方法一：通过 PyPI 安装（推荐）

```bash
pip install dinox-api
```

### 方法二：从源码安装

```bash
git clone https://github.com/JimEverest/DinoSync.git
cd DinoSync
pip install -e .
```

---

## ✨ 特性

- ✅ **完整的 API 覆盖** - 支持所有可用的 Dinox API 接口
- ✅ **异步支持** - 基于 aiohttp，性能优异
- ✅ **类型提示** - 完整的类型注解，IDE 友好
- ✅ **错误处理** - 详细的错误信息和异常处理
- ✅ **易于使用** - 简洁的 API 设计，上下文管理器支持
- ✅ **安全配置** - 使用 .env 文件管理敏感信息
- ✅ **全面测试** - 22 个测试用例，100% 通过率

---

## 🚀 快速开始

### 使用 PyPI 包（pip install dinox-api）

如果你通过 `pip install dinox-api` 安装，可以直接开始使用：

```python
import asyncio
import os
from dinox_client import DinoxClient  # 导入方式完全相同

async def main():
    # 方式1：从环境变量或 .env 文件自动加载 Token（推荐）
    token = os.environ.get('DINOX_API_TOKEN', 'YOUR_TOKEN')
    
    async with DinoxClient(api_token=token) as client:
        # 获取笔记列表
        notes = await client.get_notes_list()
        print(f"获取到 {len(notes)} 天的笔记")

asyncio.run(main())
```

**配置 Token 的三种方法：**

1. **环境变量（推荐）**
   ```bash
   export DINOX_API_TOKEN="your_token"  # Linux/Mac
   $env:DINOX_API_TOKEN="your_token"    # Windows PowerShell
   ```

2. **.env 文件（推荐）**
   ```
   # 创建 .env 文件
   DINOX_API_TOKEN=your_token
   ```

3. **代码中直接指定**
   ```python
   client = DinoxClient(api_token="YOUR_TOKEN")
   ```

**注意事项：**
- 📌 模块名是 `dinox_client`（下划线），不是 `dinox-api`（连字符）
- 📌 使用方法与源码安装完全相同
- 📌 支持所有文档中描述的功能和配置选项
- 📌 Token 可以从环境变量或 .env 文件自动加载

### 从源码使用

如果你是从 GitHub 克隆的项目，请按以下步骤操作：

#### 1. 安装依赖

```bash
pip install -r requirements.txt
```

#### 2. 配置 API Token

复制环境变量模板并配置您的 Token：

```bash
# Linux/Mac
cp env.example .env

# Windows
copy env.example .env
```

编辑 `.env` 文件：

```bash
DINOX_API_TOKEN=your_actual_token_here
```

#### 3. 基础使用

```python
import asyncio
import os
from dinox_client import DinoxClient

async def main():
    # 从环境变量或 .env 文件读取 Token
    token = os.environ.get('DINOX_API_TOKEN', 'YOUR_TOKEN')
    
    async with DinoxClient(api_token=token) as client:
        # 获取笔记列表
        notes = await client.get_notes_list()
        print(f"获取到 {len(notes)} 天的笔记")
        
        # 遍历笔记
        for day_note in notes:
            print(f"日期: {day_note['date']}")
            for note in day_note['notes']:
                print(f"  - {note['title']}")

asyncio.run(main())
```

---

## 📚 主要功能

### PyPI 包完整使用示例

通过 `pip install dinox-api` 安装后，直接使用：

```python
from dinox_client import DinoxClient
import asyncio
import os

async def example():
    # 从环境变量读取Token（推荐）
    token = os.environ.get('DINOX_API_TOKEN', 'YOUR_TOKEN')
    
    async with DinoxClient(api_token=token) as client:
        # 查询笔记（自动使用笔记服务器）
        notes = await client.get_notes_list()
        print(f"获取到 {len(notes)} 天的笔记")
        
        # 搜索笔记（自动使用AI服务器）
        results = await client.search_notes(["Python", "AI"])
        print(f"搜索结果: {len(results.get('content', ''))} 字符")
        
        # 创建笔记（自动使用AI服务器）
        await client.create_note("# 新笔记\n\n通过API创建")
            
# 运行
asyncio.run(example())
```

### 场景 1：查询笔记

```python
async with DinoxClient(api_token=token) as client:
    # 获取所有笔记
    notes = await client.get_notes_list()
    
    # 增量同步
    recent = await client.get_notes_list(last_sync_time="2025-10-18 00:00:00")
    
    # 根据 ID 查询
    note = await client.get_note_by_id("note-id-here")
```

### 场景 2：搜索和创建笔记

```python
async with DinoxClient(api_token=token) as client:
    # 搜索笔记
    result = await client.search_notes(["关键词"])
    print(result['content'])
    
    # 创建笔记
    await client.create_note("# 标题\n\n内容")
    
    # 获取卡片盒
    boxes = await client.get_zettelboxes()
```

### 场景 3：完整工作流

```python
async def complete_workflow():
    token = "YOUR_TOKEN"
    
    async with DinoxClient(api_token=token) as client:
        # 1. 同步笔记
        print("步骤1: 同步笔记...")
        notes = await client.get_notes_list()
        print(f"获取到 {len(notes)} 天的笔记")
        
        # 2. 搜索内容
        print("\n步骤2: 搜索笔记...")
        result = await client.search_notes(["Python", "API"])
        print(f"找到相关内容")
        
        # 3. 创建新笔记
        print("\n步骤3: 创建新笔记...")
        await client.create_note("# 新笔记\n\n通过 API 创建")
        print("创建成功")
```

---

## 🧪 运行测试

```bash
# 运行所有测试
python -m pytest test_dinox_client.py -v

# 查看示例
python example.py
```

**测试结果**：
```
======================== 22 passed in 3.79s ========================
```

---

## 📖 API 参考

### ✨ v0.2.0 自动服务器路由

**无需配置服务器！** 客户端自动根据调用的方法选择正确的服务器：

```python
async with DinoxClient(api_token="YOUR_TOKEN") as client:
    # 自动使用笔记服务器
    notes = await client.get_notes_list()
    note = await client.get_note_by_id("note-id")
    
    # 自动使用 AI 服务器
    results = await client.search_notes(["关键词"])
    await client.create_note("# 新笔记\n\n内容")
    boxes = await client.get_zettelboxes()
```

**服务器映射（自动处理）：**

| 服务器 | URL | 方法 |
|--------|-----|------|
| 笔记服务器 | `dinoai.chatgo.pro` | `get_notes_list`, `get_note_by_id`, `update_note` |
| AI服务器 | `aisdk.chatgo.pro` | `search_notes`, `create_note`, `get_zettelboxes` |

### 可用的方法

| 方法 | 功能 | 服务器 | 状态 |
|------|------|--------|------|
| `get_notes_list(...)` | 获取笔记列表，支持增量同步 | 笔记服务器 | ✅ 可用 |
| `get_note_by_id(note_id)` | 根据 ID 查询笔记 | 笔记服务器 | ✅ 可用 |
| `search_notes(keywords)` | 搜索笔记 | AI服务器 | ✅ 可用 |
| `get_zettelboxes()` | 获取卡片盒列表 | AI服务器 | ✅ 可用 |
| `create_note(content, ...)` | 创建笔记（支持卡片盒） | AI服务器 | ✅ 可用 |
| `create_text_note(content)` | 创建文字笔记 | AI服务器 | ✅ 可用 |
| `update_note(note_id, content_md)` | 更新笔记内容 | 笔记服务器 | ✅ 可用 |
| `format_sync_time(dt)` | 格式化同步时间 | 本地 | ✅ 可用 |

### 📚 API 参考

**完整API文档:** 查看 [API.md](API.md)

常用方法快速参考：

```python
# 查询
await client.get_notes_list(last_sync_time="2025-10-20 00:00:00")
await client.get_note_by_id(note_id)
await client.search_notes(["关键词"])

# 创建/更新
await client.create_note(content="# 标题\n\n内容")
await client.update_note(note_id, content_md)

# 卡片盒
await client.get_zettelboxes()

# 工具
DinoxClient.format_sync_time(datetime.now())
```

**详细参数说明:** 见 [API.md](API.md)

---

## ⚠️ 错误处理

```python
from dinox_client import DinoxAPIError

try:
    async with DinoxClient(api_token=token) as client:
        notes = await client.get_notes_list()
except DinoxAPIError as e:
    print(f"错误: [{e.code}] {e.message}")
    print(f"HTTP 状态: {e.status_code}")
```

---

## 📁 更多文档

- **API 参考:** [API.md](API.md) - 完整方法文档
- **开发指南:** [DEVELOPMENT.md](DEVELOPMENT.md) - 测试、发布流程
- **故障排查:** [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - 常见问题解决
- **版本历史:** [CHANGELOG.md](CHANGELOG.md) - 更新记录

---

## 📖 常见问题

**Q: 包名和模块名为什么不一样？**  
A: 安装用 `dinox-api`，导入用 `dinox_client`（Python限制）

**Q: 遇到 404 错误？**  
A: 查看 [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

**Q: 如何运行测试？**  
A: `pytest test_dinox_client.py -v` 或 `python health_check.py`

**Q: Token 在哪获取？**  
A: 联系 Dinox 管理员

**更多问题:** 见 [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

---

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE)

## 📞 支持

- **GitHub:** https://github.com/JimEverest/DinoSync
- **PyPI:** https://pypi.org/project/dinox-api/
- **官网:** https://dinox.info

