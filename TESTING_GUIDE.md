# 📦 DinoX API 测试指南

## 快速测试 PyPI 包

### 1. 安装包
```bash
pip install dinox-api
```

### 2. 配置 Token（可选）

#### 方法一：创建 .env 文件
```bash
echo "DINOX_API_TOKEN=your_actual_token_here" > .env
```

#### 方法二：设置环境变量
```bash
# Linux/Mac
export DINOX_API_TOKEN="your_actual_token_here"

# Windows PowerShell
$env:DINOX_API_TOKEN="your_actual_token_here"
```

### 3. 运行测试

#### 完整功能测试
```bash
python test_pypi_complete.py
```

此测试会：
- ✅ 自动从 .env 或环境变量读取 Token
- ✅ 测试所有主要功能
- ✅ 如果有真实 Token，会尝试实际连接
- ✅ 显示详细的测试结果

#### 简单导入测试
```bash
python test_pypi_install.py
```

#### 使用演示
```bash
python demo_pypi_usage.py
```

## 测试结果说明

### ✅ 已验证功能
- **模块导入**: `from dinox_client import DinoxClient, DinoxConfig`
- **客户端创建**: 支持多种创建方式
- **配置管理**: 灵活的服务器和超时配置
- **上下文管理器**: 支持 `async with` 语法
- **错误处理**: 正确的参数验证
- **API 方法**: 所有核心 API 方法可用
- **实际连接**: 使用真实 Token 可成功获取笔记

### 📌 注意事项
1. **包名 vs 模块名**
   - 安装: `pip install dinox-api`
   - 导入: `from dinox_client import DinoxClient`

2. **Token 加载优先级**
   - 环境变量 `DINOX_API_TOKEN`
   - .env 文件中的 `DINOX_API_TOKEN`
   - 代码中直接传入

3. **服务器选择**
   - 笔记服务器: `https://api.chatgo.pro` (读取操作)
   - AI 服务器: `https://aisdk.chatgo.pro` (创建/搜索)

## 代码示例

### 基础使用
```python
import asyncio
from dinox_client import DinoxClient

async def main():
    # 从环境变量或 .env 自动加载 token
    import os
    token = os.environ.get('DINOX_API_TOKEN') or 'your_token'
    
    async with DinoxClient(api_token=token) as client:
        # 获取笔记列表
        notes = await client.get_notes_list()
        print(f'获取到 {len(notes)} 天的笔记')

asyncio.run(main())
```

### 使用不同服务器
```python
from dinox_client import DinoxClient, DinoxConfig

# 笔记服务器（读取）
note_config = DinoxConfig(
    api_token="your_token",
    base_url="https://api.chatgo.pro"
)

# AI 服务器（创建/搜索）
ai_config = DinoxConfig(
    api_token="your_token",
    base_url="https://aisdk.chatgo.pro"
)

async with DinoxClient(config=note_config) as client:
    notes = await client.get_notes_list()

async with DinoxClient(config=ai_config) as client:
    await client.create_note("新笔记内容")
```

## 故障排除

### 问题：导入失败
```
ImportError: No module named 'dinox_client'
```
**解决**: 确保已安装 `pip install dinox-api`

### 问题：Token 未找到
```
[i] 未找到真实 Token，使用测试 Token
```
**解决**: 创建 .env 文件或设置环境变量

### 问题：连接失败
```
[w] API 调用失败: Network error
```
**解决**: 检查网络连接和 Token 有效性

## 测试文件说明

| 文件 | 用途 |
|------|------|
| `test_pypi_complete.py` | 完整功能测试，自动加载 Token |
| `test_pypi_install.py` | 简单导入测试 |
| `demo_pypi_usage.py` | 实际使用演示 |
| `.env.example` | Token 配置模板 |

## 更多信息

- GitHub: https://github.com/JimEverest/DinoSync
- PyPI: https://pypi.org/project/dinox-api/
- 文档: [README.md](README.md)
