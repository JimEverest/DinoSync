# Dinox API 快速参考卡

> 1页纸搞定常见问题 | 打印后贴在显示器旁

---

## 🚨 紧急情况

| 问题 | 立即运行 | 查看文档 |
|-----|---------|---------|
| API 无响应 | `python health_check.py` | API_STABILITY_GUIDE.md §6.1 |
| 测试失败 | `pytest test_dinox_client.py::test_xxx -v` | API_STABILITY_GUIDE.md §2 |
| 不知道用哪个服务器 | 查看 README.md API 表格 | API_STABILITY_GUIDE.md §1.1 |
| 新的错误代码 | 记录并查 | API_STABILITY_GUIDE.md §2 |

---

## 📍 当前 API 状态 (v0.2.0)

### 服务器映射

| 服务器 | URL | 方法 |
|--------|-----|------|
| **笔记** | `dinoai.chatgo.pro` | `get_notes_list`, `get_note_by_id` |
| **AI** | `aisdk.chatgo.pro` | `search_notes`, `create_note`, `get_zettelboxes` |

### 已知问题（实时）

| 方法 | 状态 | 说明 |
|-----|------|------|
| `get_note_by_id()` | ⚠️ 404 | 端点可能未部署 |
| `create_text_note()` | ⚠️ 转写失败 | 使用 `create_note()` 替代 |

---

## 🛠️ 常用命令

```bash
# 健康检查
python health_check.py

# 完整测试
pytest test_dinox_client.py -v

# 查看示例
python example.py

# 生成报告
pytest --html=report.html

# 对比快照
diff snapshots/baseline.json snapshots/current_snapshot.json
```

---

## 📚 文档速查

| 需要什么 | 看哪里 |
|---------|--------|
| 当前 API 状态 | API_STABILITY_GUIDE.md §1 |
| 已知问题列表 | API_STABILITY_GUIDE.md §2 |
| 测试策略 | API_STABILITY_GUIDE.md §3 |
| 故障排查 | API_STABILITY_GUIDE.md §6 |
| 操作检查清单 | API_STABILITY_GUIDE.md §7 |
| 使用指南 | API_PROTECTION_README.md |
| API 参考 | README.md §📚 |

---

## 🔄 标准流程

### 发布前检查

```
□ python health_check.py
□ pytest test_dinox_client.py -v
□ 更新 CHANGELOG.md
□ 更新版本号
□ git tag v0.x.0
```

### 发现问题

```
1. health_check.py → 确认问题
2. 查 §2 已知问题 → 是否已知
3. 记录到 §2 → 更新文档
4. 决策：紧急修复 vs 计划修复
5. 更新测试用例
```

### 定期维护

```
每周: health_check.py
每月: 完整测试 + 文档审查
```

---

## 💡 决策矩阵

| 错误类型 | 是否核心功能 | 操作 |
|---------|-------------|------|
| 404 | 是 | 🔴 紧急修复 |
| 404 | 否 | ⚠️ 记录问题 |
| 500 | 是 | 🔴 紧急排查 |
| 500 | 否 | ⚠️ 记录+监控 |
| 认证错误 | - | 🔴 验证Token |
| 超时 | - | ⚠️ 检查网络 |

---

## 🎯 给 AI 的指令

```
遇到 API 问题时：
1. 运行 health_check.py
2. 查 API_STABILITY_GUIDE.md §2（已知问题）
3. 使用 §8.2 模板报告
4. 按 §7 检查清单操作
```

---

## 📞 紧急联系

- **健康检查:** `python health_check.py`
- **GitHub:** JimEverest/DinoSync
- **PyPI:** pypi.org/project/dinox-api
- **完整文档:** API_STABILITY_GUIDE.md

---

**打印此页并保存** 📄  
最后更新: 2025-10-22
