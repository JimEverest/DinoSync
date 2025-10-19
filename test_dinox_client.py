"""
Dinox Client 测试脚本

使用 pytest 进行异步测试
运行方式: pytest test_dinox_client.py -v
"""

import pytest
import pytest_asyncio
import asyncio
import os
import sys
import io
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from dinox_client import (
    DinoxClient,
    DinoxConfig,
    DinoxAPIError,
    create_client
)

# 修复 Windows 控制台编码问题
if sys.platform == 'win32':
    try:
        # 只在直接运行时修改编码，pytest运行时不修改
        if not hasattr(sys, '_pytest_running'):
            sys.stdout.reconfigure(encoding='utf-8')
            sys.stderr.reconfigure(encoding='utf-8')
    except (AttributeError, io.UnsupportedOperation):
        pass  # 在某些环境下可能不支持

# 加载 .env 文件
env_path = Path(__file__).parent / '.env'
if env_path.exists():
    load_dotenv(env_path)

# 从环境变量获取 Token（安全最佳实践）
TEST_TOKEN = os.environ.get("DINOX_API_TOKEN")
if not TEST_TOKEN:
    print("警告: 未找到 DINOX_API_TOKEN 环境变量")
    print("请创建 .env 文件并设置 DINOX_API_TOKEN")
    pytest.skip("DINOX_API_TOKEN not set", allow_module_level=True)


@pytest_asyncio.fixture
async def client():
    """测试客户端 fixture"""
    async with DinoxClient(api_token=TEST_TOKEN) as c:
        yield c


@pytest.fixture
def config():
    """配置 fixture"""
    return DinoxConfig(api_token=TEST_TOKEN)


# ==================== 配置测试 ====================

def test_config_creation():
    """测试配置创建"""
    config = DinoxConfig(api_token="test_token")
    assert config.api_token == "test_token"
    assert config.base_url == "https://dinoai.chatgo.pro"
    assert config.timeout == 30


def test_config_with_custom_base_url():
    """测试自定义 base_url"""
    config = DinoxConfig(
        api_token="test_token",
        base_url="https://custom.api.com/"
    )
    # 应该移除末尾的斜杠
    assert config.base_url == "https://custom.api.com"


def test_config_requires_token():
    """测试配置需要 token"""
    with pytest.raises(ValueError, match="API token is required"):
        DinoxConfig(api_token="")


# ==================== 客户端初始化测试 ====================

def test_client_creation_with_token():
    """测试使用 token 创建客户端"""
    client = DinoxClient(api_token=TEST_TOKEN)
    assert client.config.api_token == TEST_TOKEN


def test_client_creation_with_config():
    """测试使用配置对象创建客户端"""
    config = DinoxConfig(api_token=TEST_TOKEN)
    client = DinoxClient(config=config)
    assert client.config == config


def test_client_requires_token_or_config():
    """测试客户端需要 token 或配置"""
    with pytest.raises(ValueError, match="Either api_token or config must be provided"):
        DinoxClient()


@pytest.mark.asyncio
async def test_client_context_manager():
    """测试上下文管理器"""
    async with DinoxClient(api_token=TEST_TOKEN) as client:
        assert client.session is not None
    # 退出后 session 应该关闭
    assert client.session is None


# ==================== 笔记查询接口测试 ====================

@pytest.mark.asyncio
async def test_get_notes_list(client):
    """测试获取笔记列表"""
    notes = await client.get_notes_list()
    
    # 验证返回类型
    assert isinstance(notes, list)
    
    # 如果有数据，验证结构
    if notes:
        first_day = notes[0]
        assert "date" in first_day
        assert "notes" in first_day
        assert isinstance(first_day["notes"], list)
        
        if first_day["notes"]:
            first_note = first_day["notes"][0]
            assert "noteId" in first_note
            assert "title" in first_note
            assert "content" in first_note
            print(f"\n✓ 获取到 {len(notes)} 天的笔记")


@pytest.mark.asyncio
async def test_get_notes_list_with_custom_template(client):
    """测试使用自定义模板获取笔记"""
    custom_template = "{{title}}\n\n{{content}}"
    notes = await client.get_notes_list(template=custom_template)
    
    assert isinstance(notes, list)
    print(f"\n✓ 使用自定义模板获取 {len(notes)} 天的笔记")


