#!/usr/bin/env python3
"""
Test CAI Workbench MCP Server using FastMCP Client
Simple, clean approach - testing representative tools from each category

Note: These tests use mock project IDs. For real testing with actual Cloudera AI:
- Set environment variables: CAI_WORKBENCH_HOST, CAI_WORKBENCH_API_KEY, CAI_WORKBENCH_PROJECT_ID
- Use real project IDs in format: xxxx-xxxx-xxxx-xxxx (e.g., "9er0-ooi9-uopm-8i8o")
"""

from fastmcp.client.transports import FastMCPTransport


import asyncio
import json
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastmcp import Client
from fastmcp.client.transports import FastMCPTransport
from cai_workbench_mcp_server.stdio_server import mcp


def parse_tool_result(result):
    """Helper to parse tool results consistently"""
    if hasattr(result, 'content') and result.content:
        content = result.content[0].text
        # Handle both JSON strings and dict returns
        if isinstance(content, str):
            return json.loads(content)
        else:
            return content
    return None


async def test_server_basics():
    """Test basic server connectivity and tool discovery"""
    print("\n🔍 Testing Server Basics")
    print("=" * 50)
    
    client = Client(mcp)
    
    async with client:
        # Test connectivity
        await client.ping()
        print("✅ Server connected")
        
        # Get tools count
        tools = await client.list_tools()
        print(f"✅ Found {len(tools)} tools")
        
        # Verify we have the expected number
        assert len(tools) == 164, f"Expected 164 tools, found {len(tools)}"
        print("✅ Tool count verified")


async def test_system_tools():
    """Test system information tools (work without credentials)"""
    print("\n🔍 Testing System Tools")
    print("=" * 50)

    client = Client(mcp)

    async with client:
        # Test list_runtimes_tool - should work without credentials
        print("\n📌 list_runtimes_tool:")
        try:
            result = await client.call_tool("list_runtimes_tool", {})
            # FastMCP returns the result as a list of content items
            if hasattr(result, 'content') and result.content:
                # result.content is a list of items
                content = result.content[0].text
                # Handle both JSON strings and dict returns
                if isinstance(content, str):
                    data = json.loads(content)
                else:
                    data = content
            else:
                print(f"  Result type: {type(result)}")
                print(f"  Result dir: {[attr for attr in dir(result) if not attr.startswith('_')]}")
                return

            if data.get("success"):
                print(f"  ✅ Listed runtimes successfully")
            else:
                print(f"  ℹ️  {data.get('message', 'No runtimes found')}")
        except Exception as e:
            print(f"  Error: {e}")


async def test_project_tools():
    """Test project-related tools"""
    print("\n🔍 Testing Project Tools")
    print("=" * 50)
    
    client = Client(mcp)
    
    async with client:
        # Test list_projects_tool
        print("\n📌 list_projects_tool:")
        try:
            result = await client.call_tool("list_projects_tool", {})
            if hasattr(result, 'content') and result.content:
                data = json.loads(result.content[0].text)
                print(f"  Result: {data.get('message', 'Success')[:80]}...")
            else:
                print(f"  Unexpected result format: {type(result)}")
        except Exception as e:
            print(f"  Error: {e}")
        
        # Test get_project_id_tool with parameters
        print("\n📌 get_project_id_tool:")
        try:
            result = await client.call_tool(
                "get_project_id_tool",
                {"project_name": "1234567890123456789"}  # Fixed parameter name
            )
            if hasattr(result, 'content') and result.content:
                data = json.loads(result.content[0].text)
                print(f"  Result: {data.get('message', 'Success')[:80]}...")
        except Exception as e:
            print(f"  Error: {e}")


async def test_job_tools():
    """Test job management tools"""
    print("\n🔍 Testing Job Tools")
    print("=" * 50)
    
    client = Client(mcp)
    
    async with client:
        # Test create_job_tool with full parameters
        print("\n📌 create_job_tool:")
        try:
            result = await client.call_tool(
                "create_job_tool",
                {
                    "name": "Test Job",
                    "script": "train.py",
                    "cpu": 2,
                    "memory": 4,
                    "nvidia_gpu": 0,
                    "kernel": "python3",
                    "project_id": "1234567890123456789"  # Add required project_id
                }
            )
            if hasattr(result, 'content') and result.content:
                data = json.loads(result.content[0].text)
                print(f"  Success: {data.get('success', False)}")
                print(f"  Message: {data.get('message', '')[:80]}...")
        except Exception as e:
            print(f"  Error: {e}")
        
        # Test list_jobs_tool
        print("\n📌 list_jobs_tool:")
        try:
            result = await client.call_tool("list_jobs_tool", {"project_id": "1234567890123456789"})
            if hasattr(result, 'content') and result.content:
                data = json.loads(result.content[0].text)
                print(f"  Result: {data.get('message', 'Success')[:80]}...")
        except Exception as e:
            print(f"  Error: {e}")


