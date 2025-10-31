"""Tests for the MCP server."""
import pytest
import asyncio
from src.mcp_server.server import (
    handle_list_tools,
    handle_call_tool,
    handle_list_resources,
    handle_read_resource,
)


class TestMCPTools:
    """Test MCP tools functionality."""
    
    @pytest.mark.asyncio
    async def test_list_tools(self):
        """Test that tools are listed correctly."""
        tools = await handle_list_tools()
        
        # Check that we have the expected tools
        tool_names = [tool.name for tool in tools]
        assert "echo" in tool_names
        assert "calculate" in tool_names
        assert "get_time" in tool_names
        
        # Check tool descriptions
        for tool in tools:
            assert tool.description is not None
            assert tool.inputSchema is not None
    
    @pytest.mark.asyncio
    async def test_echo_tool(self):
        """Test the echo tool."""
        result = await handle_call_tool("echo", {"text": "Hello, World!"})
        assert len(result) == 1
        assert result[0].type == "text"
        assert result[0].text == "Hello, World!"
    
    @pytest.mark.asyncio
    async def test_echo_tool_missing_argument(self):
        """Test echo tool with missing argument."""
        with pytest.raises(ValueError, match="Missing 'text' argument"):
            await handle_call_tool("echo", {})
    
    @pytest.mark.asyncio
    async def test_calculate_tool(self):
        """Test the calculate tool."""
        result = await handle_call_tool("calculate", {"expression": "2 + 3"})
        assert len(result) == 1
        assert result[0].type == "text"
        assert "Result: 5" in result[0].text
    
    @pytest.mark.asyncio
    async def test_calculate_tool_error(self):
        """Test calculate tool with invalid expression."""
        result = await handle_call_tool("calculate", {"expression": "2 + "})
        assert len(result) == 1
        assert result[0].type == "text"
        assert "Error:" in result[0].text
    
    @pytest.mark.asyncio
    async def test_get_time_tool(self):
        """Test the get_time tool."""
        result = await handle_call_tool("get_time", {})
        assert len(result) == 1
        assert result[0].type == "text"
        assert "Current time:" in result[0].text
    
    @pytest.mark.asyncio
    async def test_unknown_tool(self):
        """Test calling an unknown tool."""
        with pytest.raises(ValueError, match="Unknown tool"):
            await handle_call_tool("unknown_tool", {})


class TestMCPResources:
    """Test MCP resources functionality."""
    
    @pytest.mark.asyncio
    async def test_list_resources(self):
        """Test that resources are listed correctly."""
        resources = await handle_list_resources()
        
        # Check that we have the expected resource
        resource_uris = [resource.uri for resource in resources]
        assert "example://info" in resource_uris
        
        # Check resource properties
        for resource in resources:
            assert resource.name is not None
            assert resource.description is not None
            assert resource.mimeType is not None
    
    @pytest.mark.asyncio
    async def test_read_resource(self):
        """Test reading a resource."""
        content = await handle_read_resource("example://info")
        assert content == "This is an example resource from the Python MCP server."
    
    @pytest.mark.asyncio
    async def test_read_unknown_resource(self):
        """Test reading an unknown resource."""
        with pytest.raises(ValueError, match="Unknown resource"):
            await handle_read_resource("unknown://resource")
