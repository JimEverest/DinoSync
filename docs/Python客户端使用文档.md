# Dinox Python 异步客户端使用文档

一个功能完整的 Python 异步客户端库，用于与 Dinox AI 笔记服务进行交互。

---

## 📦 安装

### 依赖要求

- Python 3.8+
- aiohttp >= 3.9.0
- pytest >= 7.4.0 (仅用于测试)
- pytest-asyncio >= 0.21.0 (仅用于测试)

### 安装依赖

```bash
pip install -r requirements.txt
```

或手动安装核心依赖：

```bash
pip install aiohttp
```

---

## 🚀 快速开始

### 基础用法

```python
import asyncio
from dinox_client import DinoxClient

async def main():
    # 使用上下文管理器（推荐）
    async with DinoxClient(api_token="YOUR_TOKEN_HERE") as client:
        # 获取笔记列表
        notes = await client.get_notes_list()
        print(f"获取到 {len(notes)} 天的笔记")
        
        # 遍历笔记
        for day_note in notes:
            print(f"\n日期: {day_note['date']}")
            for note in day_note['notes']:
                print(f"  - {note['title']}")

if __name__ == "__main__":
    asyncio.run(main())
```

### 完整示例

```python
import asyncio
from dinox_client import DinoxClient, DinoxConfig, DinoxAPIError
from datetime import datetime

async def full_example():
    # 方式1: 直接使用 Token
    async with DinoxClient(api_token="YOUR_TOKEN") as client:
        try:
            # 1. 获取所有笔记
            notes = await client.get_notes_list()
            print(f"✓ 获取到 {len(notes)} 天的笔记")
            
            # 2. 增量同步
            recent_notes = await client.get_notes_list(
                last_sync_time="2025-10-18 00:00:00"
            )
            print(f"✓ 增量同步获取 {len(recent_notes)} 天的笔记")
            
            # 3. 搜索笔记
            results = await client.search_notes(keywords=["Python", "API"])
            print(f"✓ 搜索到 {len(results)} 条笔记")
            
            # 4. 创建笔记
            result = await client.create_note(
                content="# 测试笔记\n\n这是通过 API 创建的笔记",
                note_type="note"
            )
            print("✓ 笔记创建成功")
            
            # 5. 获取卡片盒
            boxes = await client.get_zettelboxes()
            print(f"✓ 获取到 {len(boxes)} 个卡片盒")
            
        except DinoxAPIError as e:
            print(f"✗ API 错误: [{e.code}] {e.message}")
    
    # 方式2: 使用配置对象
    config = DinoxConfig(
        api_token="YOUR_TOKEN",
        base_url="https://dinoai.chatgo.pro",
        timeout=30
    )
    
    client = DinoxClient(config=config)
    try:
        await client.connect()
        notes = await client.get_notes_list()
        print(f"配置方式: 获取 {len(notes)} 天笔记")
    finally:
        await client.close()

asyncio.run(full_example())
```

---

## 📚 API 参考

### DinoxClient 类

主客户端类，提供所有 API 交互方法。

#### 初始化

```python
# 方式1: 使用 Token
client = DinoxClient(api_token="YOUR_TOKEN")

# 方式2: 使用配置对象
config = DinoxConfig(
    api_token="YOUR_TOKEN",
    base_url="https://dinoai.chatgo.pro",  # 可选
    timeout=30  # 可选，单位：秒
)
client = DinoxClient(config=config)
```

#### 连接管理

```python
# 使用上下文管理器（推荐）
async with DinoxClient(api_token="TOKEN") as client:
    # 自动管理连接
    pass

# 手动管理连接
client = DinoxClient(api_token="TOKEN")
await client.connect()
try:
    # 使用客户端
    pass
finally:
    await client.close()
```

---

### 笔记查询接口

#### 1. 获取笔记列表

```python
async def get_notes_list(
    last_sync_time: str = "1900-01-01 00:00:00",
    template: str = None
) -> List[Dict[str, Any]]
```

