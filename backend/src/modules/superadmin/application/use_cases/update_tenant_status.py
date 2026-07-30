from src.modules.superadmin.application.commands.superadmin_commands import (
    UpdateTenantStatusCommand,
)
from src.modules.superadmin.application.dtos.superadmin_dtos import (
    UpdateTenantStatusDTO,
)
from src.modules.superadmin.application.ports.superadmin_unit_of_work import (
    SuperAdminUoWPort,
)
from src.modules.superadmin.domain.exceptions import TenantNotFoundException
from src.shared.application.ports import CachePort, AnalyticsEventPort


class UpdateTenantStatusUseCase:
    def __init__(
        self,
        uow: SuperAdminUoWPort,
        analytics: AnalyticsEventPort,
        cache: CachePort | None = None,
    ):
        self.uow = uow
        self.cache = cache
        self.analytics = analytics

    async def execute(
        self, command: UpdateTenantStatusCommand
    ) -> UpdateTenantStatusDTO:
        async with self.uow:
            tenant = await self.uow.tenant_repo.get_by_id(command.tenant_id)
            if not tenant:
                raise TenantNotFoundException()
            tenant.is_active = command.is_active
            await self.uow.tenant_repo.save(tenant)

            if not command.is_active:
                if self.uow.refresh_token_repo:
                    await self.uow.refresh_token_repo.revoke_all_for_user(
                        command.tenant_id
                    )
                if self.cache:
                    await self.cache.set_string(
                        f"disabled_user:{command.tenant_id}", "1", ttl=86400 * 30
                    )
            else:
                if self.cache:
                    await self.cache.delete_key(f"disabled_user:{command.tenant_id}")

        if not command.is_active:
            self.analytics.record_event(
                event_type="TENANT_SUSPENDED",
                tenant_id=command.tenant_id,
            )

        return UpdateTenantStatusDTO(tenant=tenant)