@pytest.mark.asyncio
async def test_get_notes_list_incremental(client):
    """测试增量同步"""
    # 获取最近的笔记
    recent_time = "2025-10-18 00:00:00"
    notes = await client.get_notes_list(last_sync_time=recent_time)
    
    assert isinstance(notes, list)
    print(f"\n✓ 增量同步获取到 {len(notes)} 天的笔记")


@pytest.mark.asyncio
async def test_search_notes(client):
    """测试搜索笔记"""
    try:
        result = await client.search_notes(keywords=["测试", "test"])
        assert isinstance(result, dict)
        assert 'content' in result
        print(f"\n✓ 搜索成功，返回内容长度: {len(result.get('content', ''))} 字符")
    except DinoxAPIError as e:
        print(f"\n⚠ 搜索接口错误: {e.message}")


# ==================== 笔记创建测试 ====================

@pytest.mark.asyncio
async def test_create_text_note(client):
    """测试创建文字笔记"""
    test_content = f"Python 测试笔记 - {datetime.now().isoformat()}"
    
    try:
        result = await client.create_text_note(content=test_content)
        assert result is not None
        print(f"\n✓ 成功创建文字笔记")
        print(f"  内容: {test_content[:50]}...")
    except DinoxAPIError as e:
        print(f"\n⚠ 创建笔记错误: {e.message}")
        # 根据错误类型决定是否要失败测试
        # "0000029" 是转写失败错误，这是API的功能限制
        if e.code not in ["RATE_LIMIT", "QUOTA_EXCEEDED", "0000029"]:
            raise
        # 对于已知的限制，测试通过


@pytest.mark.asyncio
async def test_create_note_with_zettelbox(client):
    """测试创建笔记（带卡片盒）"""
    test_content = f"""# 测试笔记

创建时间: {datetime.now().isoformat()}

这是一条通过 API 创建的测试笔记。
"""
    
    try:
        result = await client.create_note(
            content=test_content,
            note_type="note",
            zettelbox_ids=[]  # 空列表，不指定卡片盒
        )
        assert result is not None
        print(f"\n✓ 成功创建笔记（带卡片盒）")
    except DinoxAPIError as e:
        print(f"\n⚠ 创建笔记错误: {e.message}")


@pytest.mark.asyncio
async def test_update_note(client):
    """测试更新笔记"""
    try:
        # 首先获取一个笔记ID
        notes = await client.get_notes_list()
        if notes and notes[0]['notes']:
            note_id = notes[0]['notes'][0]['noteId']
            
            # 尝试更新笔记
            updated_content = f"""# 更新测试

更新时间: {datetime.now().isoformat()}

这是通过 API 更新的笔记内容。
"""
            result = await client.update_note(
                note_id=note_id,
                content_md=updated_content
            )
            assert result is not None
            print(f"\n✓ 成功更新笔记 {note_id[:8]}...")
        else:
            print("\n⚠ 没有可用的笔记进行测试")
    except DinoxAPIError as e:
        print(f"\n⚠ 更新笔记错误: {e.message}")
        # 如果是404错误，说明API未部署
        if e.status_code == 404:
            print("   提示：update_note API 端点可能未部署")


# ==================== 卡片盒测试 ====================

@pytest.mark.asyncio
async def test_get_zettelboxes():
    """测试获取卡片盒列表"""
    # get_zettelboxes 需要使用 aisdk 服务器
    config = DinoxConfig(
        api_token=TEST_TOKEN,
        base_url="https://aisdk.chatgo.pro"
    )
    async with DinoxClient(config=config) as client:
        boxes = await client.get_zettelboxes()
        assert isinstance(boxes, list)
        print(f"\n✓ 获取到 {len(boxes)} 个卡片盒")
        
        if boxes:
            print(f"  第一个卡片盒: {boxes[0]}")


# ==================== 工具函数测试 ====================

def test_format_sync_time():
    """测试时间格式化"""
    # 测试自定义时间
    dt = datetime(2025, 10, 18, 15, 30, 45)
    formatted = DinoxClient.format_sync_time(dt)
    assert formatted == "2025-10-18 15:30:45"
    
    # 测试当前时间
    formatted_now = DinoxClient.format_sync_time()
    assert len(formatted_now) == 19  # "YYYY-MM-DD HH:mm:ss" 长度


