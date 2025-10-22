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

通过 `pip install dinox-api` 安装后，以下是完整的使用示例：

```python
# 1. 基础配置
from dinox_client import DinoxClient, DinoxConfig
import asyncio
import os

# 方式一：从环境变量或 .env 文件读取（推荐）
token = os.environ.get('DINOX_API_TOKEN', 'YOUR_TOKEN')
client = DinoxClient(api_token=token)

# 方式二：直接传入 token
client = DinoxClient(api_token="YOUR_TOKEN")

# 方式三：使用配置对象（更灵活）
config = DinoxConfig(
    api_token=token,  # 使用环境变量中的 token
    base_url="https://api.chatgo.pro",  # 默认笔记服务器
    timeout=30.0
)
client = DinoxClient(config=config)

# 注意：DinoxClient 不会自动读取环境变量，需要手动传入
# token = os.environ.get('DINOX_API_TOKEN')
# client = DinoxClient(api_token=token)

# 2. 异步使用示例
async def example():
    token = os.environ.get('DINOX_API_TOKEN', 'YOUR_TOKEN')
    async with DinoxClient(api_token=token) as client:
        # 获取笔记
        notes = await client.get_notes_list()
        
        # 搜索笔记（需要使用 AI 服务器）
        ai_config = DinoxConfig(
            api_token=token,
            base_url="https://aisdk.chatgo.pro"
        )
        async with DinoxClient(config=ai_config) as ai_client:
            results = await ai_client.search_notes(["Python", "AI"])
            
# 运行异步函数
asyncio.run(example())
```

### 场景 1：查询和管理笔记（笔记服务器）

```python
# 使用默认配置（笔记服务器）
async with DinoxClient(api_token=token) as client:
    # 获取所有笔记
    notes = await client.get_notes_list()
    
    # 增量同步
    recent = await client.get_notes_list(last_sync_time="2025-10-18 00:00:00")
    
    # 根据 ID 查询
    note = await client.get_note_by_id("note-id-here")
```

### 场景 2：搜索和创建笔记（AI 服务器）

```python
from dinox_client import DinoxClient, DinoxConfig

# 配置使用 AI 服务器
config = DinoxConfig(
    api_token=token,
    base_url="https://aisdk.chatgo.pro"  # AI 服务器
)

async with DinoxClient(config=config) as client:
    # 搜索笔记
    result = await client.search_notes(["关键词"])
    print(result['content'])
    
    # 创建笔记
    await client.create_note("# 标题\n\n内容")
    
    # 获取卡片盒
    boxes = await client.get_zettelboxes()
```

### 场景 3：完整应用示例

```python
import json
from pathlib import Path

async def complete_workflow():
    token = "YOUR_TOKEN"
    
    # 1. 使用笔记服务器同步笔记
    print("步骤1: 同步笔记...")
    async with DinoxClient(api_token=token) as client:
        notes = await client.get_notes_list()
        print(f"获取到 {len(notes)} 天的笔记")
    
    # 2. 使用 AI 服务器搜索特定内容
    print("\n步骤2: 搜索笔记...")
    config_ai = DinoxConfig(
        api_token=token,
        base_url="https://aisdk.chatgo.pro"
    )
    async with DinoxClient(config=config_ai) as client:
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

### ⚠️ 重要说明：两个 API 服务器

Dinox 目前有两个 API 服务器，支持不同的功能：

| 服务器 | URL | 支持的 API |
|--------|-----|-----------|
| **笔记服务器** | `https://dinoai.chatgo.pro` | `get_notes_list`, `get_note_by_id` |
| **AI服务器** | `https://aisdk.chatgo.pro` | `search_notes`, `create_note`, `get_zettelboxes` |

**默认使用笔记服务器**。如需使用搜索和创建功能，请配置使用 AI 服务器：

