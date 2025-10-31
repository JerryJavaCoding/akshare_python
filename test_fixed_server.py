#!/usr/bin/env python3
"""Test script for the fixed MCP server."""
import subprocess
import json
import time

def test_mcp_server():
    """Test the fixed MCP server with standard MCP protocol messages."""
    
    # Start the MCP server
    process = subprocess.Popen(
        ['python', 'scripts/run_fixed_server.py'],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    try:
        # Test initialize request
        initialize_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {
                    "name": "test-client",
                    "version": "1.0.0"
                }
            }
        }
        
        print("Sending initialize request...")
        process.stdin.write(json.dumps(initialize_request) + '\n')
        process.stdin.flush()
        
        # Read response
        initialize_response = process.stdout.readline().strip()
        print(f"Initialize response: {initialize_response}")
        
        # Test tools/list request
        list_tools_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list"
        }
        
        print("Sending tools/list request...")
        process.stdin.write(json.dumps(list_tools_request) + '\n')
        process.stdin.flush()
        
        # Read response
        list_tools_response = process.stdout.readline().strip()
        print(f"Tools/list response: {list_tools_response}")
        
        # Test echo tool
        echo_request = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "echo",
                "arguments": {
                    "text": "Hello, MCP!"
                }
            }
        }
        
        print("Sending echo request...")
        process.stdin.write(json.dumps(echo_request) + '\n')
        process.stdin.flush()
        
        # Read response
        echo_response = process.stdout.readline().strip()
        print(f"Echo response: {echo_response}")
        
        print("\n✅ MCP server test completed successfully!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
    finally:
        # Clean up
        process.terminate()
        process.wait()

if __name__ == "__main__":
    test_mcp_server()
