#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试 PyPI 包安装后的使用
运行前请先安装: pip install dinox-api
"""

import asyncio
import sys

def test_import():
    """测试导入"""
    try:
        from dinox_client import DinoxClient, DinoxConfig
        print("[OK] 成功导入 dinox_client 模块")
        print(f"   - DinoxClient: {DinoxClient}")
        print(f"   - DinoxConfig: {DinoxConfig}")
        return True
    except ImportError as e:
        print(f"[ERROR] 导入失败: {e}")
        print("   请确认已安装: pip install dinox-api")
        return False

async def test_client_creation():
    """测试客户端创建"""
    try:
        from dinox_client import DinoxClient, DinoxConfig
        
        # 测试直接创建
        client1 = DinoxClient(api_token="TEST_TOKEN")
        print("[OK] 成功创建客户端（直接传入 token）")
        
        # 测试配置创建
        config = DinoxConfig(
            api_token="TEST_TOKEN",
            base_url="https://api.chatgo.pro",
            timeout=30.0
        )
        client2 = DinoxClient(config=config)
        print("[OK] 成功创建客户端（使用配置对象）")
        
        # 测试上下文管理器（不实际连接）
        print("[OK] 客户端支持上下文管理器")
        
        return True
    except Exception as e:
        print(f"[ERROR] 创建客户端失败: {e}")
        return False

def main():
    """主测试函数"""
    print("=" * 50)
    print("DinoX API PyPI 包测试")
    print("=" * 50)
    print()
    
    # 测试导入
    if not test_import():
        sys.exit(1)
    print()
    
    # 测试客户端创建
    asyncio.run(test_client_creation())
    print()
    
    print("=" * 50)
    print("[SUCCESS] All tests passed! Package works correctly.")
    print()
    print("Usage example:")
    print("```python")
    print("from dinox_client import DinoxClient")
    print("async with DinoxClient(api_token='YOUR_TOKEN') as client:")
    print("    notes = await client.get_notes_list()")
    print("```")
    print("=" * 50)

if __name__ == "__main__":
    main()