```python
from dinox_client import DinoxClient, DinoxConfig

# 使用 AI 服务器
config = DinoxConfig(
    api_token="YOUR_TOKEN",
    base_url="https://aisdk.chatgo.pro"  # AI 服务器
)
client = DinoxClient(config=config)
```

### 🆕 v0.2.0 新特性：自动服务器路由

从 v0.2.0 开始，客户端支持**自动服务器路由**，无需手动选择服务器：

```python
# v0.2.0+ 自动路由（推荐）
async with DinoxClient(api_token="YOUR_TOKEN") as client:
    # 自动使用笔记服务器
    notes = await client.get_notes_list()
    
    # 自动使用 AI 服务器
    results = await client.search_notes(["关键词"])
    boxes = await client.get_zettelboxes()
```

如需禁用自动路由并手动控制：
```python
config = DinoxConfig(
    api_token="YOUR_TOKEN",
    base_url="https://aisdk.chatgo.pro",
    auto_route=False  # 禁用自动路由
)
```

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

### 📚 完整 API 参考

#### DinoxClient 类

```python
class DinoxClient(api_token: str = None, config: DinoxConfig = None, auto_route: bool = True)
```

**参数：**
- `api_token` (str, optional): API Token (JWT格式)
- `config` (DinoxConfig, optional): 配置对象，如果提供则忽略 api_token
- `auto_route` (bool, optional): 是否启用自动服务器路由，默认 True (v0.2.0+)

#### DinoxConfig 类

```python
@dataclass
class DinoxConfig:
    api_token: str                    # API Token（必需）
    base_url: str = "https://dinoai.chatgo.pro"  # 基础 URL
    timeout: int = 30                 # 超时时间（秒）
    auto_route: bool = True          # 自动路由 (v0.2.0+)
```

#### 1. get_notes_list()

获取笔记列表，支持增量同步。

```python
async def get_notes_list(
    last_sync_time: str = "1900-01-01 00:00:00",
    template: str = None
) -> List[Dict[str, Any]]
```

**参数：**
- `last_sync_time` (str): 上次同步时间，格式 "YYYY-MM-DD HH:mm:ss"
- `template` (str, optional): Mustache 模板字符串

**返回：** 按日期分组的笔记列表

**示例：**
```python
# 获取所有笔记
notes = await client.get_notes_list()

# 增量同步
recent_notes = await client.get_notes_list(
    last_sync_time="2025-10-20 00:00:00"
)

# 遍历结果
for day_note in notes:
    print(f"日期: {day_note['date']}")
    for note in day_note['notes']:
        print(f"  - {note['title']}: {note['noteId']}")
```

#### 2. get_note_by_id()

根据 ID 获取笔记详情。

```python
async def get_note_by_id(note_id: str) -> Dict[str, Any]
```

**参数：**
- `note_id` (str): 笔记的唯一标识符（UUID）

**返回：** 笔记详情字典

**示例：**
```python
note = await client.get_note_by_id("0199eb0d-fccc-7dc8-82da-7d32be3e668b")
print(f"标题: {note['title']}")
print(f"内容: {note['content']}")
print(f"创建时间: {note['createTime']}")
```

#### 3. search_notes()

搜索笔记内容。

```python
async def search_notes(keywords: List[str]) -> Dict[str, Any]
```

**参数：**
- `keywords` (List[str]): 搜索关键词列表

**返回：** 包含搜索结果的字典

**示例：**
```python
results = await client.search_notes(["Python", "异步", "API"])
content = results.get('content', '')
print(f"找到内容: {content[:200]}...")
```

#### 4. create_note()

创建新笔记，支持卡片盒。

```python
async def create_note(
    content: str,
    note_type: str = "note",
    zettelbox_ids: List[str] = None
) -> Dict[str, Any]
```

**参数：**
- `content` (str): 笔记内容（支持 Markdown）
- `note_type` (str): 笔记类型，"note" 或 "crawl"，默认 "note"
- `zettelbox_ids` (List[str], optional): 卡片盒 ID 列表

