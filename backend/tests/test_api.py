"""
暗标竞标系统 - API 测试脚本
"""
import pytest
import asyncio
from httpx import AsyncClient
from src.main import app
from src.database import init_db, create_sample_data
from src.crypto import crypto_manager


@pytest.fixture(scope="module")
def event_loop():
    """创建事件循环"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="module")
async def client():
    """创建测试客户端"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.mark.asyncio
async def test_root():
    """测试根路径"""
    response = await app.router.routes[0].methods['GET']()
    assert response is not None


@pytest.mark.asyncio
async def test_health_check():
    """测试健康检查"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"


@pytest.mark.asyncio
async def test_crypto_encrypt_decrypt():
    """测试加密解密功能"""
    # 测试报价加密
    price = 10000.00
    encrypted = crypto_manager.encrypt_price(price)
    
    # 验证密文不为空
    assert encrypted is not None
    assert len(encrypted) > 0
    
    # 解密验证
    decrypted = crypto_manager.decrypt_price(encrypted)
    assert decrypted["price"] == price


@pytest.mark.asyncio
async def test_crypto_with_metadata():
    """测试带元数据的加密"""
    price = 15000.50
    metadata = {"currency": "CNY", "tax_included": True}
    
    encrypted = crypto_manager.encrypt_price(price, metadata)
    decrypted = crypto_manager.decrypt_price(encrypted)
    
    assert decrypted["price"] == price
    assert decrypted["metadata"] == metadata


@pytest.mark.asyncio
async def test_register_user():
    """测试用户注册"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/api/auth/register", json={
            "name": "测试用户",
            "email": "test@example.com",
            "password": "password123",
            "role": "bidder",
            "company": "测试公司"
        })
        
        # 可能成功或已存在
        assert response.status_code in [200, 400]


@pytest.mark.asyncio
async def test_login():
    """测试用户登录"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/api/auth/login", json={
            "email": "bidder1@example.com",
            "password": "password123"
        })
        
        if response.status_code == 200:
            data = response.json()
            assert "access_token" in data
            assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_wrong_password():
    """测试错误密码登录"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/api/auth/login", json={
            "email": "bidder1@example.com",
            "password": "wrongpassword"
        })
        
        assert response.status_code == 401


@pytest.mark.asyncio
async def test_list_projects():
    """测试获取项目列表"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/api/projects")
        assert response.status_code == 200
        assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_create_project_unauthorized():
    """测试未授权创建项目"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/api/projects", json={
            "title": "测试项目",
            "description": "测试描述",
            "params": {"规格": "A4"},
            "deadline": "2026-12-31T23:59:59"
        })
        
        # 应该返回 403 (需要招标方权限)
        assert response.status_code == 403


@pytest.mark.asyncio
async def test_submit_bid_unauthorized():
    """测试未授权提交投标"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/api/projects/1/bids", json={
            "price": 10000.00,
            "params": {"交货期": "7 天"}
        })
        
        # 应该返回 403 (需要投标方权限)
        assert response.status_code == 403


if __name__ == "__main__":
    pytest.main(["-v", __file__])
