import pytest
from src.shared.adapters.rsa_key import RsaKeyAdapter


@pytest.mark.asyncio
async def test_rsa_key_generation():
    adapter = RsaKeyAdapter()
    private_pem, public_pem = await adapter.generate_keypair()

    assert "-----BEGIN PRIVATE KEY-----" in private_pem
    assert "-----END PRIVATE KEY-----" in private_pem
    assert "-----BEGIN PUBLIC KEY-----" in public_pem
    assert "-----END PUBLIC KEY-----" in public_pem