**参数**：
- `last_sync_time`: 上次同步时间，格式 `YYYY-MM-DD HH:mm:ss`
- `template`: Mustache 模板字符串（可选，使用默认模板）

**返回**：按日期分组的笔记列表

**示例**：

```python
# 获取所有笔记
all_notes = await client.get_notes_list()

# 增量同步
recent_notes = await client.get_notes_list(
    last_sync_time="2025-10-18 00:00:00"
)

# 使用自定义模板
custom_template = """---
title: {{title}}
---
{{content}}
"""
notes = await client.get_notes_list(template=custom_template)

# 处理结果
for day_note in notes:
    print(f"日期: {day_note['date']}")
    for note in day_note['notes']:
        print(f"  ID: {note['noteId']}")
        print(f"  标题: {note['title']}")
        print(f"  创建时间: {note['createTime']}")
        print(f"  是否删除: {note['isDel']}")
```

#### 2. 根据 ID 查询笔记

```python
async def get_note_by_id(note_id: str) -> Dict[str, Any]
```

**参数**：
- `note_id`: 笔记 ID (UUID格式)

**返回**：笔记详情字典

**示例**：

```python
note = await client.get_note_by_id("0199eb0d-fccc-7dc8-82da-7d32be3e668b")
print(note['title'])
print(note['content'])
```

#### 3. 搜索笔记

```python
async def search_notes(keywords: List[str]) -> List[Dict[str, Any]]
```

**参数**：
- `keywords`: 关键词列表

**返回**：匹配的笔记列表

**示例**：

```python
results = await client.search_notes(keywords=["Python", "异步", "API"])
print(f"找到 {len(results)} 条笔记")
for note in results:
    print(f"- {note['title']}")
```

---

### 笔记创建/更新接口

#### 1. 创建文字笔记

```python
async def create_text_note(content: str) -> Dict[str, Any]
```

**参数**：
- `content`: 笔记内容

**返回**：创建结果

**示例**：

```python
result = await client.create_text_note("这是一条测试笔记")
print(result)
```

#### 2. 创建笔记（支持卡片盒）

```python
async def create_note(
    content: str,
    note_type: str = "note",
    zettelbox_ids: List[str] = None
) -> Dict[str, Any]
```

**参数**：
- `content`: 笔记内容（Markdown 格式）
- `note_type`: 笔记类型（"note" 或 "crawl"）
- `zettelbox_ids`: 卡片盒 ID 列表

**返回**：创建结果

**示例**：

```python
# 不指定卡片盒
result = await client.create_note(
    content="# 标题\n\n内容..."
)

# 指定卡片盒
result = await client.create_note(
    content="# 工作笔记\n\n今天完成了...",
    note_type="note",
    zettelbox_ids=["box-id-1", "box-id-2"]
)
```

#### 3. 更新笔记

```python
async def update_note(note_id: str, content_md: str) -> Dict[str, Any]
```

**参数**：
- `note_id`: 笔记 ID
- `content_md`: 更新后的内容（Markdown 格式）

**返回**：更新结果

**示例**：

```python
result = await client.update_note(
    note_id="0199eb0d-fccc-7dc8-82da-7d32be3e668b",
    content_md="# 更新后的标题\n\n更新后的内容"
)
```

---

### 卡片盒接口

#### 获取卡片盒列表

```python
async def get_zettelboxes() -> List[Dict[str, Any]]
```

**返回**：卡片盒列表

**示例**：

```python
boxes = await client.get_zettelboxes()
for box in boxes:
    print(f"- {box.get('name', 'Unnamed')}")
```

---

### 工具方法

#### 格式化同步时间

```python
@staticmethod
def format_sync_time(dt: datetime = None) -> str
```

**参数**：
- `dt`: datetime 对象（可选，默认当前时间）

**返回**：格式化的时间字符串 "YYYY-MM-DD HH:mm:ss"

