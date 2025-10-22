# -*- coding: utf-8 -*-
"""
Dinox API 异步客户端

一个用于与 Dinox AI 笔记服务交互的异步 Python 客户端库。

Author: Dinox Team
License: MIT
Version: 0.2.0
"""

__version__ = "0.2.0"

import aiohttp
import asyncio
from typing import List, Dict, Any, Optional, Union
from dataclasses import dataclass
from datetime import datetime
import json
import sys
import io

# Fix Windows encoding issues
if sys.platform == 'win32':
    try:
        if hasattr(sys.stdout, 'reconfigure'):
            sys.stdout.reconfigure(encoding='utf-8')
            sys.stderr.reconfigure(encoding='utf-8')
    except (AttributeError, io.UnsupportedOperation):
        pass


# Server URLs
NOTE_SERVER_URL = "https://dinoai.chatgo.pro"
AI_SERVER_URL = "https://aisdk.chatgo.pro"

# Method-to-server mapping for automatic routing
METHOD_SERVER_MAP = {
    # Note Server methods
    "get_notes_list": NOTE_SERVER_URL,
    "get_note_by_id": NOTE_SERVER_URL,
    "update_note": NOTE_SERVER_URL,
    
    # AI Server methods
    "search_notes": AI_SERVER_URL,
    "create_note": AI_SERVER_URL,
    "create_text_note": AI_SERVER_URL,
    "get_zettelboxes": AI_SERVER_URL,
}

@dataclass
class DinoxConfig:
    """
    Dinox 客户端配置
    
    注意：Dinox 有两个 API 服务器：
    - https://dinoai.chatgo.pro - 笔记查询API（get_notes_list, get_note_by_id等）
    - https://aisdk.chatgo.pro - 搜索和创建API（search_notes, create_note等）
    
    默认使用 dinoai，如需使用搜索功能请切换到 aisdk
    自动路由：设置 auto_route=True 可自动选择合适的服务器（v0.2.0+新功能）
    """
    api_token: str
    base_url: str = "https://dinoai.chatgo.pro"
    timeout: int = 30
    auto_route: bool = True  # 新增：自动路由功能
    
    def __post_init__(self):
        """验证配置"""
        if not self.api_token:
            raise ValueError("API token is required")
        # 移除 base_url 末尾的斜杠
        self.base_url = self.base_url.rstrip('/')


class DinoxAPIError(Exception):
    """Dinox API 错误基类"""
    def __init__(self, code: str, message: str, status_code: int = None):
        self.code = code
        self.message = message
        self.status_code = status_code
        super().__init__(f"[{code}] {message}")


