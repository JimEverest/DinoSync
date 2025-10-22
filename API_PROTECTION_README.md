# Dinox API 保护性文档与测试体系使用指南

> **目标：** 让开发者和 Coding AI 在面对上游 API 变更时，有预案、有目标、更从容

**创建日期：** 2025-10-22  
**适用版本：** dinox-api v0.2.0+

---

## 🎯 核心理念

作为下游 API 客户端，我们通过**非代码手段**应对上游不稳定性：

1. **清晰文档** - 记录当前状态、已知问题、历史变更
2. **系统测试** - 自动化监控、快速发现问题
3. **明确流程** - 标准化排查、决策清单

> ⚠️ **注意：** 这套体系**不涉及**重试、退避、降级、缓存等弹性代码机制

---

## 📚 文档体系

### 1. 核心文档

| 文档 | 用途 | 更新频率 | 负责人 |
|-----|------|---------|--------|
| **API_STABILITY_GUIDE.md** | 完整的稳定性保障指南 | 发现问题时 | 开发者 |
| **API_PROTECTION_README.md** | 使用指南（本文档） | 架构变更时 | 开发者 |
| **CHANGELOG.md** | 版本变更记录 | 每次发布 | 自动/开发者 |
| **README.md** | API 参考和状态表格 | 功能变更时 | 开发者 |

### 2. 快照文件

```
snapshots/
├── baseline.json              # 基准快照（最后一个稳定状态）
├── current_snapshot.json      # 当前快照（每次健康检查更新）
└── snapshot_YYYYMMDD.json     # 历史快照（定期归档）
```

### 3. 报告文件

```
health_report_YYYYMMDD_HHMMSS.json  # 详细健康检查报告
```

---

## 🛠️ 工具集

### 1. 健康检查工具 (`health_check.py`)

**用途：** 快速验证所有 API 端点状态

**运行时机：**
- ✅ 每次发布前
- ✅ 发现问题时
- ✅ 定期监控（建议每天）
- ✅ 上游通知变更后

**使用方法：**
```bash
# 基本运行
python health_check.py

# 使用特定 Token
export DINOX_API_TOKEN="your_token"  # Linux/Mac
$env:DINOX_API_TOKEN="your_token"    # Windows PowerShell
python health_check.py

# 在 CI/CD 中运行
python health_check.py || echo "Health check failed"
```

**输出解读：**
- `✅ HEALTHY` - 所有核心功能正常
- `⚠️ DEGRADED` - 部分核心功能异常，但可用
- `❌ UNHEALTHY` - 严重问题，核心功能不可用

**生成的文件：**
- `health_report_YYYYMMDD_HHMMSS.json` - 详细报告
- `snapshots/current_snapshot.json` - 当前快照

### 2. 完整测试套件 (`test_dinox_client.py`)

**用途：** 完整的功能和集成测试

**运行方法：**
```bash
# 运行所有测试
pytest test_dinox_client.py -v

# 运行特定测试
pytest test_dinox_client.py::test_get_notes_list -v

# 生成 HTML 报告
pytest test_dinox_client.py --html=report.html --self-contained-html

# 查看覆盖率
pytest test_dinox_client.py --cov=dinox_client --cov-report=html
```

### 3. 示例脚本 (`example.py`)

**用途：** 演示所有功能的实际使用

**运行方法：**
```bash
python example.py
```

---

## 📋 标准工作流程

### 日常开发流程

```
开发新功能
    ↓
运行单元测试 (pytest)
    ↓
运行健康检查 (health_check.py)
    ↓
提交代码
    ↓
CI/CD 自动测试
```

### 发现问题流程

```
发现 API 异常
    ↓
1. 运行健康检查 → 获取当前状态
    ↓
2. 查阅 API_STABILITY_GUIDE.md 第 2 节 → 确认是否已知问题
    ↓
3. 如果是新问题 → 按第 7 节检查清单操作
    ↓
4. 更新文档（第 1、2 节）
    ↓
5. 决定是否需要代码修改
    ↓
6. 更新测试用例
    ↓
7. 发布新版本（如需要）
```

### 定期维护流程

```
每周一次：
  □ 运行完整健康检查
  □ 检查是否有新的已知问题
  □ 归档快照文件

每月一次：
  □ 运行完整测试套件
  □ 审查所有已知问题
  □ 更新性能基准数据
  □ 审查文档完整性
```

---

## 🚨 应急响应指南

### Scenario 1: 核心端点返回 404

**症状：** `get_notes_list()` 返回 404

**立即操作：**
```bash
# 1. 确认问题
python health_check.py

# 2. 检查服务器可达性
curl -I https://dinoai.chatgo.pro

# 3. 查看历史快照
ls -lt snapshots/
```

**参考文档：** API_STABILITY_GUIDE.md 第 6.1 节

**决策：**
- 如果是临时问题 → 等待恢复，通知用户
- 如果是路径变更 → 更新代码，发布紧急版本
- 如果是长期不可用 → 标记为已知问题，提供替代方案

---

### Scenario 2: 新端点出现

**症状：** 官方文档提到新的 API 端点

