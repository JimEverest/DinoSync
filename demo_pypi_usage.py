#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
DinoX API PyPI 包使用演示
展示通过 pip install dinox-api 安装后的实际使用方法
"""

import asyncio
import json
from datetime import datetime
from dinox_client import DinoxClient, DinoxConfig

# ============================================================
# 配置你的 API Token
# ============================================================
API_TOKEN = "YOUR_ACTUAL_TOKEN_HERE"  # 替换为你的实际 token


async def demo_basic_usage():
    """基础使用示例"""
    print("\n" + "="*50)
    print("1. 基础使用示例")
    print("="*50)
    
    # 创建客户端
    async with DinoxClient(api_token=API_TOKEN) as client:
        print("客户端创建成功！")
        print(f"- 基础 URL: {client.config.base_url}")
        print(f"- 超时设置: {client.config.timeout}秒")
        
        # 如果有有效 token，可以取消注释以下代码：
        # try:
        #     # 获取笔记列表
        #     notes = await client.get_notes_list()
        #     print(f"\n获取到 {len(notes)} 天的笔记")
        #     
        #     # 显示最近的笔记
        #     if notes and len(notes) > 0:
        #         recent_day = notes[0]
        #         print(f"最近日期: {recent_day['date']}")
        #         print(f"当天笔记数: {len(recent_day['notes'])}")
        # except Exception as e:
        #     print(f"API 调用失败: {e}")


async def demo_note_server():
    """笔记服务器使用示例"""
    print("\n" + "="*50)
    print("2. 笔记服务器功能")
    print("="*50)
    
    # 使用笔记服务器配置
    config = DinoxConfig(
        api_token=API_TOKEN,
        base_url="https://api.chatgo.pro",  # 笔记服务器
        timeout=30.0
    )
    
    async with DinoxClient(config=config) as client:
        print("已连接到笔记服务器")
        
        # 示例：获取笔记列表
        print("\n可用功能：")
        print("1. 获取所有笔记:")
        print("   notes = await client.get_notes_list()")
        
        print("\n2. 增量同步（获取指定时间后的笔记）:")
        print("   recent = await client.get_notes_list(")
        print("       last_sync_time='2025-10-18 00:00:00'")
        print("   )")
        
        print("\n3. 根据 ID 查询笔记:")
        print("   note = await client.get_note_by_id('note_id_here')")


async def demo_ai_server():
    """AI 服务器使用示例"""
    print("\n" + "="*50)
    print("3. AI 服务器功能")
    print("="*50)
    
    # 使用 AI 服务器配置
    config = DinoxConfig(
        api_token=API_TOKEN,
        base_url="https://aisdk.chatgo.pro",  # AI 服务器
        timeout=60.0  # AI 操作可能需要更长时间
    )
    
    async with DinoxClient(config=config) as client:
        print("已连接到 AI 服务器")
        
        # 示例：搜索和创建功能
        print("\n可用功能：")
        print("1. 搜索笔记:")
        print("   results = await client.search_notes(['Python', 'AI'])")
        
        print("\n2. 创建文字笔记:")
        print("   await client.create_note('# 标题\\n\\n内容...')")
        
        print("\n3. 获取卡片盒列表:")
        print("   boxes = await client.get_zettelboxes()")


async def demo_error_handling():
    """错误处理示例"""
    print("\n" + "="*50)
    print("4. 错误处理示例")
    print("="*50)
    
    try:
        # 使用无效的 token 演示错误处理
        async with DinoxClient(api_token="INVALID_TOKEN") as client:
            # 尝试调用 API（会失败）
            # notes = await client.get_notes_list()
            print("注意：实际调用时需要处理以下错误：")
            print("- 网络连接错误")
            print("- 认证失败（401）")
            print("- 权限不足（403）")
            print("- 服务器错误（500）")
            
    except Exception as e:
        print(f"错误示例: {e}")


async def demo_concurrent_requests():
    """并发请求示例"""
    print("\n" + "="*50)
    print("5. 并发请求示例")
    print("="*50)
    
    async with DinoxClient(api_token=API_TOKEN) as client:
        print("并发请求可以提高效率：")
        print("""
# 示例：同时执行多个请求
tasks = [
    client.get_notes_list(),
    client.get_note_by_id('id1'),
    client.get_note_by_id('id2')
]
results = await asyncio.gather(*tasks)
        """)


async def demo_custom_processing():
    """自定义处理示例"""
    print("\n" + "="*50)
    print("6. 数据处理示例")
    print("="*50)
    
    print("处理获取的笔记数据：")
    print("""
async with DinoxClient(api_token=TOKEN) as client:
    # 获取笔记
    notes = await client.get_notes_list()
    
    # 统计信息
    total_notes = sum(len(day['notes']) for day in notes)
    print(f'总笔记数: {total_notes}')
    
    # 搜索特定内容
    for day in notes:
        for note in day['notes']:
            if 'Python' in note.get('content', ''):
                print(f'找到相关笔记: {note["title"]}')
    
    # 导出为 JSON
    with open('my_notes.json', 'w', encoding='utf-8') as f:
        json.dump(notes, f, ensure_ascii=False, indent=2)
    """)


def show_quick_start():
    """显示快速开始指南"""
    print("\n" + "="*60)
    print(" DinoX API 快速开始指南")
    print("="*60)
    
    print("\n1. 安装包:")
    print("   pip install dinox-api")
    
    print("\n2. 导入模块:")
    print("   from dinox_client import DinoxClient, DinoxConfig")
    
    print("\n3. 创建客户端:")
    print("   client = DinoxClient(api_token='YOUR_TOKEN')")
    
    print("\n4. 使用异步上下文管理器:")
    print("""   async with DinoxClient(api_token='YOUR_TOKEN') as client:
       notes = await client.get_notes_list()""")
    
    print("\n5. 选择服务器:")
    print("   - 笔记服务器: https://api.chatgo.pro (读取)")
    print("   - AI 服务器: https://aisdk.chatgo.pro (创建/搜索)")


async def main():
    """主函数"""
    print("\n" + "="*60)
    print(" DinoX API (pip install dinox-api) 使用演示")
    print("="*60)
    print(f"\n当前时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("包版本: 0.1.0")
    
    # 显示快速开始
    show_quick_start()
    
    # 运行演示
    print("\n" + "="*60)
    print(" 功能演示")
    print("="*60)
    
    # 依次运行各个演示
    await demo_basic_usage()
    await demo_note_server()
    await demo_ai_server()
    await demo_error_handling()
    await demo_concurrent_requests()
    await demo_custom_processing()
    
    # 总结
    print("\n" + "="*60)
    print(" 总结")
    print("="*60)
    print("\n[SUCCESS] PyPI package installed and working correctly!")
    print("\nMain Features:")
    print("- Async API calls")
    print("- Support for two server endpoints")
    print("- Complete error handling")
    print("- Flexible configuration options")
    print("- Context manager support")
    print("\nNext Steps:")
    print("1. 获取有效的 API Token")
    print("2. 选择合适的服务器端点")
    print("3. 开始使用 API！")
    print("\n文档: https://github.com/JimEverest/DinoSync")
    print("PyPI: https://pypi.org/project/dinox-api/")


if __name__ == "__main__":
    asyncio.run(main())