**示例**：

```python
from datetime import datetime

# 当前时间
current_time = DinoxClient.format_sync_time()
print(current_time)  # "2025-10-19 15:30:45"

# 指定时间
dt = datetime(2025, 10, 18, 12, 0, 0)
formatted = DinoxClient.format_sync_time(dt)
print(formatted)  # "2025-10-18 12:00:00"
```

---

## 🔧 配置选项

### DinoxConfig

```python
@dataclass
class DinoxConfig:
    api_token: str              # 必需，API Token
    base_url: str = "https://dinoai.chatgo.pro"  # API 基础 URL
    timeout: int = 30           # 请求超时时间（秒）
```

**示例**：

```python
# 基本配置
config = DinoxConfig(api_token="YOUR_TOKEN")

# 自定义配置
config = DinoxConfig(
    api_token="YOUR_TOKEN",
    base_url="https://custom.api.com",
    timeout=60
)

client = DinoxClient(config=config)
```

---

## ⚠️ 错误处理

### DinoxAPIError

所有 API 错误都会抛出 `DinoxAPIError` 异常。

**属性**：
- `code`: 错误码
- `message`: 错误消息
- `status_code`: HTTP 状态码（可选）

**示例**：

```python
from dinox_client import DinoxAPIError

try:
    notes = await client.get_notes_list()
except DinoxAPIError as e:
    print(f"错误码: {e.code}")
    print(f"错误信息: {e.message}")
    print(f"HTTP状态: {e.status_code}")
    
    # 根据错误码处理
    if e.code == "401":
        print("Token 无效，请重新登录")
    elif e.code == "NETWORK_ERROR":
        print("网络连接失败")
```

### 常见错误码

| 错误码 | 说明 | 处理建议 |
|--------|------|----------|
| 000000 | 成功 | - |
| 400001 | Token 无效或已过期 | 检查并更新 Token |
| 400002 | 参数错误 | 检查请求参数 |
| 500000 | 服务器内部错误 | 稍后重试 |
| NETWORK_ERROR | 网络错误 | 检查网络连接 |
| INVALID_JSON | JSON 解析错误 | 检查响应格式 |

---

## 🎯 最佳实践

### 1. 使用上下文管理器

```python
# ✅ 推荐：自动管理连接
async with DinoxClient(api_token="TOKEN") as client:
    notes = await client.get_notes_list()

# ❌ 不推荐：手动管理容易忘记关闭
client = DinoxClient(api_token="TOKEN")
await client.connect()
notes = await client.get_notes_list()
# 忘记调用 await client.close()
```

### 2. 增量同步

```python
import json
from datetime import datetime

# 保存上次同步时间
def save_sync_time(time_str: str):
    with open("last_sync.json", "w") as f:
        json.dump({"last_sync_time": time_str}, f)

def load_sync_time() -> str:
    try:
        with open("last_sync.json", "r") as f:
            data = json.load(f)
            return data.get("last_sync_time", "1900-01-01 00:00:00")
    except FileNotFoundError:
        return "1900-01-01 00:00:00"

# 使用
async def sync_notes():
    async with DinoxClient(api_token="TOKEN") as client:
        last_sync = load_sync_time()
        notes = await client.get_notes_list(last_sync_time=last_sync)
        
        # 处理笔记...
        
        # 保存新的同步时间
        current_time = DinoxClient.format_sync_time()
        save_sync_time(current_time)
```

### 3. 错误重试

```python
import asyncio

async def fetch_with_retry(client, max_retries=3):
    for attempt in range(max_retries):
        try:
            return await client.get_notes_list()
        except DinoxAPIError as e:
            if e.code == "NETWORK_ERROR" and attempt < max_retries - 1:
                wait_time = 2 ** attempt  # 指数退避
                print(f"重试 {attempt + 1}/{max_retries}，等待 {wait_time}秒...")
                await asyncio.sleep(wait_time)
            else:
                raise
```

