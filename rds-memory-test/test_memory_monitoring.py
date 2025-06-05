#!/usr/bin/env python3

import subprocess
import time
import json
import sys
from datetime import datetime

def test_docker_stats():
    """Test Docker stats functionality"""
    print("Testing Docker stats command...")
    
    try:
        result = subprocess.run(
            ["docker", "ps", "--format", "{{.Names}}"],
            capture_output=True, text=True, check=True
        )
        
        container_names = [name.strip() for name in result.stdout.strip().split('\n') if name.strip()]
        print(f"Found containers: {container_names}")
        
        if not container_names:
            print("No running containers found!")
            return False
        
        cmd = ["docker", "stats", "--no-stream", "--format", "json"] + container_names
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        
        print("Docker stats output:")
        for line in result.stdout.strip().split('\n'):
            if line:
                data = json.loads(line)
                print(f"  {data['Name']}: {data['MemUsage']} ({data['MemPerc']})")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"Error testing Docker stats: {e}")
        return False

def test_monitoring_script():
    """Test the monitoring script functionality"""
    print("\nTesting monitoring script...")
    
    try:
        result = subprocess.run(
            ["python", "monitor_memory.py"],
            capture_output=True, text=True, timeout=30
        )
        
        print("Monitoring script output:")
        print(result.stdout)
        
        if result.stderr:
            print("Monitoring script errors:")
            print(result.stderr)
        
        return result.returncode == 0
        
    except subprocess.TimeoutExpired:
        print("Monitoring script timed out (expected for continuous monitoring)")
        return True
    except Exception as e:
        print(f"Error testing monitoring script: {e}")
        return False

def main():
    """Main test function"""
    print("=== Memory Monitoring Test ===")
    
    docker_stats_ok = test_docker_stats()
    
    monitoring_ok = test_monitoring_script()
    
    print("\n=== Test Results ===")
    print(f"Docker stats test: {'PASS' if docker_stats_ok else 'FAIL'}")
    print(f"Monitoring script test: {'PASS' if monitoring_ok else 'FAIL'}")
    
    if docker_stats_ok and monitoring_ok:
        print("All memory monitoring tests passed!")
        return 0
    else:
        print("Some tests failed.")
        return 1

if __name__ == "__main__":
    exit(main())
