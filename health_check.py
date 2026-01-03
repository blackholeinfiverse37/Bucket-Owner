#!/usr/bin/env python3
"""
BHIV Central Depository Health Check Script
==========================================

This script performs comprehensive health checks on the system.
"""

import asyncio
import aiohttp
import sys
import json
from typing import Dict, Any

async def check_api_health(base_url: str = "http://localhost:8000") -> Dict[str, Any]:
    """Check API health status"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{base_url}/health", timeout=10) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    return {"error": f"HTTP {response.status}"}
    except Exception as e:
        return {"error": str(e)}

async def check_bucket_status(base_url: str = "http://localhost:8000") -> Dict[str, Any]:
    """Check BHIV Bucket status"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{base_url}/bucket/status", timeout=10) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    return {"error": f"HTTP {response.status}"}
    except Exception as e:
        return {"error": str(e)}

async def check_constitutional_status(base_url: str = "http://localhost:8000") -> Dict[str, Any]:
    """Check constitutional lock status"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{base_url}/bucket/constitutional", timeout=10) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    return {"error": f"HTTP {response.status}"}
    except Exception as e:
        return {"error": str(e)}

async def main():
    """Run comprehensive health checks"""
    print("🏛️ BHIV Central Depository Health Check")
    print("=" * 50)
    
    # Check API health
    print("📊 Checking API Health...")
    health = await check_api_health()
    if "error" in health:
        print(f"❌ API Health: {health['error']}")
        sys.exit(1)
    else:
        print(f"✅ API Health: {health['status']}")
        print(f"   Services: {health.get('services', {})}")
    
    # Check BHIV Bucket
    print("\n🏛️ Checking BHIV Bucket Status...")
    bucket = await check_bucket_status()
    if "error" in bucket:
        print(f"❌ BHIV Bucket: {bucket['error']}")
    else:
        print(f"✅ BHIV Bucket: Active")
        print(f"   Version: {bucket.get('version', 'Unknown')}")
    
    # Check Constitutional Status
    print("\n⚖️ Checking Constitutional Status...")
    constitutional = await check_constitutional_status()
    if "error" in constitutional:
        print(f"❌ Constitutional: {constitutional['error']}")
    else:
        locked = constitutional.get('locked', False)
        integrity = constitutional.get('integrity_verified', False)
        print(f"✅ Constitutional Lock: {'Locked' if locked else 'Unlocked'}")
        print(f"✅ Integrity: {'Verified' if integrity else 'Failed'}")
    
    print("\n🎉 Health check completed!")
    
    # Overall status
    if "error" not in health and health.get("status") == "healthy":
        print("✅ System Status: HEALTHY")
        sys.exit(0)
    else:
        print("⚠️ System Status: DEGRADED")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())