**返回：** 创建结果

**示例：**
```python
# 创建简单笔记
result = await client.create_note(
    content="# 我的笔记\n\n这是笔记内容"
)

# 创建带卡片盒的笔记
result = await client.create_note(
    content="# 项目笔记\n\n重要内容...",
    note_type="note",
    zettelbox_ids=["box-id-1", "box-id-2"]
)
```

#### 5. create_text_note()

创建纯文本笔记。

```python
async def create_text_note(content: str) -> Dict[str, Any]
```

**参数：**
- `content` (str): 笔记文本内容

**返回：** 创建结果

**示例：**
```python
result = await client.create_text_note("这是一条简单的文本笔记")
```

#### 6. update_note()

更新现有笔记。

```python
async def update_note(note_id: str, content_md: str) -> Dict[str, Any]
```

**参数：**
- `note_id` (str): 要更新的笔记 ID
- `content_md` (str): 新的笔记内容（Markdown 格式）

**返回：** 更新结果

**示例：**
```python
result = await client.update_note(
    note_id="0199eb0d-fccc-7dc8-82da-7d32be3e668b",
    content_md="# 更新后的标题\n\n更新后的内容..."
)
```

#### 7. get_zettelboxes()

获取所有卡片盒列表。

```python
async def get_zettelboxes() -> List[Dict[str, Any]]
```

**返回：** 卡片盒列表

**示例：**
```python
boxes = await client.get_zettelboxes()
for box in boxes:
    print(f"卡片盒: {box.get('name', '未命名')}")
    print(f"  ID: {box.get('id')}")
```

#### 8. format_sync_time()

格式化时间为同步时间格式。

```python
@staticmethod
def format_sync_time(dt: datetime = None) -> str
```

**参数：**
- `dt` (datetime, optional): 要格式化的时间，默认为当前时间

**返回：** 格式化的时间字符串 "YYYY-MM-DD HH:mm:ss"

**示例：**
```python
# 当前时间
current_sync_time = DinoxClient.format_sync_time()

# 指定时间
from datetime import datetime
specific_time = datetime(2025, 10, 20, 15, 30, 0)
formatted = DinoxClient.format_sync_time(specific_time)
```

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

## 🎯 最佳实践

### 1. 使用上下文管理器

```python
# ✅ 推荐：自动管理连接
async with DinoxClient(api_token=token) as client:
    notes = await client.get_notes_list()

# ❌ 不推荐：需要手动管理
client = DinoxClient(api_token=token)
await client.connect()
try:
    notes = await client.get_notes_list()
finally:
    await client.close()
```

### 2. 使用环境变量管理 Token

```python
import os
from dotenv import load_dotenv

load_dotenv()
token = os.environ.get("DINOX_API_TOKEN")
```

### 3. 实现增量同步

只获取更新的笔记，减少数据传输和处理时间。

---

## 📁 项目结构

```
dinox_api_py/
├── dinox_client.py           # 核心客户端库
├── test_dinox_client.py      # 测试套件（22个测试）
├── test_pypi_complete.py     # PyPI包完整功能测试
├── test_pypi_install.py      # PyPI包简单导入测试
├── demo_pypi_usage.py        # PyPI包使用演示
├── example.py                # 使用示例
├── setup.py                  # PyPI包配置
├── pyproject.toml           # 现代Python打包配置
├── LICENSE                  # MIT许可证
├── requirements.txt          # 项目依赖
├── .env                      # 环境变量（不提交到Git）
├── env.example              # 环境变量模板
├── .gitignore               # Git忽略文件
├── README.md                # 本文件
├── TESTING_GUIDE.md         # 测试指南
├── PYPI_SETUP_GUIDE.md      # PyPI发布指南
├── .github/                 # GitHub Actions工作流
│   └── workflows/
│       ├── test.yml         # 自动测试
│       └── publish-to-pypi.yml  # 自动发布
└── docs/                    # 详细文档
    ├── Python客户端使用文档.md
    ├── 获取笔记列表（同步接口）.md
    └── ...
```