### 4. 并发请求

```python
async def fetch_multiple_notes(client, note_ids: List[str]):
    # 并发获取多个笔记
    tasks = [client.get_note_by_id(nid) for nid in note_ids]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # 处理结果
    notes = []
    for result in results:
        if isinstance(result, Exception):
            print(f"获取失败: {result}")
        else:
            notes.append(result)
    
    return notes
```

### 5. 环境变量管理 Token

```python
import os
from dinox_client import DinoxClient

# ✅ 安全：使用环境变量
token = os.environ.get("DINOX_API_TOKEN")
if not token:
    raise ValueError("请设置 DINOX_API_TOKEN 环境变量")

async with DinoxClient(api_token=token) as client:
    # 使用客户端
    pass

# ❌ 不安全：硬编码 Token
# client = DinoxClient(api_token="eyJhbGc...")  # 不要这样做！
```

---

## 🧪 测试

### 运行测试

```bash
# 运行所有测试
pytest test_dinox_client.py -v

# 运行特定测试
pytest test_dinox_client.py::test_get_notes_list -v

# 查看详细输出
pytest test_dinox_client.py -v -s

# 生成覆盖率报告
pytest test_dinox_client.py --cov=dinox_client --cov-report=html
```

### 设置测试 Token

```bash
# Linux/Mac
export DINOX_API_TOKEN="your_token_here"

# Windows PowerShell
$env:DINOX_API_TOKEN="your_token_here"

# Windows CMD
set DINOX_API_TOKEN=your_token_here
```

### 测试结果

运行测试套件后的典型输出：

```
======================== test session starts ========================
collected 21 items

test_dinox_client.py::test_config_creation PASSED           [  4%]
test_dinox_client.py::test_get_notes_list PASSED           [ 38%]
test_dinox_client.py::test_create_note PASSED               [ 61%]
test_dinox_client.py::test_full_workflow PASSED             [ 90%]
...

==================== 20 passed, 1 failed in 4.48s ====================
```

---

## 📊 性能建议

### 1. 连接复用

```python
# ✅ 复用连接
async with DinoxClient(api_token="TOKEN") as client:
    for i in range(10):
        notes = await client.get_notes_list()
        # 处理笔记...

# ❌ 每次创建新连接（慢）
for i in range(10):
    async with DinoxClient(api_token="TOKEN") as client:
        notes = await client.get_notes_list()
```

### 2. 批量操作

```python
# ✅ 并发获取（快）
async def get_all_notes_details(client, note_ids):
    tasks = [client.get_note_by_id(nid) for nid in note_ids]
    return await asyncio.gather(*tasks)

# ❌ 串行获取（慢）
async def get_all_notes_details_slow(client, note_ids):
    notes = []
    for nid in note_ids:
        note = await client.get_note_by_id(nid)
        notes.append(note)
    return notes
```

### 3. 超时设置

```python
# 针对慢速网络调整超时
config = DinoxConfig(
    api_token="TOKEN",
    timeout=60  # 增加到60秒
)
```

---

## 🔍 调试

### 启用日志

```python
import logging

# 启用详细日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# 使用客户端
async with DinoxClient(api_token="TOKEN") as client:
    notes = await client.get_notes_list()
```

### 查看请求详情

```python
# 在 dinox_client.py 的 _request 方法中添加日志
async def _request(self, method, endpoint, **kwargs):
    url = f"{self.config.base_url}{endpoint}"
    print(f"🔗 请求: {method} {url}")
    print(f"📤 请求体: {kwargs.get('data')}")
    
    # ... 发送请求 ...
    
    print(f"📥 响应: {response.status}")
    print(f"📄 响应体: {response_text[:200]}...")
```

---

## 📖 完整示例应用

### Obsidian 同步脚本

