# Dinox API 完整参考

**版本:** v0.2.0  
**更新:** 2025-10-22

---

## 核心类

### DinoxClient

```python
DinoxClient(api_token: str = None, config: DinoxConfig = None)
```

**参数:**
- `api_token`: API Token (JWT格式)
- `config`: 配置对象（可选，用于设置timeout）

**用法:**
```python
# 简单方式（推荐）
async with DinoxClient(api_token="YOUR_TOKEN") as client:
    notes = await client.get_notes_list()

# 高级配置
config = DinoxConfig(api_token="YOUR_TOKEN", timeout=60)
async with DinoxClient(config=config) as client:
    notes = await client.get_notes_list()
```

### DinoxConfig

```python
@dataclass
class DinoxConfig:
    api_token: str      # API Token（必需）
    timeout: int = 30   # 超时时间（秒）
```

**注意:** v0.2.0+ 自动服务器路由，无需配置 base_url

---

## API 方法

### 笔记查询

#### `get_notes_list()`
获取笔记列表，支持增量同步。

```python
await client.get_notes_list(
    last_sync_time="1900-01-01 00:00:00",  # 可选
    template=None  # 可选，Mustache模板
)
```

**返回:** `List[Dict]` - 按日期分组的笔记列表

#### `get_note_by_id()`  
根据 ID 获取笔记详情。

```python
await client.get_note_by_id(note_id="uuid-here")
```

**返回:** `Dict` - 笔记详情

#### `search_notes()`
搜索笔记内容。

```python
await client.search_notes(keywords=["关键词1", "关键词2"])
```

**返回:** `Dict` - 包含 'content' 字段的搜索结果

---

### 笔记管理

#### `create_note()`
创建新笔记。

```python
await client.create_note(
    content="# 标题\n\n内容",
    note_type="note",  # 可选: "note" 或 "crawl"
    zettelbox_ids=[]   # 可选: 卡片盒ID列表
)
```

**返回:** `Dict` - 创建结果

#### `create_text_note()`
创建纯文本笔记。

```python
await client.create_text_note(content="文本内容")
```

**返回:** `Dict` - 创建结果  
**注意:** 此方法在某些服务器可能返回404

#### `update_note()`
更新现有笔记。

```python
await client.update_note(
    note_id="uuid-here",
    content_md="# 新内容"
)
```

**返回:** `Dict` - 更新结果

---

### 卡片盒

#### `get_zettelboxes()`
获取所有卡片盒。

```python
await client.get_zettelboxes()
```

**返回:** `List[Dict]` - 卡片盒列表

---

### 工具方法

#### `format_sync_time()`
格式化时间为同步格式。

```python
from datetime import datetime
DinoxClient.format_sync_time(datetime.now())
```

**返回:** `str` - "YYYY-MM-DD HH:mm:ss"

---

## 错误处理

所有API错误抛出 `DinoxAPIError`:

```python
from dinox_client import DinoxAPIError

try:
    await client.get_notes_list()
except DinoxAPIError as e:
    print(f"错误码: {e.code}")
    print(f"错误信息: {e.message}")
    print(f"HTTP状态: {e.status_code}")
```

### 常见错误码

| 错误码 | 说明 | 处理方法 |
|--------|------|---------|
| `000000` | 成功 | - |
| `401` / `000008` | 认证失败 | 检查Token |
| `404` | 端点不存在 | 检查API状态 |
| `500` | 服务器错误 | 稍后重试 |
| `NETWORK_ERROR` | 网络错误 | 检查连接 |

---

## 服务器映射

v0.2.0+ 支持自动服务器路由：

| 方法 | 自动路由到 |
|-----|-----------|
| `get_notes_list`, `get_note_by_id`, `update_note` | 笔记服务器 (dinoai.chatgo.pro) |
| `search_notes`, `create_note`, `get_zettelboxes` | AI服务器 (aisdk.chatgo.pro) |

**说明:** v0.2.0+ 总是自动路由，无需手动配置服务器

---

## 响应格式

### 笔记列表
```json
[
  {
    "date": "2025-10-22",
    "notes": [
      {
        "noteId": "uuid",
        "title": "标题",
        "content": "内容",
        "createTime": "2025-10-22T10:00:00",
        "isDel": false
      }
    ]
  }
]
```

### 搜索结果
```json
{
  "content": "搜索结果内容..."
}
```

---

**详细示例:** 参见 `example.py`  
**测试:** `pytest test_dinox_client.py -v`
