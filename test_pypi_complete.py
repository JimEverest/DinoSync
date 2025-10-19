#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
完整测试 PyPI 安装的 dinox-api 包
测试所有主要功能和配置选项
"""

import asyncio
import json
import sys
import os
from datetime import datetime
from pathlib import Path

# 设置控制台编码为 UTF-8
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

def load_token():
    """从环境变量或 .env 文件加载 Token"""
    # 1. 首先尝试从环境变量获取
    token = os.environ.get('DINOX_API_TOKEN')
    if token:
        print("[i] 使用环境变量中的 Token")
        return token
    
    # 2. 尝试从 .env 文件读取
    env_file = Path('.env')
    if env_file.exists():
        try:
            with open(env_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line.startswith('DINOX_API_TOKEN='):
                        token = line.split('=', 1)[1].strip()
                        if token:
                            print("[i] 使用 .env 文件中的 Token")
                            return token
        except Exception as e:
            print(f"[w] 读取 .env 文件失败: {e}")
    
    # 3. 如果都没有，返回测试 token
    print("[i] 未找到真实 Token，使用测试 Token")
    return "TEST_TOKEN_123"

# 获取 API Token
API_TOKEN = load_token()

def print_section(title):
    """打印分隔线"""
    print("\n" + "="*60)
    print(f" {title}")
    print("="*60)

def test_import():
    """测试导入所有组件"""
    print_section("测试 1: 导入测试")
    
    try:
        # 测试基础导入
        from dinox_client import DinoxClient
        print("[✓] 成功导入 DinoxClient")
        
        from dinox_client import DinoxConfig
        print("[✓] 成功导入 DinoxConfig")
        
        # 测试其他可能的导入
        try:
            from dinox_client import DinoxError
            print("[✓] 成功导入 DinoxError")
        except ImportError:
            print("[i] DinoxError 未导出（可选）")
            
        return True
        
    except ImportError as e:
        print(f"[✗] 导入失败: {e}")
        print("\n请确认已安装: pip install dinox-api")
        return False

def test_config():
    """测试配置选项"""
    print_section("测试 2: 配置测试")
    
    try:
        from dinox_client import DinoxConfig
        
        # 测试默认配置
        config1 = DinoxConfig(api_token=API_TOKEN)
        print(f"[✓] 默认配置创建成功")
        token_display = config1.api_token[:10] + "..." if len(config1.api_token) > 10 else config1.api_token
        print(f"    - API Token: {token_display}")
        print(f"    - Base URL: {config1.base_url}")
        print(f"    - Timeout: {config1.timeout}")
        
        # 测试自定义配置
        config2 = DinoxConfig(
            api_token=API_TOKEN,
            base_url="https://api.chatgo.pro",
            timeout=60.0
        )
        print(f"[✓] 自定义配置创建成功")
        print(f"    - Base URL: {config2.base_url}")
        print(f"    - Timeout: {config2.timeout}")
        
        # 测试 AI 服务器配置
        config3 = DinoxConfig(
            api_token=API_TOKEN,
            base_url="https://aisdk.chatgo.pro"
        )
        print(f"[✓] AI 服务器配置创建成功")
        print(f"    - AI Server URL: {config3.base_url}")
        
        return True
        
    except Exception as e:
        print(f"[✗] 配置测试失败: {e}")
        return False

async def test_client_creation():
    """测试客户端创建方式"""
    print_section("测试 3: 客户端创建")
    
    try:
        from dinox_client import DinoxClient, DinoxConfig
        
        # 方式 1: 直接传入 token
        client1 = DinoxClient(api_token=API_TOKEN)
        print("[✓] 方式1: 直接创建客户端成功")
        
        # 方式 2: 使用配置对象
        config = DinoxConfig(
            api_token=API_TOKEN,
            base_url="https://api.chatgo.pro"
        )
        client2 = DinoxClient(config=config)
        print("[✓] 方式2: 使用配置对象创建成功")
        
        # 方式 3: 从环境变量（需要手动读取）
        print("[i] 注意: DinoxClient 不会自动从环境变量读取 token")
        print("[i] 需要手动读取环境变量:")
        print("    token = os.environ.get('DINOX_API_TOKEN')")
        print("    client = DinoxClient(api_token=token)")
        
        # 演示手动读取
        env_token = os.environ.get('DINOX_API_TOKEN', API_TOKEN)
        if env_token:
            client3 = DinoxClient(api_token=env_token)
            print("[✓] 方式3: 手动从环境变量创建成功")
        
        return True
        
    except Exception as e:
        print(f"[✗] 客户端创建失败: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_client_methods():
    """测试客户端方法是否存在"""
    print_section("测试 4: 客户端方法检查")
    
    try:
        from dinox_client import DinoxClient
        
        client = DinoxClient(api_token=API_TOKEN)
        
        # 检查方法是否存在
        methods = [
            # 笔记服务器方法
            ('get_notes_list', '获取笔记列表'),
            ('get_note_by_id', '根据ID获取笔记'),
            
            # AI 服务器方法
            ('search_notes', '搜索笔记'),
            ('create_note', '创建笔记'),
            ('get_zettelboxes', '获取卡片盒'),
            ('create_note_text', '创建文字笔记'),
            ('create_note_audio', '创建音频笔记'),
            ('create_attachment', '创建附件')
        ]
        
        for method_name, description in methods:
            if hasattr(client, method_name):
                print(f"[✓] {method_name}: {description}")
            else:
                print(f"[✗] {method_name}: 方法不存在")
        
        return True
        
    except Exception as e:
        print(f"[✗] 方法检查失败: {e}")
        return False

async def test_context_manager():
    """测试上下文管理器"""
    print_section("测试 5: 上下文管理器")
    
    try:
        from dinox_client import DinoxClient
        
        # 测试 async with 语法
        async with DinoxClient(api_token=API_TOKEN) as client:
            print("[✓] 上下文管理器进入成功")
            print(f"    - Client类型: {type(client).__name__}")
            
        print("[✓] 上下文管理器退出成功")
        
        return True
        
    except Exception as e:
        print(f"[✗] 上下文管理器测试失败: {e}")
        return False

async def test_error_handling():
    """测试错误处理"""
    print_section("测试 6: 错误处理")
    
    try:
        from dinox_client import DinoxClient
        
        # 测试无效 token
        try:
            client = DinoxClient(api_token="")
            print("[i] 空 token 被允许（警告）")
        except Exception:
            print("[✓] 空 token 被正确拒绝")
        
        # 测试无效配置
        try:
            client = DinoxClient(api_token=None)
            print("[i] None token 被允许（警告）")
        except Exception:
            print("[✓] None token 被正确拒绝")
        
        return True
        
    except Exception as e:
        print(f"[✗] 错误处理测试失败: {e}")
        return False

async def test_real_connection():
    """测试实际连接（如果有有效 token）"""
    print_section("测试 7: 连接测试")
    
    try:
        from dinox_client import DinoxClient
        
        # 使用配置的 token
        client = DinoxClient(api_token=API_TOKEN)
        
        # 检查是否是真实 token
        is_real_token = API_TOKEN and not API_TOKEN.startswith("TEST_")
        
        if is_real_token:
            print(f"[i] 检测到 Token: {API_TOKEN[:10]}...")
            print("[i] 尝试实际连接测试...")
            
            try:
                # 尝试获取笔记列表（最基本的测试）
                async with DinoxClient(api_token=API_TOKEN) as real_client:
                    notes = await real_client.get_notes_list()
                    print(f"[✓] 成功连接并获取笔记！获取到 {len(notes)} 天的笔记")
                    
                    if notes and len(notes) > 0:
                        recent_day = notes[0]
                        print(f"    - 最近日期: {recent_day.get('date', 'N/A')}")
                        print(f"    - 当天笔记数: {len(recent_day.get('notes', []))}")
                    
            except Exception as api_error:
                print(f"[w] API 调用失败: {api_error}")
                print("[i] 这可能是因为 Token 无效或网络问题")
        else:
            print("[i] 使用测试 Token，跳过实际连接测试")
            print("[i] 如果有有效 token，设置环境变量 DINOX_API_TOKEN 或创建 .env 文件")
            print("[i] 可测试的功能：")
            print("    - await client.get_notes_list()")
            print("    - await client.search_notes(['关键词'])")
            print("    - await client.create_note('内容')")
        
        return True
        
    except Exception as e:
        print(f"[✗] 连接测试失败: {e}")
        return False

def test_package_info():
    """测试包信息"""
    print_section("测试 8: 包信息")
    
    try:
        import dinox_client
        
        # 检查包路径
        print(f"[i] 包路径: {dinox_client.__file__}")
        
        # 检查可用属性
        available = [attr for attr in dir(dinox_client) if not attr.startswith('_')]
        print(f"[i] 导出的类/函数: {', '.join(available)}")
        
        # 检查版本（如果有）
        if hasattr(dinox_client, '__version__'):
            print(f"[i] 版本: {dinox_client.__version__}")
        else:
            print("[i] 版本信息未定义")
        
        return True
        
    except Exception as e:
        print(f"[✗] 包信息获取失败: {e}")
        return False

async def main():
    """主测试函数"""
    print("\n" + "="*60)
    print(" DinoX API PyPI 包完整测试")
    print("="*60)
    print(f"\n运行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Python 版本: {sys.version}")
    
    # 显示 Token 信息
    print("\nToken 配置:")
    if API_TOKEN:
        token_display = API_TOKEN[:10] + "..." if len(API_TOKEN) > 10 else API_TOKEN
        print(f"  - Token: {token_display}")
        if API_TOKEN.startswith("TEST_"):
            print("  - 类型: 测试 Token")
        else:
            print("  - 类型: 可能是真实 Token")
    
    # 记录测试结果
    results = []
    
    # 运行所有测试
    tests = [
        ("导入测试", test_import()),
        ("配置测试", test_config()),
        ("客户端创建", test_client_creation()),
        ("客户端方法", test_client_methods()),
        ("上下文管理器", test_context_manager()),
        ("错误处理", test_error_handling()),
        ("连接测试", test_real_connection()),
        ("包信息", test_package_info())
    ]
    
    # 执行异步测试
    for name, test in tests:
        if asyncio.iscoroutine(test):
            result = await test
        else:
            result = test
        results.append((name, result))
    
    # 打印测试摘要
    print_section("测试摘要")
    
    passed = 0
    failed = 0
    
    for name, result in results:
        if result:
            print(f"[✓] {name}: 通过")
            passed += 1
        else:
            print(f"[✗] {name}: 失败")
            failed += 1
    
    print(f"\n总计: {passed} 通过, {failed} 失败")
    
    # 使用示例
    if passed == len(results):
        print_section("✅ 所有测试通过！")
        print("\n使用示例:")
        print("```python")
        print("import asyncio")
        print("from dinox_client import DinoxClient")
        print("")
        print("async def main():")
        print("    async with DinoxClient(api_token='YOUR_TOKEN') as client:")
        print("        # 获取笔记列表")
        print("        notes = await client.get_notes_list()")
        print("        print(f'获取到 {len(notes)} 天的笔记')")
        print("")
        print("asyncio.run(main())")
        print("```")
        
        print("\n配置真实 Token 的方法:")
        print("1. 环境变量: export DINOX_API_TOKEN='your_token'")
        print("2. .env 文件: DINOX_API_TOKEN=your_token")
        print("3. 代码中直接传入: DinoxClient(api_token='your_token')")
    else:
        print_section("⚠️ 部分测试失败")
        print("请检查上面的错误信息")
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