```python
"""
Obsidian Dinox 同步脚本
定期从 Dinox 同步笔记到本地 Obsidian 仓库
"""
import asyncio
import os
import json
from pathlib import Path
from datetime import datetime
from dinox_client import DinoxClient, DinoxAPIError

# 配置
OBSIDIAN_VAULT = Path("~/Documents/Obsidian/MyVault").expanduser()
DINOX_FOLDER = OBSIDIAN_VAULT / "Dinox Notes"
SYNC_STATE_FILE = DINOX_FOLDER / ".sync_state.json"

def load_sync_state():
    """加载同步状态"""
    if SYNC_STATE_FILE.exists():
        with open(SYNC_STATE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"last_sync_time": "1900-01-01 00:00:00"}

def save_sync_state(state):
    """保存同步状态"""
    DINOX_FOLDER.mkdir(parents=True, exist_ok=True)
    with open(SYNC_STATE_FILE, 'w', encoding='utf-8') as f:
        json.dump(state, f, indent=2)

def save_note_to_file(note, date_folder):
    """保存笔记到文件"""
    # 使用 noteId 作为文件名
    note_id = note['noteId'].replace('-', '_')
    file_path = date_folder / f"{note_id}.md"
    
    # 如果笔记被删除，删除本地文件
    if note.get('isDel'):
        if file_path.exists():
            file_path.unlink()
            print(f"  🗑 删除: {file_path.name}")
        return
    
    # 保存笔记内容
    content = note.get('content', '')
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"  ✓ 保存: {file_path.name}")

async def sync_notes():
    """同步笔记"""
    token = os.environ.get("DINOX_API_TOKEN")
    if not token:
        print("❌ 错误: 请设置 DINOX_API_TOKEN 环境变量")
        return
    
    print(f"\n{'='*60}")
    print("Dinox → Obsidian 同步")
    print(f"{'='*60}\n")
    
    # 加载同步状态
    state = load_sync_state()
    last_sync = state['last_sync_time']
    print(f"上次同步: {last_sync}")
    
    async with DinoxClient(api_token=token) as client:
        try:
            # 获取笔记
            print(f"正在获取笔记...")
            notes = await client.get_notes_list(last_sync_time=last_sync)
            
            if not notes:
                print("✓ 没有新笔记")
                return
            
            # 处理每一天的笔记
            total_processed = 0
            for day_note in notes:
                date = day_note['date']
                date_folder = DINOX_FOLDER / date
                date_folder.mkdir(parents=True, exist_ok=True)
                
                print(f"\n📅 {date} ({len(day_note['notes'])} 条笔记)")
                
                for note in day_note['notes']:
                    save_note_to_file(note, date_folder)
                    total_processed += 1
            
            # 更新同步状态
            current_time = DinoxClient.format_sync_time()
            state['last_sync_time'] = current_time
            save_sync_state(state)
            
            print(f"\n{'='*60}")
            print(f"✓ 同步完成!")
            print(f"  处理笔记: {total_processed} 条")
            print(f"  新同步时间: {current_time}")
            print(f"{'='*60}\n")
            
        except DinoxAPIError as e:
            print(f"\n❌ 同步失败: [{e.code}] {e.message}")

if __name__ == "__main__":
    asyncio.run(sync_notes())
```

---

## 📞 技术支持

- **Email**: zmyjust@gmail.com
- **GitHub**: https://github.com/ryzencool/dinox-sync
- **官网**: https://dinox.info

---

## 📄 许可证

MIT License

---

## 🔄 更新日志

### v1.0.0 (2025-10-19)

- ✅ 完整的 API 接口实现
- ✅ 异步支持
- ✅ 完善的错误处理
- ✅ 类型提示
- ✅ 全面的测试覆盖
- ✅ 详细的文档

---

## 📚 相关文档

- [获取笔记列表API](./获取笔记列表（同步接口）.md)
- [根据 ID 查询笔记](./根据%20id%20查询笔记.md)
- [创建笔记API](./创建笔记.md)
- [Dinox 官方文档](https://dinox.info)

---

**享受使用 Dinox Python Client！** 🎉

