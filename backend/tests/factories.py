import factory
from factory.alchemy import SQLAlchemyModelFactory
from src.core.models import SystemLog
from src.modules.users.infrastructure.models import User

class BaseFactory(SQLAlchemyModelFactory):
    pass
    # Note: sqlalchemy_session should be injected in conftest.py or tests

class SystemLogFactory(BaseFactory):
    class Meta:
        model = SystemLog

    id = factory.Faker("uuid4")
    action = factory.Faker("word")
    entity_id = factory.Faker("uuid4")
    details = {}
    ip_address = factory.Faker("ipv4")

class UserFactory(BaseFactory):
    class Meta:
        model = User

    id = factory.Faker("uuid4")
    email = factory.Faker("email")
    hashed_password = "dummy_hash"
    is_active = True
    is_verified = True
