import { n as apiClient } from "./api-client-DJkUESpZ.mjs";
//#region node_modules/.nitro/vite/services/ssr/assets/projects-B5Nezf2L.js
var getProjects = async (params) => {
	const { data } = await apiClient.get("/projects/", { params });
	return data;
};
var getProject = async (projectId) => {
	const { data } = await apiClient.get(`/projects/${projectId}`);
	return data;
};
var createProject = async (payload) => {
	const { data } = await apiClient.post("/projects/", payload);
	return data;
};
var updateProjectName = async (projectId, name) => {
	const { data } = await apiClient.put(`/projects/${projectId}/name`, { name });
	return data;
};
var updateProjectEnvironment = async (projectId, environment) => {
	const { data } = await apiClient.put(`/projects/${projectId}/environment`, { environment });
	return data;
};
var updateProjectFrontendUrl = async (projectId, frontendUrl) => {
	const { data } = await apiClient.put(`/projects/${projectId}/frontend-url`, { frontend_url: frontendUrl });
	return data;
};
var updateProjectOrigins = async (projectId, allowedOrigins) => {
	const { data } = await apiClient.put(`/projects/${projectId}/origins`, { allowed_origins: allowedOrigins });
	return data;
};
var updateProjectOAuth = async (projectId, payload) => {
	const { data } = await apiClient.put(`/projects/${projectId}/oauth`, payload);
	return data;
};
var updateProjectClaims = async (projectId, claims) => {
	const { data } = await apiClient.put(`/projects/${projectId}/claims`, { claims });
	return data;
};
var deleteProject = async (projectId) => {
	await apiClient.delete(`/projects/${projectId}`);
};
var rotateApiKey = async (projectId) => {
	const { data } = await apiClient.post(`/projects/${projectId}/keys/rotate-api-key`);
	return data;
};
var rotateJwtSecret = async (projectId) => {
	const { data } = await apiClient.post(`/projects/${projectId}/keys/rotate-jwt-secret`);
	return data;
};
var getProjectSecrets = async (projectId) => {
	const { data } = await apiClient.get(`/projects/${projectId}/secrets`);
	return data;
};
var getProjectUsers = async (projectId, page = 1, size = 50, search = "") => {
	const params = new URLSearchParams();
	params.append("page", page.toString());
	params.append("size", size.toString());
	if (search) params.append("search", search);
	const { data } = await apiClient.get(`/projects/${projectId}/users?${params.toString()}`);
	return data;
};
var getTenantUsers = async (page = 1, size = 50, search = "") => {
	const params = new URLSearchParams();
	params.append("page", page.toString());
	params.append("size", size.toString());
	if (search) params.append("search", search);
	const { data } = await apiClient.get(`/projects/users?${params.toString()}`);
	return data;
};
var updateProjectUserStatus = async (projectId, userId, isActive) => {
	const { data } = await apiClient.put(`/projects/${projectId}/users/${userId}/status`, { is_active: isActive });
	return data;
};
var getProjectUserClaims = async (projectId, userId) => {
	const { data } = await apiClient.get(`/projects/${projectId}/users/${userId}/claims`);
	return data;
};
var updateProjectUserClaims = async (projectId, userId, overrides) => {
	const { data } = await apiClient.patch(`/projects/${projectId}/users/${userId}/claims`, { overrides });
	return data;
};
var updateTenantUserStatus = async (email, isActive) => {
	const { data } = await apiClient.post(`/projects/users/${email}/status`, { is_active: isActive });
	return data;
};
//#endregion
export { updateProjectUserClaims as _, getProjectUserClaims as a, getTenantUsers as c, updateProjectClaims as d, updateProjectEnvironment as f, updateProjectOrigins as g, updateProjectOAuth as h, getProjectSecrets as i, rotateApiKey as l, updateProjectName as m, deleteProject as n, getProjectUsers as o, updateProjectFrontendUrl as p, getProject as r, getProjects as s, createProject as t, rotateJwtSecret as u, updateProjectUserStatus as v, updateTenantUserStatus as y };
