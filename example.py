"""
Dinox Client 使用示例

演示如何使用 Dinox Python 客户端的基本功能
"""

import asyncio
import os
import sys
import io
from pathlib import Path
from dotenv import load_dotenv
from dinox_client import DinoxClient, DinoxAPIError, DinoxConfig
from datetime import datetime

# 修复 Windows 编码问题
if sys.platform == 'win32':
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
    except (AttributeError, io.UnsupportedOperation):
        pass

# 加载 .env 文件
env_path = Path(__file__).parent / '.env'
if env_path.exists():
    load_dotenv(env_path)


async def example_basic_usage():
    """基础用法示例"""
    print("\n" + "="*60)
    print("示例 1: 基础用法")
    print("="*60)
    
    # 从环境变量获取 Token
    token = os.environ.get("DINOX_API_TOKEN")
    if not token:
        print("❌ 请设置 DINOX_API_TOKEN 环境变量")
        return
    
    # 使用上下文管理器（推荐）
    async with DinoxClient(api_token=token) as client:
        try:
            # 获取笔记列表
            notes = await client.get_notes_list()
            print(f"\n[OK] 获取到 {len(notes)} 天的笔记")
            
            # 显示前3天的笔记
            for day_note in notes[:3]:
                print(f"\n日期: {day_note['date']}")
                for note in day_note['notes'][:5]:  # 每天最多显示5条
                    title = note['title'] or '(无标题)'
                    print(f"  - {title[:50]}")
                    
        except DinoxAPIError as e:
            print(f"[ERROR] [{e.code}] {e.message}")


async def example_incremental_sync():
    """增量同步示例"""
    print("\n" + "="*60)
    print("示例 2: 增量同步")
    print("="*60)
    
    token = os.environ.get("DINOX_API_TOKEN")
    if not token:
        print("❌ 请设置 DINOX_API_TOKEN 环境变量")
        return
    
    async with DinoxClient(api_token=token) as client:
        try:
            # 只获取最近的笔记
            recent_time = "2025-10-18 00:00:00"
            notes = await client.get_notes_list(last_sync_time=recent_time)
            
            total_notes = sum(len(day['notes']) for day in notes)
            print(f"\n✓ 从 {recent_time} 开始同步")
            print(f"✓ 获取到 {total_notes} 条更新的笔记")
            
        except DinoxAPIError as e:
            print(f"[ERROR] [{e.code}] {e.message}")


async def example_search():
    """搜索笔记示例"""
    print("\n" + "="*60)
    print("示例 3: 搜索笔记")
    print("="*60)
    
    token = os.environ.get("DINOX_API_TOKEN")
    if not token:
        print("❌ 请设置 DINOX_API_TOKEN 环境变量")
        return
    
    # v0.2.0+ 自动路由到AI服务器
    async with DinoxClient(api_token=token) as client:
        try:
            keywords = ["测试", "test"]
            result = await client.search_notes(keywords=keywords)
            
            print(f"\n✓ 搜索关键词: {', '.join(keywords)}")
            if 'content' in result:
                print(f"✓ 找到内容长度: {len(result['content'])} 字符")
            print(f"✓ 自动路由到: AI服务器")
            
        except DinoxAPIError as e:
            print(f"[ERROR] [{e.code}] {e.message}")


async def example_create_note():
    """创建笔记示例"""
    print("\n" + "="*60)
    print("示例 4: 创建笔记")
    print("="*60)
    
    token = os.environ.get("DINOX_API_TOKEN")
    if not token:
        print("❌ 请设置 DINOX_API_TOKEN 环境变量")
        return
    
    # v0.2.0+ 自动路由到AI服务器
    async with DinoxClient(api_token=token) as client:
        try:
            content = f"""# Python 客户端测试

创建时间: {datetime.now().isoformat()}

这是一条通过 Dinox Python 客户端创建的测试笔记。

## 功能

- ✅ 异步支持
- ✅ 自动服务器路由
- ✅ 类型提示
- ✅ 错误处理
"""
            
            result = await client.create_note(
                content=content,
                note_type="note"
            )
            
            print("\n✓ 笔记创建成功!")
            print(f"  内容: {content.split(chr(10))[0]}")
            print(f"✓ 自动路由到: AI服务器")
            
        except DinoxAPIError as e:
            print(f"⚠ {e.message}")


