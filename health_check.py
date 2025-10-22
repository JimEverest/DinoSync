#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Dinox API Health Check - 快速验证所有端点状态
用途: 每次部署前、定期监控、问题排查
运行: python health_check.py
"""

import asyncio
from datetime import datetime
from dinox_client import DinoxClient, DinoxAPIError, __version__
import json
import sys
import os

# 从环境变量获取 Token
API_TOKEN = os.environ.get("DINOX_API_TOKEN", "test_token_placeholder")
TIMEOUT = 10  # 健康检查超时时间（秒）

# 端点健康检查定义
HEALTH_CHECKS = {
    "note_server": {
        "server": "https://dinoai.chatgo.pro",
        "description": "笔记服务器 - 负责笔记查询和管理",
        "tests": [
            {
                "name": "get_notes_list",
                "description": "获取笔记列表（增量同步）",
                "method": lambda c: c.get_notes_list(last_sync_time="2025-10-22 00:00:00"),
                "expected_type": list,
                "critical": True  # 核心功能
            },
            {
                "name": "get_note_by_id",
                "description": "根据ID获取笔记",
                "method": lambda c: c.get_note_by_id("test-id-12345"),
                "expected_errors": [404],  # 已知会返回404
                "critical": False,
                "known_issue": "端点可能未部署或路径变更"
            }
        ]
    },
    "ai_server": {
        "server": "https://aisdk.chatgo.pro",
        "description": "AI 服务器 - 负责搜索和创建功能",
        "tests": [
            {
                "name": "search_notes",
                "description": "搜索笔记内容",
                "method": lambda c: c.search_notes(["test"]),
                "expected_type": dict,
                "critical": True
            },
            {
                "name": "get_zettelboxes",
                "description": "获取卡片盒列表",
                "method": lambda c: c.get_zettelboxes(),
                "expected_type": list,
                "critical": False
            },
            {
                "name": "create_note",
                "description": "创建测试笔记",
                "method": lambda c: c.create_note(
                    content=f"# Health Check Test\n\nTimestamp: {datetime.now().isoformat()}\n\nThis note was created by automated health check."
                ),
                "expected_type": dict,
                "critical": True,
                "cleanup": True  # 标记为测试数据
            }
        ]
    }
}


async def run_health_check():
    """执行完整健康检查"""
    report = {
        "timestamp": datetime.now().isoformat(),
        "client_version": __version__,
        "overall_status": "HEALTHY",
        "summary": {
            "total_tests": 0,
            "passed": 0,
            "failed": 0,
            "expected_failures": 0,
            "timeouts": 0
        },
        "servers": {}
    }
    
    print(f"🏥 Dinox API 健康检查")
    print(f"{'='*60}")
    print(f"📅 时间: {report['timestamp']}")
    print(f"📦 客户端版本: {__version__}")
    print(f"🔑 Token: {'[已配置]' if API_TOKEN != 'test_token_placeholder' else '[未配置 - 使用测试token]'}")
    print(f"{'='*60}\n")
    
    async with DinoxClient(api_token=API_TOKEN) as client:
        for server_name, server_config in HEALTH_CHECKS.items():
            server_report = {
                "url": server_config["server"],
                "description": server_config["description"],
                "status": "HEALTHY",
                "tests": []
            }
            
            print(f"🖥️  测试服务器: {server_name.upper()}")
            print(f"   URL: {server_config['server']}")
            print(f"   {server_config['description']}\n")
            
            for test in server_config["tests"]:
                test_result = {
                    "name": test["name"],
                    "description": test["description"],
                    "status": "UNKNOWN",
                    "critical": test.get("critical", False),
                    "known_issue": test.get("known_issue"),
                    "error": None,
                    "response_time_ms": 0
                }
                
                report["summary"]["total_tests"] += 1
                
                # 显示测试信息
                critical_mark = " 🔴 [核心]" if test.get("critical") else ""
                print(f"   📝 {test['name']}{critical_mark}")
                print(f"      {test['description']}")
                
                start_time = asyncio.get_event_loop().time()
                try:
                    result = await asyncio.wait_for(
                        test["method"](client),
                        timeout=TIMEOUT
                    )
                    elapsed = asyncio.get_event_loop().time() - start_time
                    test_result["response_time_ms"] = int(elapsed * 1000)
                    
                    # 验证返回类型
                    if "expected_type" in test:
                        if isinstance(result, test["expected_type"]):
                            test_result["status"] = "PASS"
                            report["summary"]["passed"] += 1
                            print(f"      ✅ 通过 ({test_result['response_time_ms']}ms)")
                        else:
                            test_result["status"] = "FAIL"
                            test_result["error"] = f"类型错误: 期望 {test['expected_type']}, 实际 {type(result)}"
                            report["summary"]["failed"] += 1
                            print(f"      ❌ 失败: {test_result['error']}")
                            
                            if test.get("critical"):
                                server_report["status"] = "DEGRADED"
                                report["overall_status"] = "DEGRADED"
                    else:
                        test_result["status"] = "PASS"
                        report["summary"]["passed"] += 1
                        print(f"      ✅ 通过 ({test_result['response_time_ms']}ms)")
                        
                except DinoxAPIError as e:
                    elapsed = asyncio.get_event_loop().time() - start_time
                    test_result["response_time_ms"] = int(elapsed * 1000)
                    
                    # 检查是否是预期的错误
                    if "expected_errors" in test and e.status_code in test["expected_errors"]:
                        test_result["status"] = "EXPECTED_FAIL"
                        test_result["error"] = f"预期错误: [{e.code}] {e.message}"
                        report["summary"]["expected_failures"] += 1
                        print(f"      ⚠️  预期失败: [{e.code}] ({test_result['response_time_ms']}ms)")
                        if test.get("known_issue"):
                            print(f"      💡 已知问题: {test['known_issue']}")
                    else:
                        test_result["status"] = "FAIL"
                        test_result["error"] = f"[{e.code}] {e.message}"
                        report["summary"]["failed"] += 1
                        print(f"      ❌ 失败: {test_result['error']} ({test_result['response_time_ms']}ms)")
                        
                        if test.get("critical"):
                            server_report["status"] = "DEGRADED"
                            report["overall_status"] = "DEGRADED"
                            
                except asyncio.TimeoutError:
                    test_result["status"] = "TIMEOUT"
                    test_result["error"] = f"超时 (>{TIMEOUT}s)"
                    report["summary"]["timeouts"] += 1
                    print(f"      ⏱️  超时: {test_result['error']}")
                    
                    if test.get("critical"):
                        server_report["status"] = "UNHEALTHY"
                        report["overall_status"] = "UNHEALTHY"
                
                except Exception as e:
                    test_result["status"] = "ERROR"
                    test_result["error"] = f"未知错误: {str(e)}"
                    report["summary"]["failed"] += 1
                    print(f"      💥 错误: {test_result['error']}")
                
                server_report["tests"].append(test_result)
                print()  # 空行
            
            report["servers"][server_name] = server_report
            print()  # 服务器之间的空行
    
    return report


def print_summary(report):
    """打印总结信息"""
    print(f"\n{'='*60}")
    print("📊 健康检查总结")
    print(f"{'='*60}\n")
    
    # 整体状态
    status_emoji = {
        "HEALTHY": "✅",
        "DEGRADED": "⚠️",
        "UNHEALTHY": "❌"
    }.get(report["overall_status"], "❓")
    
    print(f"整体状态: {status_emoji} {report['overall_status']}\n")
    
    # 统计信息
    summary = report["summary"]
    print(f"测试统计:")
    print(f"  总计: {summary['total_tests']}")
    print(f"  ✅ 通过: {summary['passed']}")
    print(f"  ❌ 失败: {summary['failed']}")
    print(f"  ⚠️  预期失败: {summary['expected_failures']}")
    print(f"  ⏱️  超时: {summary['timeouts']}")
    
    # 成功率
    if summary['total_tests'] > 0:
        success_rate = (summary['passed'] / summary['total_tests']) * 100
        print(f"  📈 成功率: {success_rate:.1f}%")
    
    # 服务器状态
    print(f"\n服务器状态:")
    for server_name, server_data in report["servers"].items():
        status_emoji = {
            "HEALTHY": "✅",
            "DEGRADED": "⚠️",
            "UNHEALTHY": "❌"
        }.get(server_data["status"], "❓")
        print(f"  {status_emoji} {server_name}: {server_data['status']}")
    
    # 关键问题
    critical_failures = []
    for server_name, server_data in report["servers"].items():
        for test in server_data["tests"]:
            if test["critical"] and test["status"] not in ["PASS", "EXPECTED_FAIL"]:
                critical_failures.append(f"{server_name}.{test['name']}")
    
    if critical_failures:
        print(f"\n🔴 核心功能异常:")
        for failure in critical_failures:
            print(f"  - {failure}")
    
    print(f"\n{'='*60}\n")


def save_report(report):
    """保存详细报告"""
    # JSON 报告
    timestamp_str = datetime.now().strftime('%Y%m%d_%H%M%S')
    json_file = f"health_report_{timestamp_str}.json"
    
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"📄 详细报告已保存: {json_file}")
    
    # 快照文件（用于对比）
    snapshot_file = "snapshots/current_snapshot.json"
    os.makedirs("snapshots", exist_ok=True)
    
    with open(snapshot_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"📸 快照已更新: {snapshot_file}")
    
    return json_file


async def main():
    """主函数"""
    try:
        # 运行健康检查
        report = await run_health_check()
        
        # 打印总结
        print_summary(report)
        
        # 保存报告
        report_file = save_report(report)
        
        # 建议操作
        if report["overall_status"] == "UNHEALTHY":
            print("⚠️  发现严重问题，建议:")
            print("  1. 检查网络连接和 Token 有效性")
            print("  2. 查看 API_STABILITY_GUIDE.md 第 6 节排查流程")
            print("  3. 运行完整测试: pytest test_dinox_client.py -v")
            return 1
        elif report["overall_status"] == "DEGRADED":
            print("⚠️  部分功能异常，建议:")
            print("  1. 查看上述失败的核心功能")
            print("  2. 检查 API_STABILITY_GUIDE.md 已知问题列表")
            print("  3. 考虑使用替代方法或等待恢复")
            return 0
        else:
            print("✅ 所有检查通过，API 运行正常！")
            return 0
            
    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断检查")
        return 130
    except Exception as e:
        print(f"\n\n💥 健康检查失败: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
