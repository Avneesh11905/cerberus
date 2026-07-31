import { n as apiClient } from "./api-client-DJkUESpZ.mjs";
//#region node_modules/.nitro/vite/services/ssr/assets/superadmin-BFifgmRl.js
var getTenants = async (page = 1, size = 50, search) => {
	const params = {
		page,
		size
	};
	if (search) params.search = search;
	const { data } = await apiClient.get("/superadmin/tenants", { params });
	return data;
};
var updateTenantStatus = async (tenantId, isActive) => {
	const { data } = await apiClient.patch(`/superadmin/tenants/${tenantId}/status`, { is_active: isActive });
	return data;
};
var updateTenantRole = async (tenantId, role) => {
	const { data } = await apiClient.patch(`/superadmin/tenants/${tenantId}/role`, { role });
	return data;
};
var getSystemLogs = async (page = 1, limit = 100, level, startDate, endDate) => {
	const params = {
		page,
		limit
	};
	if (level) params.level = level;
	if (startDate) params.start_date = startDate;
	if (endDate) params.end_date = endDate;
	const { data } = await apiClient.get("/superadmin/logs", { params });
	return data;
};
//#endregion
export { updateTenantStatus as i, getTenants as n, updateTenantRole as r, getSystemLogs as t };