async def example_get_zettelboxes():
    """获取卡片盒示例"""
    print("\n" + "="*60)
    print("示例 5: 获取卡片盒")
    print("="*60)
    
    token = os.environ.get("DINOX_API_TOKEN")
    if not token:
        print("❌ 请设置 DINOX_API_TOKEN 环境变量")
        return
    
    # v0.2.0+ 自动路由到AI服务器
    async with DinoxClient(api_token=token) as client:
        try:
            boxes = await client.get_zettelboxes()
            
            print(f"\n✓ 获取到 {len(boxes)} 个卡片盒")
            print(f"✓ 自动路由到: AI服务器")
            for i, box in enumerate(boxes[:5], 1):
                name = box.get('name', '(未命名)')
                print(f"  {i}. 📦 {name}")
                
        except DinoxAPIError as e:
            print(f"[ERROR] [{e.code}] {e.message}")


async def example_auto_routing():
    """自动路由示例 - v0.2.0新特性"""
    print("\n" + "="*60)
    print("示例 6: 自动服务器路由（v0.2.0+）")
    print("="*60)
    
    token = os.environ.get("DINOX_API_TOKEN")
    if not token:
        print("❌ 请设置 DINOX_API_TOKEN 环境变量")
        return
    
    # 一个客户端，自动路由到不同服务器
    async with DinoxClient(api_token=token) as client:
        print("\n使用同一个客户端实例:\n")
        
        # 自动路由到笔记服务器
        try:
            notes = await client.get_notes_list()
            print(f"  ✓ get_notes_list() → 自动路由到笔记服务器")
            print(f"    结果: {len(notes)} 天的笔记")
        except DinoxAPIError as e:
            print(f"  ✗ 错误: {e.message}")
        
        # 自动路由到AI服务器
        try:
            result = await client.search_notes(["测试"])
            print(f"  ✓ search_notes() → 自动路由到AI服务器")
            if 'content' in result:
                print(f"    结果: 找到内容")
        except DinoxAPIError as e:
            print(f"  ✗ 错误: {e.message}")
        
        print(f"\n💡 无需手动切换服务器，完全自动！")


async def example_concurrent_requests():
    """并发请求示例"""
    print("\n" + "="*60)
    print("示例 7: 并发请求")
    print("="*60)
    
    token = os.environ.get("DINOX_API_TOKEN")
    if not token:
        print("❌ 请设置 DINOX_API_TOKEN 环境变量")
        return
    
    import time
    
    async with DinoxClient(api_token=token) as client:
        try:
            # 创建5个并发请求
            print("\n正在发送 5 个并发请求...")
            start_time = time.time()
            
            tasks = [client.get_notes_list() for _ in range(5)]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            end_time = time.time()
            elapsed = end_time - start_time
            
            # 统计结果
            successful = sum(1 for r in results if isinstance(r, list))
            
            print(f"\n✓ 并发请求完成")
            print(f"  成功: {successful}/5")
            print(f"  总耗时: {elapsed:.2f} 秒")
            print(f"  平均耗时: {elapsed/5:.2f} 秒/请求")
            
        except DinoxAPIError as e:
            print(f"[ERROR] [{e.code}] {e.message}")


async def main():
    """运行所有示例"""
    print("\n" + "="*60)
    print("Dinox Python Client 示例集合")
    print("="*60)
    
    # 检查环境变量
    if not os.environ.get("DINOX_API_TOKEN"):
        print("\n⚠️  请先设置 DINOX_API_TOKEN 环境变量")
        print("\n设置方法:")
        print("  Linux/Mac:  export DINOX_API_TOKEN='your_token'")
        print("  Windows PS: $env:DINOX_API_TOKEN='your_token'")
        return
    
    try:
        # 运行所有示例
        await example_basic_usage()
        await example_incremental_sync()
        await example_search()
        await example_create_note()
        await example_get_zettelboxes()
        await example_auto_routing()
        await example_concurrent_requests()
        
        print("\n" + "="*60)
        print("✅ 所有示例运行完成!")
        print("="*60)
        
    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断")
    except Exception as e:
        print(f"\n\n❌ 发生错误: {e}")


if __name__ == "__main__":
    asyncio.run(main())