---

## 🔧 配置选项

### DinoxConfig

```python
from dinox_client import DinoxClient, DinoxConfig

config = DinoxConfig(
    api_token="YOUR_TOKEN",              # 必需
    base_url="https://dinoai.chatgo.pro", # 可选
    timeout=30                            # 可选，单位：秒
)

client = DinoxClient(config=config)
```

---

## 📊 性能

在标准网络条件下的性能表现：

- 单次获取笔记列表：~1.2秒
- 5个并发请求：~1.5秒（总计）
- 平均响应时间：~0.3秒/请求

---

## 🧪 测试

### 运行测试脚本

项目包含完整的测试脚本，可以验证 PyPI 包是否正常工作：

```bash
# 1. 安装包
pip install dinox-api

# 2. 配置 Token（可选）
echo "DINOX_API_TOKEN=your_token" > .env

# 3. 运行测试
python test_pypi_complete.py  # 完整功能测试
python test_pypi_install.py   # 简单导入测试
python demo_pypi_usage.py     # 使用演示
```

测试脚本会自动从环境变量或 .env 文件加载 Token。

更多测试信息请查看 [TESTING_GUIDE.md](TESTING_GUIDE.md)

---

## 🛠️ 故障排除

### 问题：找不到 DINOX_API_TOKEN

**解决方案**：
1. 确认已创建 `.env` 文件
2. 检查 Token 配置格式：`DINOX_API_TOKEN=your_token_here`
3. 确保没有多余的空格或引号

### 问题：API 返回 404 错误

**原因**：该 API 端点暂未部署

**解决方案**：使用其他可用的 API 方法，参考上面的 API 状态表

---

## ❓ 常见问题

### 1. PyPI 包名与模块名的区别是什么？

- **安装时使用**: `dinox-api`（连字符）
  ```bash
  pip install dinox-api
  ```
- **导入时使用**: `dinox_client`（下划线）
  ```python
  from dinox_client import DinoxClient
  ```
- **原因**: Python 模块名不支持连字符，但 PyPI 包名可以使用

### 2. PyPI 安装和源码安装有什么区别？

**没有任何区别！** 两种安装方式：
- 功能完全相同
- API 完全相同
- 使用方法完全相同

唯一的区别是安装方式：
- PyPI: `pip install dinox-api`（更方便，自动处理依赖）
- 源码: `git clone` + `pip install -r requirements.txt`（可以修改源码）

### 3. 如何选择服务器地址？

- **笔记服务器** (`https://api.chatgo.pro`): 
  - 用于: 获取笔记列表、查询笔记详情、同步笔记
  - 特点: 只读操作，稳定可靠
  
- **AI 服务器** (`https://aisdk.chatgo.pro`): 
  - 用于: 搜索笔记、创建笔记、获取卡片盒
  - 特点: 支持写入操作，AI 功能

### 4. Token 在哪里获取？

联系 Dinox 管理员获取您的 API Token。获取后请妥善保管，避免泄露。

### 5. 为什么要使用异步？

- 提高并发性能
- 非阻塞 I/O 操作
- 更好的资源利用
- 符合现代 Python 开发趋势

---

## 📄 许可证

本项目采用 MIT 许可证。

---

## 📞 技术支持

- **Email**: zmyjust@gmail.com
- **GitHub**: https://github.com/ryzencool/dinox-sync
- **官网**: https://dinox.info
- **详细文档**: [docs/Python客户端使用文档.md](docs/Python客户端使用文档.md)

---

## 🙏 致谢

感谢 Dinox 团队提供优秀的 API 服务！

---

**开始使用 Dinox Python Client，让笔记管理更简单！** 🎉

