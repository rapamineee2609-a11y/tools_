import socket
import subprocess
import asyncio
import aiohttp
import platform
from typing import Optional, Tuple

async def get_public_ip() -> Optional[str]:
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("https://api.ipify.org", timeout=5) as resp:
                return await resp.text()
    except:
        return None

def get_local_ip() -> Optional[str]:
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return None

async def check_internet() -> bool:
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("https://google.com", timeout=3) as resp:
                return resp.status == 200
    except:
        return False

async def ping_host(host: str, count: int = 4) -> str:
    system = platform.system().lower()
    if system == "windows":
        cmd = ["ping", "-n", str(count), host]
    else:
        cmd = ["ping", "-c", str(count), host]
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=10
        )
        return result.stdout if result.returncode == 0 else f"Ping failed: {result.stderr}"
    except Exception as e:
        return f"Error: {str(e)}"

async def traceroute_host(host: str) -> str:
    system = platform.system().lower()
    if system == "windows":
        cmd = ["tracert", host]
    else:
        cmd = ["traceroute", "-n", host]
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30
        )
        return result.stdout if result.returncode == 0 else f"Traceroute failed: {result.stderr}"
    except Exception as e:
        return f"Error: {str(e)}"
