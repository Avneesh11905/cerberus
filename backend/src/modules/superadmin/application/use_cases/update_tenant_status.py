from uuid import UUID
from src.modules.auth.authentication.application.ports import RefreshTokenRepositoryPort
from src.modules.superadmin.application.ports import TenantRepositoryPort
from src.modules.superadmin.domain.entities import TenantEntity
from src.modules.superadmin.domain.exceptions import TenantNotFoundException
from src.shared.application.ports import CachePort, UoWPort


class UpdateTenantStatusUseCase[SessionType]:
    def __init__(
        self,
        tenant_repository: TenantRepositoryPort,
        refresh_repo: RefreshTokenRepositoryPort | None = None,
        cache: CachePort | None = None,
    ):
        self.tenant_repository = tenant_repository
        self.refresh_repo = refresh_repo
        self.cache = cache

    async def execute(
        self, uow: UoWPort[SessionType], tenant_id: UUID, is_active: bool
    ) -> TenantEntity:
        tenant = await self.tenant_repository.get_by_id(uow.session, tenant_id)
        if not tenant:
            raise TenantNotFoundException()
        tenant.is_active = is_active
        await self.tenant_repository.save(uow.session, tenant)

        if not is_active:
            if self.refresh_repo:
                await self.refresh_repo.revoke_all_for_user(uow.session, tenant_id)
            if self.cache:
                await self.cache.set_string(
                    f"disabled_user:{tenant_id}", "1", ttl=86400 * 30
                )
        else:
            if self.cache:
                await self.cache.delete_key(f"disabled_user:{tenant_id}")

        return tenant