class DinoxClient:
    """
    Dinox API 异步客户端
    
    示例用法:
        async with DinoxClient(api_token="your_token") as client:
            notes = await client.get_notes_list()
            print(f"获取到 {len(notes)} 天的笔记")
    """
    
    def __init__(self, api_token: str = None, config: DinoxConfig = None, auto_route: bool = True):
        """
        初始化 Dinox 客户端
        
        Args:
            api_token: API Token (JWT格式)
            config: DinoxConfig 配置对象，如果提供则忽略 api_token
            auto_route: 是否启用自动服务器路由 (v0.2.0+)
        """
        if config:
            self.config = config
        elif api_token:
            self.config = DinoxConfig(api_token=api_token, auto_route=auto_route)
        else:
            raise ValueError("Either api_token or config must be provided")
        
        self.session: Optional[aiohttp.ClientSession] = None
        self.note_session: Optional[aiohttp.ClientSession] = None  # Note server session
        self.ai_session: Optional[aiohttp.ClientSession] = None    # AI server session
        self._current_method: Optional[str] = None  # Track current method for auto-routing
    
    async def __aenter__(self):
        """异步上下文管理器入口"""
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器退出"""
        await self.close()
    
    async def connect(self):
        """创建 HTTP 会话"""
        timeout = aiohttp.ClientTimeout(total=self.config.timeout)
        
        if self.config.auto_route:
            # Create separate sessions for each server when auto-routing
            if self.note_session is None:
                self.note_session = aiohttp.ClientSession(timeout=timeout)
            if self.ai_session is None:
                self.ai_session = aiohttp.ClientSession(timeout=timeout)
        else:
            # Create single session for manual routing
            if self.session is None:
                self.session = aiohttp.ClientSession(timeout=timeout)
    
    async def close(self):
        """关闭 HTTP 会话"""
        if self.session:
            await self.session.close()
            self.session = None
        if self.note_session:
            await self.note_session.close()
            self.note_session = None
        if self.ai_session:
            await self.ai_session.close()
            self.ai_session = None
    
    def _get_headers(self, extra_headers: Dict[str, str] = None) -> Dict[str, str]:
        """
        获取请求头
        
        Args:
            extra_headers: 额外的请求头
            
        Returns:
            完整的请求头字典
        """
        headers = {
            "Authorization": self.config.api_token,
            "Content-Type": "application/json"
        }
        if extra_headers:
            headers.update(extra_headers)
        return headers
    
    async def _request(
        self,
        method: str,
        endpoint: str,
        data: Dict[str, Any] = None,
        params: Dict[str, Any] = None,
        extra_headers: Dict[str, str] = None
    ) -> Dict[str, Any]:
        """
        发送 HTTP 请求 (支持自动服务器路由 v0.2.0+)
        
        Args:
            method: HTTP 方法 (GET, POST, PUT, DELETE)
            endpoint: API 端点路径
            data: 请求体数据
            params: URL 参数
            extra_headers: 额外的请求头
            
        Returns:
            响应 JSON 数据
            
        Raises:
            DinoxAPIError: API 错误
        """
        # Determine which server and session to use
        if self.config.auto_route and self._current_method:
            # Use automatic routing based on the method
            if self._current_method in METHOD_SERVER_MAP:
                server_url = METHOD_SERVER_MAP[self._current_method]
                if server_url == NOTE_SERVER_URL:
                    if not self.note_session:
                        await self.connect()
                    session = self.note_session
                else:  # AI_SERVER_URL
                    if not self.ai_session:
                        await self.connect()
                    session = self.ai_session
            else:
                # Default to note server for unknown methods
                server_url = self.config.base_url
                if not self.note_session:
                    await self.connect()
                session = self.note_session
        else:
            # Use manual routing with configured base_url
            server_url = self.config.base_url
            if not self.session:
                await self.connect()
            session = self.session or self.note_session or self.ai_session
        
        url = f"{server_url}{endpoint}"
        headers = self._get_headers(extra_headers)
        
        try:
            async with session.request(
                method=method,
                url=url,
                json=data,
                params=params,
                headers=headers
            ) as response:
                response_text = await response.text()
                
                # 检查 HTTP 状态码
                if response.status >= 400:
                    try:
                        error_data = json.loads(response_text)
                        error_msg = error_data.get('msg', response_text)
                        error_code = error_data.get('code', str(response.status))
                    except json.JSONDecodeError:
                        error_msg = response_text
                        error_code = str(response.status)
                    
                    raise DinoxAPIError(
                        code=error_code,
                        message=error_msg,
                        status_code=response.status
                    )
                
                # 解析响应
                try:
                    result = json.loads(response_text)
                except json.JSONDecodeError:
                    raise DinoxAPIError(
                        code="INVALID_JSON",
                        message=f"Invalid JSON response: {response_text[:100]}",
                        status_code=response.status
                    )
                
                # 检查业务错误码
                if isinstance(result, dict):
                    code = result.get('code')
                    if code and code != "000000":
                        raise DinoxAPIError(
                            code=code,
                            message=result.get('msg', 'Unknown error'),
                            status_code=response.status
                        )
                
                return result
        
        except aiohttp.ClientError as e:
            raise DinoxAPIError(
                code="NETWORK_ERROR",
                message=f"Network error: {str(e)}"
            )
    
    # ==================== 笔记查询接口 ====================
    
    async def get_notes_list(
        self,
        last_sync_time: str = "1900-01-01 00:00:00",
        template: str = None
    ) -> List[Dict[str, Any]]:
        """
        获取笔记列表（支持增量同步）
        
        Args:
            last_sync_time: 上次同步时间，格式 YYYY-MM-DD HH:mm:ss
            template: Mustache 模板字符串，如果不提供则使用默认模板
            
        Returns:
            按日期分组的笔记列表
            
        Example:
            >>> notes = await client.get_notes_list()
            >>> for day_note in notes:
            ...     print(f"日期: {day_note['date']}")
            ...     print(f"笔记数: {len(day_note['notes'])}")
        """
        self._current_method = "get_notes_list"  # Set method for auto-routing
        if template is None:
            template = self._get_default_template()
        
        data = {
            "noteId": 0,
            "lastSyncTime": last_sync_time,
            "template": template
        }
        
        result = await self._request("POST", "/openapi/v5/notes", data=data)
        return result.get('data', [])
    
    async def get_note_by_id(self, note_id: str) -> Dict[str, Any]:
        """
        根据 ID 查询笔记
        
        Args:
            note_id: 笔记 ID
            
        Returns:
            笔记详情
            
        Example:
            >>> note = await client.get_note_by_id("0199eb0d-fccc-7dc8-82da-7d32be3e668b")
            >>> print(note['title'])
        """
        self._current_method = "get_note_by_id"  # Set method for auto-routing
        result = await self._request("GET", f"/api/openapi/note/{note_id}")
        return result
    
    async def search_notes(self, keywords: List[str]) -> Dict[str, Any]:
        """
        根据关键词查询笔记
        
        Args:
            keywords: 关键词列表
            
        Returns:
            包含搜索结果的字典，包含 'content' 字段
            
        Example:
            >>> result = await client.search_notes(["Python", "异步"])
            >>> print(result['content'])
        """
        self._current_method = "search_notes"  # Set method for auto-routing
        data = {"keywords": keywords}
        result = await self._request("POST", "/api/openapi/searchNotes", data=data)
        return result.get('data', {})
    
    # ==================== 笔记创建/更新接口 ====================
    
    async def create_text_note(self, content: str) -> Dict[str, Any]:
        """
        创建文字笔记
        
        ⚠️ 注意：此接口当前有功能限制，可能返回"转写失败"错误
        
        Args:
            content: 笔记内容
            
        Returns:
            创建结果
            
        Raises:
            DinoxAPIError: 可能返回错误码 0000029 "转写失败"
            
        Example:
            >>> result = await client.create_text_note("这是一条测试笔记")
            >>> print(result)
        """
        self._current_method = "create_text_note"  # Set method for auto-routing
        data = {"content": content}
        result = await self._request("POST", "/openapi/text/input", data=data)
        return result
    
    async def create_note(
        self,
        content: str,
        note_type: str = "note",
        zettelbox_ids: List[str] = None
    ) -> Dict[str, Any]:
        """
        创建笔记（支持卡片盒）
        
        Args:
            content: 笔记内容（Markdown 格式）
            note_type: 笔记类型 ("note" 或 "crawl")
            zettelbox_ids: 卡片盒 ID 列表
            
        Returns:
            创建结果
            
        Example:
            >>> result = await client.create_note(
            ...     content="# 测试笔记\\n\\n这是内容",
            ...     zettelbox_ids=["box-id-1"]
            ... )
        """
        self._current_method = "create_note"  # Set method for auto-routing
        data = {
            "type": note_type,
            "content": content,
            "zettelboxIds": zettelbox_ids or []
        }
        result = await self._request("POST", "/api/openapi/createNote", data=data)
        return result
    
    async def update_note(self, note_id: str, content_md: str) -> Dict[str, Any]:
        """
        更新笔记
        
        Args:
            note_id: 笔记 ID
            content_md: 笔记内容（Markdown 格式）
            
        Returns:
            更新结果
            
        Example:
            >>> result = await client.update_note(
            ...     note_id="0199eb0d-fccc-7dc8-82da-7d32be3e668b",
            ...     content_md="更新后的内容"
            ... )
        """
        self._current_method = "update_note"  # Set method for auto-routing
        data = {
            "noteId": note_id,
            "contentMd": content_md
        }
        result = await self._request("POST", "/openapi/updateNote", data=data)
        return result
    
    # ==================== 卡片盒接口 ====================
    
    async def get_zettelboxes(self) -> List[Dict[str, Any]]:
        """
        获取卡片盒列表
        
        Returns:
            卡片盒列表
            
        Example:
            >>> boxes = await client.get_zettelboxes()
            >>> for box in boxes:
            ...     print(box['name'])
        """
        self._current_method = "get_zettelboxes"  # Set method for auto-routing
        result = await self._request("GET", "/api/openapi/zettelboxes")
        return result.get('data', [])
    
    # ==================== 辅助方法 ====================
    
    @staticmethod
    def _get_default_template() -> str:
        """获取默认的笔记模板"""
        return """---
