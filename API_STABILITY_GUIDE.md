# Dinox API 稳定性保障指南

**目标受众：** 开发者和 Coding AI  
**用途：** 应对上游 API 变更和不稳定性的预案  
**版本：** 1.0  
**最后更新：** 2025-10-22

---

## 📋 目录

1. [当前 API 状态文档](#1-当前-api-状态文档)
2. [已知问题与限制](#2-已知问题与限制)
3. [测试策略](#3-测试策略)
4. [变更监控方案](#4-变更监控方案)
5. [版本兼容性策略](#5-版本兼容性策略)
6. [故障排查流程](#6-故障排查流程)
7. [更新检查清单](#7-更新检查清单)

---

## 1. 当前 API 状态文档

### 1.1 服务器架构映射

**当前状态（v0.2.0）：**

| 服务器类型 | URL | 稳定性 | 响应时间 | 方法映射 |
|-----------|-----|--------|---------|---------|
| **笔记服务器** | `https://dinoai.chatgo.pro` | ⚠️ 中等 | ~1.2s | `get_notes_list`, `get_note_by_id`, `update_note` |
| **AI 服务器** | `https://aisdk.chatgo.pro` | ✅ 稳定 | ~0.8s | `search_notes`, `create_note`, `get_zettelboxes`, `create_text_note` |

**记录时间：** 2025-10-22  
**测试条件：** 实际 API Token，中国大陆网络环境

### 1.2 端点状态矩阵

| 方法 | 端点路径 | HTTP方法 | 服务器 | 状态 | 最后验证 | 已知问题 |
|-----|---------|---------|--------|------|---------|---------|
| `get_notes_list()` | `/openapi/v5/notes` | POST | Note | ✅ | 2025-10-22 | 无 |
| `get_note_by_id()` | `/api/openapi/note/{id}` | GET | Note | ⚠️ | 2025-10-22 | 返回 404（可能未部署） |
| `search_notes()` | `/api/openapi/searchNotes` | POST | AI | ✅ | 2025-10-22 | 无 |
| `create_note()` | `/api/openapi/createNote` | POST | AI | ✅ | 2025-10-22 | 无 |
| `create_text_note()` | `/openapi/text/input` | POST | AI | ⚠️ | 2025-10-22 | 可能返回"转写失败" |
| `get_zettelboxes()` | `/api/openapi/zettelboxes` | GET | AI | ✅ | 2025-10-22 | 需要有效认证 |
| `update_note()` | `/openapi/updateNote` | POST | Note | ⚠️ | 2025-10-22 | 可能未部署 |

**图例：**
- ✅ 稳定可用
- ⚠️ 部分可用或不稳定
- ❌ 已知不可用
- 🔄 状态未知，需要验证

---

## 2. 已知问题与限制

### 2.1 服务器级别问题

#### 问题 #1: 笔记服务器部分端点返回 404

**发现日期：** 2025-10-22  
**影响方法：** `get_note_by_id()`  
**错误示例：**
```json
{
  "timestamp": 1761105843986,
  "status": 404,
  "error": "Not Found",
  "path": "/api/openapi/note/019a09ad-5bf0-7e79-9046-dbf60633ddec"
}
```

**可能原因：**
- 端点路径变更
- 端点尚未部署到生产环境
- 服务器配置问题

**当前应对：**
- 已在代码中捕获并处理 404 错误
- 测试中标记为已知失败
- 不影响核心功能 `get_notes_list()`

**监控建议：**
- 定期测试该端点（建议频率：每周）
- 检查是否有路径变更公告

---

#### 问题 #2: create_text_note() 转写失败

**发现日期：** 历史已知问题  
**影响方法：** `create_text_note()`  
**错误代码：** `0000029`  
**错误消息：** "转写失败"

**可能原因：**
- 后端转写服务不稳定
- 特定内容格式触发错误
- 功能尚在开发中

**当前应对：**
- 文档中明确标注此限制
- 提供替代方法 `create_note()`
- 测试中允许此错误

---

### 2.2 认证相关问题

#### 问题 #3: Token 过期处理不明确

**状态：** 需要验证  
**Token 格式：** JWT  
**过期时间：** 未在文档中说明

**需要验证：**
- [ ] Token 是否有过期时间
- [ ] 过期后返回什么错误代码
- [ ] 是否需要刷新机制
- [ ] 是否支持 Token 续期

**测试命令：**
```python
# 使用已知过期的 Token 测试
async with DinoxClient(api_token="EXPIRED_TOKEN") as client:
    try:
        await client.get_notes_list()
    except DinoxAPIError as e:
        print(f"过期 Token 错误码: {e.code}")
        print(f"错误消息: {e.message}")
```

---

### 2.3 服务器差异问题

#### 问题 #4: 路径前缀不一致

**观察：** 不同端点使用不同的路径前缀

- `/openapi/v5/notes` - 包含版本号
- `/api/openapi/searchNotes` - 不包含版本号
- `/openapi/text/input` - 不同的路径结构

**风险：**
- 版本升级可能改变路径
- 难以统一处理

**建议：**
- 记录所有路径变体
- 在测试中验证路径正确性

---

## 3. 测试策略

### 3.1 多层次测试架构

```
┌─────────────────────────────────────┐
│   L1: 单元测试                       │
│   测试客户端逻辑，不依赖真实 API      │
└─────────────────────────────────────┘
           ↓
┌─────────────────────────────────────┐
│   L2: 集成测试                       │
│   使用真实 API，验证端点可用性        │
└─────────────────────────────────────┘
           ↓
┌─────────────────────────────────────┐
│   L3: 健康检查测试                   │
│   快速验证所有端点状态                │
└─────────────────────────────────────┘
           ↓
┌─────────────────────────────────────┐
│   L4: 契约测试                       │
│   验证 API 响应结构是否变化           │
└─────────────────────────────────────┘
```

### 3.2 健康检查测试套件

创建 `health_check.py` 用于快速验证所有端点：

```python
#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
API Health Check - 快速验证所有端点状态
运行频率：每次部署前、每周一次定期检查
"""

import asyncio
from datetime import datetime
from dinox_client import DinoxClient, DinoxAPIError
import json

# 测试配置
API_TOKEN = "YOUR_TOKEN_HERE"
TIMEOUT = 10  # 健康检查超时时间

# 端点健康检查定义
HEALTH_CHECKS = {
    "note_server": {
        "server": "https://dinoai.chatgo.pro",
        "tests": [
            {
                "name": "get_notes_list",
                "method": lambda c: c.get_notes_list(last_sync_time="2025-10-22 00:00:00"),
                "expected_type": list,
                "critical": True  # 核心功能
            },
            {
                "name": "get_note_by_id",
                "method": lambda c: c.get_note_by_id("test-id"),
                "expected_errors": [404],  # 已知会失败
                "critical": False
            }
        ]
    },
    "ai_server": {
        "server": "https://aisdk.chatgo.pro",
        "tests": [
            {
                "name": "search_notes",
                "method": lambda c: c.search_notes(["test"]),
                "expected_type": dict,
                "critical": True
            },
            {
                "name": "get_zettelboxes",
                "method": lambda c: c.get_zettelboxes(),
                "expected_type": list,
                "critical": False
            },
            {
                "name": "create_note",
                "method": lambda c: c.create_note(f"# Health Check {datetime.now().isoformat()}"),
                "expected_type": dict,
                "critical": True
            }
        ]
    }
}

async def run_health_check():
    """执行完整健康检查"""
    report = {
        "timestamp": datetime.now().isoformat(),
        "overall_status": "HEALTHY",
        "servers": {}
    }
    
    async with DinoxClient(api_token=API_TOKEN) as client:
        for server_name, server_config in HEALTH_CHECKS.items():
            server_report = {
                "url": server_config["server"],
                "status": "HEALTHY",
                "tests": []
            }
            
            for test in server_config["tests"]:
                test_result = {
                    "name": test["name"],
                    "status": "UNKNOWN",
                    "critical": test.get("critical", False),
                    "error": None,
                    "response_time": 0
                }
                
                start_time = asyncio.get_event_loop().time()
                try:
                    result = await asyncio.wait_for(
                        test["method"](client),
                        timeout=TIMEOUT
                    )
                    test_result["response_time"] = asyncio.get_event_loop().time() - start_time
                    
                    # 验证返回类型
                    if "expected_type" in test:
                        if isinstance(result, test["expected_type"]):
                            test_result["status"] = "PASS"
                        else:
                            test_result["status"] = "FAIL"
                            test_result["error"] = f"Expected {test['expected_type']}, got {type(result)}"
                    else:
                        test_result["status"] = "PASS"
                        
                except DinoxAPIError as e:
                    test_result["response_time"] = asyncio.get_event_loop().time() - start_time
                    
                    # 检查是否是预期的错误
                    if "expected_errors" in test and e.status_code in test["expected_errors"]:
                        test_result["status"] = "EXPECTED_FAIL"
                        test_result["error"] = f"Expected error: {e.code}"
                    else:
                        test_result["status"] = "FAIL"
                        test_result["error"] = f"[{e.code}] {e.message}"
                        
                        if test.get("critical"):
                            server_report["status"] = "DEGRADED"
                            report["overall_status"] = "DEGRADED"
                            
                except asyncio.TimeoutError:
                    test_result["status"] = "TIMEOUT"
                    test_result["error"] = f"Timeout after {TIMEOUT}s"
                    if test.get("critical"):
                        server_report["status"] = "UNHEALTHY"
                        report["overall_status"] = "UNHEALTHY"
                
                server_report["tests"].append(test_result)
            
            report["servers"][server_name] = server_report
    
    return report

async def main():
    """运行健康检查并生成报告"""
    print("🏥 Dinox API Health Check")
    print("=" * 60)
    
    report = await run_health_check()
    
    # 打印报告
    print(f"\n⏰ 检查时间: {report['timestamp']}")
    print(f"📊 整体状态: {report['overall_status']}\n")
    
    for server_name, server_data in report["servers"].items():
        print(f"\n🖥️  {server_name.upper()}")
        print(f"   URL: {server_data['url']}")
        print(f"   状态: {server_data['status']}")
        print(f"   测试结果:")
        
        for test in server_data["tests"]:
            status_icon = {
                "PASS": "✅",
                "FAIL": "❌",
                "EXPECTED_FAIL": "⚠️",
                "TIMEOUT": "⏱️",
                "UNKNOWN": "❓"
            }.get(test["status"], "❓")
            
            critical_mark = " [CRITICAL]" if test.get("critical") else ""
            print(f"      {status_icon} {test['name']}{critical_mark}")
            print(f"         响应时间: {test['response_time']:.2f}s")
            if test.get("error"):
                print(f"         错误: {test['error']}")
    
    # 保存 JSON 报告
    report_file = f"health_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"\n📄 详细报告已保存至: {report_file}")
    
    # 返回退出码
    if report["overall_status"] == "UNHEALTHY":
        return 1
    return 0

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
```

**使用场景：**
- 每次发布前运行
- CI/CD 流程中集成
- 定期监控（cron job）
- 问题排查时的第一步

---

### 3.3 契约测试（Schema Validation）

创建 `contract_tests.py` 验证 API 响应结构：

```python
#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
API Contract Tests - 验证 API 响应格式是否变化
当这些测试失败时，说明上游 API 可能已经变更
"""

import asyncio
from dinox_client import DinoxClient

# 预期的响应结构
EXPECTED_SCHEMAS = {
    "get_notes_list": {
        "type": "list",
        "item_schema": {
            "date": str,
            "notes": list
        },
        "note_schema": {
            "noteId": str,
            "title": (str, type(None)),
            "content": str,
            "createTime": str,
            "isDel": bool
        }
    },
    "search_notes": {
        "type": "dict",
        "schema": {
            "content": str
        }
    },
    "get_zettelboxes": {
        "type": "list",
        "item_schema": {
            "id": str,
            "name": str
        }
    }
}

def validate_schema(data, schema, path="root"):
    """验证数据是否符合预期结构"""
    errors = []
    
    # 验证类型
    if "type" in schema:
        expected_type = {"list": list, "dict": dict, "str": str}.get(schema["type"], schema["type"])
        if not isinstance(data, expected_type):
            errors.append(f"{path}: Expected {schema['type']}, got {type(data).__name__}")
            return errors
    
    # 验证字典字段
    if "schema" in schema and isinstance(data, dict):
        for key, expected_type in schema["schema"].items():
            if key not in data:
                errors.append(f"{path}.{key}: Missing required field")
            elif not isinstance(data[key], expected_type):
                errors.append(f"{path}.{key}: Expected {expected_type}, got {type(data[key])}")
    
    # 验证列表项
    if "item_schema" in schema and isinstance(data, list) and len(data) > 0:
        for i, item in enumerate(data[:3]):  # 只检查前3项
            item_errors = validate_schema(item, {"schema": schema["item_schema"]}, f"{path}[{i}]")
            errors.extend(item_errors)
    
    return errors

async def test_contracts():
    """运行所有契约测试"""
    results = {}
    
    async with DinoxClient(api_token="YOUR_TOKEN") as client:
        # 测试 get_notes_list
        notes = await client.get_notes_list()
        errors = validate_schema(notes, EXPECTED_SCHEMAS["get_notes_list"])
        results["get_notes_list"] = {"pass": len(errors) == 0, "errors": errors}
        
        # 测试 search_notes
        search_result = await client.search_notes(["test"])
        errors = validate_schema(search_result, EXPECTED_SCHEMAS["search_notes"])
        results["search_notes"] = {"pass": len(errors) == 0, "errors": errors}
        
        # 测试 get_zettelboxes
        boxes = await client.get_zettelboxes()
        errors = validate_schema(boxes, EXPECTED_SCHEMAS["get_zettelboxes"])
        results["get_zettelboxes"] = {"pass": len(errors) == 0, "errors": errors}
    
    # 输出结果
    print("📋 Contract Test Results")
    print("=" * 60)
    for method, result in results.items():
        status = "✅ PASS" if result["pass"] else "❌ FAIL"
        print(f"\n{method}: {status}")
        if not result["pass"]:
            print("  Errors:")
            for error in result["errors"]:
                print(f"    - {error}")
    
    return all(r["pass"] for r in results.values())
```

---

### 3.4 测试执行计划

| 测试类型 | 频率 | 触发条件 | 负责人 |
|---------|------|---------|--------|
| 单元测试 | 每次提交 | Git push | CI/CD |
| 健康检查 | 每天 | Cron job | 自动化 |
| 契约测试 | 每周 | 手动或定时 | 开发者 |
| 完整集成测试 | 发布前 | 手动触发 | 开发者 |
| 性能基准测试 | 每月 | 手动触发 | 开发者 |

---

## 4. 变更监控方案

### 4.1 变更检测检查清单

**每次测试时记录：**

```yaml
# api_snapshot_YYYYMMDD.yaml
date: "2025-10-22"
version: "0.2.0"

servers:
  note_server:
    url: "https://dinoai.chatgo.pro"
    reachable: true
    response_time_ms: 1200
    
  ai_server:
    url: "https://aisdk.chatgo.pro"
    reachable: true
    response_time_ms: 800

endpoints:
  - name: "get_notes_list"
    path: "/openapi/v5/notes"
    method: "POST"
    status: "working"
    response_fields: ["date", "notes"]
    
  - name: "search_notes"
    path: "/api/openapi/searchNotes"
    method: "POST"
    status: "working"
    response_fields: ["content"]

known_issues:
  - endpoint: "get_note_by_id"
    issue: "返回 404"
    since: "2025-10-22"
    impact: "medium"
```

### 4.2 自动对比工具

```python
#!/usr/bin/env python
"""
compare_snapshots.py - 对比两次 API 快照，发现变化
"""

import yaml
import sys

def compare_snapshots(old_file, new_file):
    """对比两个快照文件"""
    with open(old_file) as f:
        old = yaml.safe_load(f)
    with open(new_file) as f:
        new = yaml.safe_load(f)
    
    changes = []
    
    # 对比服务器
    for server_name in old["servers"]:
        old_server = old["servers"][server_name]
        new_server = new["servers"].get(server_name, {})
        
        if not new_server:
            changes.append(f"⚠️  服务器 {server_name} 已移除")
        elif old_server["url"] != new_server["url"]:
            changes.append(f"🔄 服务器 {server_name} URL 变更: {old_server['url']} → {new_server['url']}")
    
    # 对比端点
    old_endpoints = {e["name"]: e for e in old["endpoints"]}
    new_endpoints = {e["name"]: e for e in new["endpoints"]}
    
    for name, old_ep in old_endpoints.items():
        if name not in new_endpoints:
            changes.append(f"⚠️  端点 {name} 已移除")
        else:
            new_ep = new_endpoints[name]
            if old_ep["path"] != new_ep["path"]:
                changes.append(f"🔄 端点 {name} 路径变更: {old_ep['path']} → {new_ep['path']}")
            if old_ep["status"] != new_ep["status"]:
                changes.append(f"📊 端点 {name} 状态变更: {old_ep['status']} → {new_ep['status']}")
    
    return changes

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python compare_snapshots.py <old_snapshot.yaml> <new_snapshot.yaml>")
        sys.exit(1)
    
    changes = compare_snapshots(sys.argv[1], sys.argv[2])
    
    if changes:
        print("🔍 发现以下变化:\n")
        for change in changes:
            print(f"  {change}")
        sys.exit(1)
    else:
        print("✅ 未发现变化")
        sys.exit(0)
```

---

## 5. 版本兼容性策略

### 5.1 语义化版本控制

```
dinox-api 版本号: MAJOR.MINOR.PATCH

MAJOR (主版本号): 上游 API 不兼容变更
  例如: 端点路径变更、响应结构大改

MINOR (次版本号): 新增功能，向后兼容
  例如: 新增端点、新增可选参数

PATCH (修订号): Bug 修复，完全兼容
  例如: 错误处理优化、文档更新
```

### 5.2 兼容性矩阵

| dinox-api 版本 | Dinox API 状态 | 兼容性 | 说明 |
|---------------|---------------|--------|------|
| 0.1.0 | 2025-10-19 | ✅ | 初始版本 |
| 0.2.0 | 2025-10-22 | ✅ | 添加自动路由 |
| 0.3.0 | TBD | 🔄 | 待定 |

### 5.3 弃用策略

当发现上游 API 变更时：

1. **立即更新文档**，标记受影响的方法
2. **保留旧方法**至少 2 个 MINOR 版本
3. **添加弃用警告**
4. **提供迁移指南**

示例：
```python
@deprecated(version="0.3.0", removed_in="0.5.0", 
            alternative="use new_method() instead")
async def old_method(self):
    """This method is deprecated..."""
    warnings.warn("old_method() is deprecated", DeprecationWarning)
    return await self.new_method()
```

---

## 6. 故障排查流程

### 6.1 问题分类决策树

```
API 调用失败
    ├─ 网络错误
    │   ├─ 检查网络连接
    │   └─ 检查服务器可达性
    │
    ├─ 认证错误 (401, 403, 000008)
    │   ├─ 验证 Token 有效性
    │   └─ 检查 Token 权限
    │
    ├─ 404 错误
    │   ├─ 检查端点路径是否正确
    │   ├─ 对照当前 API 状态文档
    │   └─ 可能是已知问题，参考第 2 节
    │
    ├─ 500 错误
    │   ├─ 记录详细错误信息
    │   ├─ 检查请求参数
    │   └─ 可能是服务器问题，等待恢复
    │
    └─ 超时
        ├─ 检查网络延迟
        ├─ 增加 timeout 参数
        └─ 考虑降级处理
```

### 6.2 诊断命令

```bash
# 1. 快速健康检查
python health_check.py

# 2. 详细测试特定端点
python -m pytest test_dinox_client.py::test_get_notes_list -v

# 3. 对比 API 快照
python compare_snapshots.py snapshots/baseline.yaml snapshots/current.yaml

# 4. 生成诊断报告
python -m pytest test_dinox_client.py --html=report.html

# 5. 测试连接性
curl -H "Authorization: YOUR_TOKEN" https://dinoai.chatgo.pro/openapi/v5/notes
```

---

## 7. 更新检查清单

### 7.1 发现上游变更时的操作清单

- [ ] **Step 1: 记录变更**
  - [ ] 创建快照文件 `api_snapshot_YYYYMMDD.yaml`
  - [ ] 记录所有观察到的变化
  - [ ] 截图或保存错误响应

- [ ] **Step 2: 影响评估**
  - [ ] 运行完整测试套件
  - [ ] 统计受影响的方法
  - [ ] 评估严重程度（Critical/High/Medium/Low）

- [ ] **Step 3: 更新文档**
  - [ ] 更新 API_STABILITY_GUIDE.md 第 2 节（已知问题）
  - [ ] 更新 README.md 的状态表格
  - [ ] 添加到 CHANGELOG.md

- [ ] **Step 4: 决策**
  - [ ] 是否需要紧急修复？
  - [ ] 是否需要发布新版本？
  - [ ] 是否需要通知用户？

- [ ] **Step 5: 实施（如需要）**
  - [ ] 修改代码适配变更
  - [ ] 更新测试用例
  - [ ] 更新版本号
  - [ ] 发布新版本

- [ ] **Step 6: 通知**
  - [ ] 更新 GitHub Release Notes
  - [ ] 更新 PyPI 描述
  - [ ] 发送变更通知（如有订阅列表）

### 7.2 定期维护清单（每月）

- [ ] 运行完整测试套件
- [ ] 检查所有端点状态
- [ ] 生成并对比 API 快照
- [ ] 审查已知问题列表
- [ ] 更新性能基准数据
- [ ] 审查 GitHub Issues
- [ ] 检查依赖包更新

---

## 8. 给 AI 的明确指令

当你（Coding AI）需要处理 Dinox API 相关问题时：

### 8.1 诊断步骤

```
1. 首先阅读本文档第 1 节，了解当前 API 状态
2. 检查第 2 节，确认是否是已知问题
3. 运行 health_check.py 获取实时状态
4. 根据第 6 节的决策树进行诊断
5. 参考第 7 节的检查清单执行操作
```

### 8.2 响应模板

发现问题时使用此模板：

```markdown
## API 问题报告

**发现时间:** YYYY-MM-DD HH:MM:SS
**影响方法:** method_name()
**严重程度:** Critical/High/Medium/Low

### 问题描述
[详细描述问题现象]

### 错误信息
```
[粘贴完整错误信息]
```

### 已知状态
- 根据 API_STABILITY_GUIDE.md 第 X 节，这是/不是已知问题
- 上次正常工作时间: YYYY-MM-DD
- 相关端点: /path/to/endpoint

### 影响范围
- 受影响的方法: [列表]
- 核心功能受影响: 是/否
- 有替代方案: 是/否

### 建议操作
1. [具体操作步骤]
2. [...]

### 需要决策
- [ ] 是否需要紧急修复?
- [ ] 是否需要发布新版本?
- [ ] 是否需要更新文档?
```

---

## 9. 快速参考

### 常用文件位置

```
项目根目录/
├── API_STABILITY_GUIDE.md          # 本文档
├── health_check.py                 # 健康检查脚本
├── contract_tests.py               # 契约测试
├── compare_snapshots.py            # 快照对比工具
├── snapshots/                      # API 快照目录
│   ├── baseline.yaml               # 基准快照
│   └── api_snapshot_YYYYMMDD.yaml  # 历史快照
└── test_dinox_client.py            # 完整测试套件
```

### 常用命令

```bash
# 快速健康检查
python health_check.py

# 完整测试
pytest test_dinox_client.py -v

# 契约测试
python contract_tests.py

# 生成报告
pytest --html=report.html --self-contained-html
```

### 关键联系人

- **项目维护者:** JimEverest
- **PyPI 包:** https://pypi.org/project/dinox-api/
- **文档:** README.md

---

## 10. 总结

作为下游开发者，我们通过以下机制保护项目稳定性：

✅ **明确的文档** - API 状态、已知问题、端点映射  
✅ **系统化测试** - 健康检查、契约测试、集成测试  
✅ **变更监控** - 快照对比、自动检测  
✅ **清晰流程** - 排查决策树、操作检查清单  
✅ **版本策略** - 语义化版本、兼容性矩阵  

**核心原则：** 
> 文档即时更新 + 测试持续监控 + 流程清晰明确 = 从容应对上游变化

---

**文档版本:** 1.0  
**最后更新:** 2025-10-22  
**下次审查:** 2025-11-22