async def test_file_tools():
    """Test file operation tools"""
    print("\n🔍 Testing File Tools")
    print("=" * 50)
    
    client = Client(mcp)
    
    async with client:
        # Test upload_file_tool
        print("\n📌 upload_file_tool:")
        try:
            result = await client.call_tool(
                "upload_file_tool",
                {
                    "file_path": "/tmp/test.txt",
                    "target_name": "uploaded.txt",
                    "target_dir": "/data",
                    "project_id": "1234567890123456789"
                }
            )
            if hasattr(result, 'content') and result.content:
                data = json.loads(result.content[0].text)
                print(f"  Success: {data.get('success', False)}")
                print(f"  Message: {data.get('message', '')[:80]}...")
        except Exception as e:
            print(f"  Error: {e}")
        
        # Test list_project_files_tool
        print("\n📌 list_project_files_tool:")
        try:
            result = await client.call_tool(
                "list_project_files_tool",
                {
                    "project_id": "1234567890123456789",
                    "path": "/"
                }
            )
            if hasattr(result, 'content') and result.content:
                data = json.loads(result.content[0].text)
                print(f"  Result: {data.get('message', 'Success')[:80]}...")
        except Exception as e:
            print(f"  Error: {e}")


async def test_model_tools():
    """Test model management tools"""
    print("\n🔍 Testing Model Tools")
    print("=" * 50)
    
    client = Client(mcp)
    
    async with client:
        # Test create_model_build_tool
        print("\n📌 create_model_build_tool:")
        try:
            result = await client.call_tool(
                "create_model_build_tool",
                {
                    "project_id": "1234567890123456789",
                    "model_id": "test-model",
                    "file_path": "model.py",
                    "function_name": "predict",
                    "kernel": "python3"
                }
            )
            if hasattr(result, 'content') and result.content:
                data = json.loads(result.content[0].text)
                print(f"  Success: {data.get('success', False)}")
                print(f"  Message: {data.get('message', '')[:80]}...")
        except Exception as e:
            print(f"  Error: {e}")


async def test_experiment_tools():
    """Test experiment tracking tools"""
    print("\n🔍 Testing Experiment Tools")
    print("=" * 50)
    
    client = Client(mcp)
    
    async with client:
        # Test create_experiment_tool
        print("\n📌 create_experiment_tool:")
        try:
            result = await client.call_tool(
                "create_experiment_tool",
                {
                    "name": "Test Experiment",
                    "description": "Testing MCP server",
                    "project_id": "1234567890123456789"  # Add required project_id
                }
            )
            if hasattr(result, 'content') and result.content:
                data = json.loads(result.content[0].text)
                print(f"  Success: {data.get('success', False)}")
                print(f"  Message: {data.get('message', '')[:80]}...")
        except Exception as e:
            print(f"  Error: {e}")


async def run_all_tests():
    """Run all test categories"""
    print("\n" + "=" * 60)
    print("🚀 CAI Workbehcnk MCP Server Test Suite")
    print("=" * 60)
    
    test_functions = [
        test_server_basics,
        test_system_tools,
        test_project_tools,
        test_job_tools,
        test_file_tools,
        test_model_tools,
        test_experiment_tools
    ]
    
    for test_func in test_functions:
        try:
            await test_func()
        except Exception as e:
            print(f"\n❌ Error in {test_func.__name__}: {str(e)}")
    
    print("\n" + "=" * 60)
    print("✅ Test suite completed")
    print("=" * 60)


async def quick_smoke_test():
    """Quick smoke test - minimal verification"""
    print("\n🚀 Quick Smoke Test")
    
    client = Client(mcp)
    
    async with client:
        # Just verify basics work
        await client.ping()
        tools = await client.list_tools()
        
        print(f"✅ Server running with {len(tools)} tools")
        
        # Try one tool that should work without config
        try:
            result = await client.call_tool("list_runtimes_tool", {})
            data = parse_tool_result(result)
            if data:
                print(f"✅ Tool execution works - listed runtimes")
            else:
                print(f"✅ Tool execution works (result type: {type(result)})")
        except Exception as e:
            print(f"⚠️  Tool execution: {e}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Test CAI Workbench MCP Server")
    parser.add_argument("--quick", action="store_true", help="Run quick smoke test only")
    args = parser.parse_args()
    
    if args.quick:
        asyncio.run(quick_smoke_test())
    else:
        asyncio.run(run_all_tests())