title: {{title}}
noteId: {{noteId}}
type: {{type}}
tags:
{{#tags}}
    - {{.}}
{{/tags}}
zettelBoxes:
{{#zettelBoxes}}
    - {{.}}
{{/zettelBoxes}}
audioUrl: {{audioUrl}}
createTime: {{createTime}}
updateTime: {{updateTime}}
---
{{#audioUrl}}
![录音]({{audioUrl}})
{{/audioUrl}}

{{content}}
"""
    
    @staticmethod
    def format_sync_time(dt: datetime = None) -> str:
        """
        格式化同步时间
        
        Args:
            dt: datetime 对象，如果为 None 则使用当前时间
            
        Returns:
            格式化的时间字符串 "YYYY-MM-DD HH:mm:ss"
        """
        if dt is None:
            dt = datetime.now()
        return dt.strftime("%Y-%m-%d %H:%M:%S")


# ==================== 便捷函数 ====================

async def create_client(api_token: str, **kwargs) -> DinoxClient:
    """
    创建并连接 Dinox 客户端
    
    Args:
        api_token: API Token
        **kwargs: 其他配置参数
        
    Returns:
        已连接的 DinoxClient 实例
    """
    config = DinoxConfig(api_token=api_token, **kwargs)
    client = DinoxClient(config=config)
    await client.connect()
    return client


# ==================== 示例代码 ====================

async def example_usage():
    """示例代码"""
    # 方式 1: 使用上下文管理器（推荐）
    async with DinoxClient(api_token="YOUR_TOKEN_HERE") as client:
        # 获取笔记列表
        notes = await client.get_notes_list()
        print(f"获取到 {len(notes)} 天的笔记")
        
        # 创建文字笔记
        result = await client.create_text_note("测试笔记内容")
        print(f"创建结果: {result}")
    
    # 方式 2: 手动管理连接
    client = DinoxClient(api_token="YOUR_TOKEN_HERE")
    try:
        await client.connect()
        boxes = await client.get_zettelboxes()
        print(f"卡片盒数量: {len(boxes)}")
    finally:
        await client.close()


if __name__ == "__main__":
    # 运行示例
    asyncio.run(example_usage())

