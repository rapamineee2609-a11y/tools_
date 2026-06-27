import pytest
import asyncio
from core.network import get_local_ip, get_public_ip, check_internet

@pytest.mark.asyncio
async def test_get_local_ip():
    ip = get_local_ip()
    assert ip is not None
    assert isinstance(ip, str)

@pytest.mark.asyncio
async def test_get_public_ip():
    ip = await get_public_ip()
    assert ip is not None
    assert "." in ip

@pytest.mark.asyncio
async def test_check_internet():
    result = await check_internet()
    assert isinstance(result, bool)
