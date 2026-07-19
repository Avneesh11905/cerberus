from uuid import uuid4

from src.shared.adapters.api_key import ApiKeyAdapter


def test_api_key_generation_and_hashing():
    adapter = ApiKeyAdapter()
    project_id = uuid4()

    # Generate
    key = adapter.generate(project_id)
    assert key.startswith(f"cerb_{project_id.hex}_")

    # Hash
    hashed = adapter.hash(key)
    assert len(hashed) == 64  # SHA-256 is 64 hex chars

    # Verify
    assert adapter.verify(key, hashed) is True
    assert adapter.verify(key, "wrong_hash") is False
    assert adapter.verify("wrong_key", hashed) is False
