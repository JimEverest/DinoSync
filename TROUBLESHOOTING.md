# 故障排查

**快速诊断:** 运行 `python health_check.py`

---

## 📍 当前 API 状态 (实时更新)

**最后验证:** 2025-10-22

### 服务器状态

| 服务器 | URL | 状态 | 响应时间 |
|--------|-----|------|---------|
| 笔记服务器 | `https://dinoai.chatgo.pro` | ✅ 正常 | ~500ms |
| AI 服务器 | `https://aisdk.chatgo.pro` | ✅ 正常 | ~800ms |

### 端点状态矩阵

| 方法 | 端点 | 服务器 | 状态 | 说明 |
|-----|------|--------|------|------|
| `get_notes_list()` | `/openapi/v5/notes` | Note | ✅ | 完全正常 |
| `get_note_by_id()` | `/api/openapi/note/{id}` | Note | ⚠️ | 返回404，可能未部署 |
| `search_notes()` | `/api/openapi/searchNotes` | AI | ✅ | 完全正常 |
| `create_note()` | `/api/openapi/createNote` | AI | ✅ | 完全正常 |
| `create_text_note()` | `/openapi/text/input` | AI | ⚠️ | 返回404 |
| `get_zettelboxes()` | `/api/openapi/zettelboxes` | AI | ✅ | 完全正常 |
| `update_note()` | `/openapi/updateNote` | Note | ⚠️ | 可能未部署 |

**图例:** ✅ 正常 | ⚠️ 部分可用/已知问题 | ❌ 不可用

---

## 已知问题

### 问题 #1: get_note_by_id() 返回 404
- **发现:** 2025-10-22
- **错误:** `{"status":404,"error":"Not Found"}`
- **影响:** 中等（不影响核心功能）
- **替代方案:** 使用 `get_notes_list()` 获取所有笔记
- **状态:** 等待上游修复

### 问题 #2: create_text_note() 返回 404
- **发现:** 2025-10-22
- **错误:** `404 Not Found`
- **影响:** 低
- **替代方案:** 使用 `create_note()` 替代
- **状态:** 建议使用 create_note()

---

## 常见问题

### 1. 导入失败

**问题:**
```python
ImportError: No module named 'dinox_client'
```

**解决:**
```bash
pip install dinox-api
# 注意：包名是 dinox-api，模块名是 dinox_client
```

---

### 2. Token 认证失败

**问题:**
```
[401] auth failed
[000008] auth failed
```

**解决:**
```bash
# 检查Token是否正确
echo $DINOX_API_TOKEN  # Linux/Mac
echo $env:DINOX_API_TOKEN  # Windows

# Token格式应该是 JWT: xxxxx.yyyyy.zzzzz
```

---

### 3. 404 错误

**问题:**
```
[404] Not Found
```

**可能原因:**
- 端点路径错误
- 服务器未部署该端点
- 使用了错误的服务器

**解决:**
```python
# 使用自动路由 (v0.2.0+)
async with DinoxClient(api_token="TOKEN") as client:
    # 自动选择正确服务器
    await client.get_notes_list()  # → Note Server
    await client.search_notes(["关键词"])  # → AI Server
```

**已知404端点:**
- `create_text_note()` - 使用 `create_note()` 替代
- `get_note_by_id()` - 部分服务器未部署

---

### 4. 网络错误

**问题:**
```
[NETWORK_ERROR] Network error
```

**诊断:**
```bash
# 测试服务器连接
curl -I https://dinoai.chatgo.pro
curl -I https://aisdk.chatgo.pro

# 测试DNS
ping dinoai.chatgo.pro
```

**解决:**
- 检查网络连接
- 检查防火墙设置
- 增加超时时间:
  ```python
  config = DinoxConfig(api_token="TOKEN", timeout=60)
  ```

---

### 5. 超时错误

**问题:**
```
asyncio.TimeoutError
```

**解决:**
```python
# 增加超时时间
config = DinoxConfig(
    api_token="TOKEN",
    timeout=60  # 增加到60秒
)
```

---

### 6. UTF-8 编码错误 (Windows)

**问题:**
```
UnicodeEncodeError: 'gbk' codec can't encode...
```

**解决:**
- v0.2.0+ 已自动修复
- 如仍有问题:
  ```python
  import sys
  import io
  sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
  ```

---

## 诊断流程

### 快速诊断决策树

```
API调用失败
├─ 网络错误 (NETWORK_ERROR)
│  ├─ ping dinoai.chatgo.pro / aisdk.chatgo.pro
│  └─ 检查防火墙/代理设置
│
├─ 认证错误 (401/403/000008)
│  ├─ 验证Token格式 (JWT三段式)
│  ├─ 检查Token是否过期
│  └─ 测试: python -c "import os; print(len(os.getenv('DINOX_API_TOKEN')))"
│
├─ 404 错误
│  ├─ 查看上面"端点状态矩阵"
│  ├─ 检查是否在"已知问题"列表
│  └─ 如是新问题 → 运行 health_check.py 记录
│
├─ 500 服务器错误
│  ├─ 检查请求参数是否正确
│  ├─ 保存完整错误响应
│  └─ 稍后重试（可能是临时问题）
│
└─ 超时 (TimeoutError)
   ├─ 增加timeout: DinoxConfig(timeout=60)
   └─ 检查网络延迟
```

### Step 1: 运行健康检查

```bash
python health_check.py
```

输出解读：
- `✅ HEALTHY` - 所有核心功能正常
- `⚠️ DEGRADED` - 部分功能异常，但可用
- `❌ UNHEALTHY` - 核心功能不可用

### Step 2: 查看错误详情

```python
try:
    await client.get_notes_list()
except DinoxAPIError as e:
    print(f"错误码: {e.code}")
    print(f"错误信息: {e.message}")
    print(f"HTTP状态: {e.status_code}")
```

### Step 3: 查找已知问题

检查本文档"已知问题"部分，如果找到匹配的问题，按说明使用替代方案。

### Step 4: 上报新问题（如果是未知问题）

1. 保存 `health_check.py` 输出
2. 记录完整错误信息
3. 更新本文档"已知问题"部分
4. 提交GitHub Issue（如需要）

---

## 错误码速查

| 错误码 | 说明 | 解决方法 |
|--------|------|---------|
| `000000` | 成功 | - |
| `401` | 未授权 | 检查Token |
| `403` | 禁止访问 | 检查权限 |
| `404` | 未找到 | 检查端点和服务器 |
| `500` | 服务器错误 | 稍后重试 |
| `000008` | 认证失败 | 验证Token |
| `NETWORK_ERROR` | 网络错误 | 检查连接 |

---

## 测试连接

### 最小测试脚本

```python
import asyncio
from dinox_client import DinoxClient

async def test():
    async with DinoxClient(api_token="YOUR_TOKEN") as client:
        notes = await client.get_notes_list()
        print(f"成功! 获取 {len(notes)} 天笔记")

asyncio.run(test())
```

---

## 获取帮助

1. **运行健康检查:** `python health_check.py`
2. **查看示例:** `python example.py`
3. **运行测试:** `pytest test_dinox_client.py -v`
4. **提交Issue:** https://github.com/JimEverest/DinoSync/issues

提交Issue时请附上：
- `health_check.py` 的输出
- Python版本和系统信息
- 完整错误信息
