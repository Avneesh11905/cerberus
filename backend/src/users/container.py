"""
Dependency Injection container for the Users domain.
Instantiates the concrete repositories and makes them available to the API routes.
"""
from src.authentication.container import get_container
from src.users.adapters.user_profile_repository import SQLUserProfileRepository

# Container for the users slice
user_profile_repository = SQLUserProfileRepository(get_container().refresh_token_repo)