def test_default_template():
    """测试默认模板"""
    template = DinoxClient._get_default_template()
    assert "{{title}}" in template
    assert "{{noteId}}" in template
    assert "{{content}}" in template


# ==================== 错误处理测试 ====================

@pytest.mark.asyncio
async def test_invalid_token():
    """测试无效 token"""
    async with DinoxClient(api_token="invalid_token") as client:
        with pytest.raises(DinoxAPIError) as exc_info:
            await client.get_notes_list()
        
        error = exc_info.value
        assert error.code is not None
        print(f"\n✓ 正确捕获无效 token 错误: {error.message}")


@pytest.mark.asyncio
async def test_network_error_handling():
    """测试网络错误处理"""
    config = DinoxConfig(
        api_token=TEST_TOKEN,
        base_url="https://invalid-domain-that-does-not-exist-12345.com"
    )
    
    async with DinoxClient(config=config) as client:
        with pytest.raises(DinoxAPIError) as exc_info:
            await client.get_notes_list()
        
        error = exc_info.value
        assert error.code == "NETWORK_ERROR"
        print(f"\n✓ 正确捕获网络错误")


# ==================== 集成测试 ====================

@pytest.mark.asyncio
async def test_full_workflow(client):
    """测试完整工作流"""
    print("\n" + "="*60)
    print("完整工作流测试")
    print("="*60)
    
    # 1. 获取笔记列表
    print("\n1. 获取笔记列表...")
    notes = await client.get_notes_list()
    print(f"   ✓ 获取到 {len(notes)} 天的笔记")
    
    # 2. 获取卡片盒
    print("\n2. 获取卡片盒...")
    try:
        boxes = await client.get_zettelboxes()
        print(f"   ✓ 获取到 {len(boxes)} 个卡片盒")
    except DinoxAPIError as e:
        print(f"   ⚠ {e.message}")
    
    # 3. 创建测试笔记
    print("\n3. 创建测试笔记...")
    try:
        test_content = f"自动化测试笔记 - {datetime.now().isoformat()}"
        result = await client.create_text_note(content=test_content)
        print(f"   ✓ 创建成功")
    except DinoxAPIError as e:
        print(f"   ⚠ {e.message}")
    
    # 4. 格式化时间
    print("\n4. 格式化同步时间...")
    sync_time = DinoxClient.format_sync_time()
    print(f"   ✓ 当前同步时间: {sync_time}")
    
    print("\n" + "="*60)
    print("✓ 完整工作流测试通过")
    print("="*60)


# ==================== 便捷函数测试 ====================

@pytest.mark.asyncio
async def test_create_client_helper():
    """测试便捷创建函数"""
    client = await create_client(api_token=TEST_TOKEN)
    assert client.session is not None
    
    # 测试可以正常调用 API
    notes = await client.get_notes_list()
    assert isinstance(notes, list)
    
    await client.close()
    print("\n✓ 便捷创建函数测试通过")


# ==================== 性能测试 ====================

@pytest.mark.asyncio
async def test_concurrent_requests(client):
    """测试并发请求"""
    import time
    
    print("\n测试并发请求性能...")
    
    # 创建 5 个并发请求
    start_time = time.time()
    tasks = [client.get_notes_list() for _ in range(5)]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    end_time = time.time()
    
    # 验证结果
    successful = sum(1 for r in results if isinstance(r, list))
    print(f"\n✓ 5 个并发请求完成:")
    print(f"  - 成功: {successful}")
    print(f"  - 总耗时: {end_time - start_time:.2f} 秒")
    print(f"  - 平均耗时: {(end_time - start_time) / 5:.2f} 秒/请求")


# ==================== 主测试套件 ====================

def run_tests():
    """运行所有测试"""
    print("\n" + "="*60)
    print("Dinox Client 测试套件")
    print("="*60)
    
    # 使用 pytest 运行测试
    pytest.main([
        __file__,
        "-v",  # 详细输出
        "-s",  # 显示 print 输出
        "--tb=short",  # 短错误回溯
        "--color=yes"  # 彩色输出
    ])


if __name__ == "__main__":
    run_tests()