**立即操作：**
```bash
# 1. 记录新端点信息
# 编辑 API_STABILITY_GUIDE.md 第 1.2 节

# 2. 添加到健康检查
# 编辑 health_check.py，添加新测试

# 3. 运行验证
python health_check.py
```

**后续：**
- 在 `dinox_client.py` 中添加新方法
- 添加单元测试
- 更新 README.md API 参考
- 发布次版本（0.x.0）

---

### Scenario 3: 认证失败

**症状：** 返回 `401` 或 `000008` 错误

**立即操作：**
```bash
# 1. 验证 Token
echo $DINOX_API_TOKEN

# 2. 测试 Token 有效性
python -c "
import asyncio
from dinox_client import DinoxClient
async def test():
    async with DinoxClient(api_token='YOUR_TOKEN') as c:
        await c.get_notes_list()
asyncio.run(test())
"

# 3. 检查 Token 格式
# JWT Token 应该是三段式: xxxxx.yyyyy.zzzzz
```

**参考文档：** API_STABILITY_GUIDE.md 第 2.2 节

---

### Scenario 4: 响应结构变化

**症状：** 测试失败，提示字段缺失

**立即操作：**
```bash
# 1. 对比快照
# 查看 snapshots/baseline.json vs current_snapshot.json

# 2. 记录变化
# 更新 API_STABILITY_GUIDE.md 第 2 节

# 3. 评估影响
pytest test_dinox_client.py -v
```

**决策矩阵：**

| 变化类型 | 影响 | 操作 |
|---------|------|------|
| 新增字段 | 低 | 更新文档，可选更新代码 |
| 删除字段 | 高 | 立即更新代码，发布主版本 |
| 字段重命名 | 高 | 更新代码，发布主版本 |
| 类型变更 | 高 | 更新代码，发布主版本 |

---

## 💡 给 AI 的使用指南

### 当你需要诊断 API 问题时：

**Step 1: 收集信息**
```
1. 阅读 API_STABILITY_GUIDE.md 第 1 节（当前状态）
2. 检查第 2 节（已知问题）
3. 运行 health_check.py
```

**Step 2: 分析问题**
```
根据 API_STABILITY_GUIDE.md 第 6.1 节的决策树：
- 网络错误 → 检查连接
- 认证错误 → 验证 Token
- 404 错误 → 对照端点状态矩阵
- 500 错误 → 检查请求参数
- 超时 → 检查网络延迟
```

**Step 3: 响应模板**

使用 API_STABILITY_GUIDE.md 第 8.2 节的标准模板报告问题。

**Step 4: 更新文档**

按照第 7 节检查清单执行操作。

### AI 决策规则

```python
if is_known_issue(error):
    refer_to_section_2()  # 已知问题列表
    suggest_workaround()
else:
    create_issue_report()  # 使用标准模板
    update_documentation()
    suggest_next_steps()

if is_critical(error):
    recommend_urgent_fix()
    create_hotfix_version()
else:
    schedule_for_next_release()
```

---

## 📊 监控指标

### 关键指标

| 指标 | 健康阈值 | 警告阈值 | 危险阈值 |
|-----|---------|---------|---------|
| **成功率** | ≥80% | 60-80% | <60% |
| **响应时间** | <2s | 2-5s | >5s |
| **核心功能可用** | 100% | 67-99% | <67% |
| **已知问题数** | 0-2 | 3-5 | >5 |

### 趋势监控

定期（每周）生成趋势图：

```bash
# 收集一周的健康检查结果
ls health_report_*.json | tail -7

# 分析趋势
python analyze_trends.py --days 7
```

---

## 🎓 最佳实践

### ✅ DO

1. **每次发布前**运行健康检查
2. **立即记录**新发现的问题
3. **保留历史快照**（至少3个月）
4. **使用标准模板**报告问题
5. **更新文档优先于写代码**

### ❌ DON'T

1. 不要忽略 `EXPECTED_FAIL` 的测试
2. 不要删除历史快照
3. 不要跳过文档更新
4. 不要在代码中硬编码服务器 URL
5. 不要假设 API 永远稳定

---

## 📈 成功指标

这套体系成功的标志：

- ✅ 问题在影响用户前被发现
- ✅ 每个问题都有清晰的文档记录
- ✅ 任何人（包括 AI）都能快速定位问题
- ✅ 有明确的应对流程，不需要临时决策
- ✅ 版本发布有信心，不担心上游变化

---

## 🔗 快速链接

- **完整指南:** API_STABILITY_GUIDE.md
- **API 状态:** API_STABILITY_GUIDE.md 第 1 节
- **已知问题:** API_STABILITY_GUIDE.md 第 2 节
- **故障排查:** API_STABILITY_GUIDE.md 第 6 节
- **操作清单:** API_STABILITY_GUIDE.md 第 7 节

---

## 📞 支持

- **GitHub:** 提交 Issue 时附上健康检查报告
- **文档问题:** 直接编辑 API_STABILITY_GUIDE.md
- **新功能请求:** 先检查是否上游 API 已支持

---

**记住：文档和测试是我们应对不确定性的最佳武器** 🛡️

**下次更新：** 当发现新问题或上游 API 变更时
