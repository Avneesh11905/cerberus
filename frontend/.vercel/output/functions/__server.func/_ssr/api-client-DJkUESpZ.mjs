import { r as __exportAll$1 } from "../_runtime.mjs";
import { t as useAuthStore } from "./auth-E6d_NOW7.mjs";
import { t as axios } from "../_libs/axios+[...].mjs";
//#region node_modules/.nitro/vite/services/ssr/assets/api-client-DJkUESpZ.js
var api_client_DJkUESpZ_exports = /* @__PURE__ */ __exportAll$1({
	a: () => refreshClient,
	i: () => extractErrorMessage,
	n: () => apiClient,
	r: () => api_client_exports,
	t: () => API_URL
});
var __defProp = Object.defineProperty;
var __exportAll = (all, no_symbols) => {
	let target = {};
	for (var name in all) __defProp(target, name, {
		get: all[name],
		enumerable: true
	});
	if (!no_symbols) __defProp(target, Symbol.toStringTag, { value: "Module" });
	return target;
};
var api_client_exports = /* @__PURE__ */ __exportAll({
	API_URL: () => API_URL,
	apiClient: () => apiClient,
	extractErrorMessage: () => extractErrorMessage,
	refreshClient: () => refreshClient,
	refreshToken: () => refreshToken
});
function extractErrorMessage(error, fallback = "An error occurred") {
	if (!error) return fallback;
	if (axios.isAxiosError(error)) {
		const data = error.response?.data;
		const detail = data?.detail;
		if (Array.isArray(detail) && detail.length > 0 && detail[0].msg) return String(detail[0].msg);
		if (typeof detail === "string") return detail;
		if (typeof detail === "object" && detail !== null && detail.msg) return String(detail.msg);
		if (Array.isArray(data) && data.length > 0 && data[0].msg) return String(data[0].msg);
		if (typeof data === "object" && data !== null && data.msg) return String(data.msg);
	}
	if (error instanceof Error) return error.message;
	if (typeof error === "string") return error;
	return fallback;
}
var API_URL = "http://localhost:8000/v1";
var apiClient = axios.create({
	baseURL: API_URL,
	withCredentials: true,
	xsrfCookieName: "csrf_token",
	xsrfHeaderName: "X-CSRF",
	headers: { "Content-Type": "application/json" }
});
var isRefreshing = false;
var failedQueue = [];
var processQueue = (error, token = null) => {
	failedQueue.forEach((prom) => {
		if (error) prom.reject(error);
		else prom.resolve(token);
	});
	failedQueue = [];
};
apiClient.interceptors.request.use((config) => {
	const { accessToken, csrfToken } = useAuthStore.getState();
	if (accessToken) config.headers.Authorization = `Bearer ${accessToken}`;
	if (csrfToken) config.headers["X-CSRF"] = csrfToken;
	return config;
}, (error) => {
	return Promise.reject(error);
});
var refreshClient = axios.create({
	baseURL: API_URL,
	withCredentials: true,
	xsrfCookieName: "csrf_token",
	xsrfHeaderName: "X-CSRF",
	headers: { "Content-Type": "application/json" }
});
var refreshToken = async () => {
	if (isRefreshing) return new Promise((resolve, reject) => {
		failedQueue.push({
			resolve,
			reject
		});
	});
	isRefreshing = true;
	try {
		const csrfToken = useAuthStore.getState().csrfToken;
		const { data } = await refreshClient.post("/auth/refresh", {}, { headers: csrfToken ? { "X-CSRF": csrfToken } : void 0 });
		const newAccessToken = data.access_token;
		const newCsrfToken = data.csrf_token;
		if (data.user) useAuthStore.getState().setAuth(newAccessToken, newCsrfToken || "", data.user);
		else useAuthStore.getState().setAccessToken(newAccessToken, newCsrfToken);
		processQueue(null, newAccessToken);
		return newAccessToken;
	} catch (refreshError) {
		processQueue(refreshError, null);
		useAuthStore.getState().logout();
		return Promise.reject(refreshError);
	} finally {
		isRefreshing = false;
	}
};
apiClient.interceptors.response.use((response) => {
	return response;
}, async (error) => {
	const originalRequest = error.config;
	const isAuthRoute = originalRequest.url?.includes("/auth/login") || originalRequest.url?.includes("/auth/verify-email") || originalRequest.url?.includes("/auth/refresh") || originalRequest.url?.includes("/auth/password");
	if (error.response?.status === 401 && !originalRequest._retry && !isAuthRoute) {
		if (isRefreshing) return new Promise(function(resolve, reject) {
			failedQueue.push({
				resolve,
				reject
			});
		}).then((token) => {
			originalRequest.headers.Authorization = "Bearer " + token;
			return apiClient(originalRequest);
		}).catch((err) => {
			return Promise.reject(err);
		});
		originalRequest._retry = true;
		try {
			const newAccessToken = await refreshToken();
			originalRequest.headers.Authorization = `Bearer ${newAccessToken}`;
			const newCsrfToken = useAuthStore.getState().csrfToken;
			if (newCsrfToken) originalRequest.headers["X-CSRF"] = newCsrfToken;
			return apiClient(originalRequest);
		} catch (refreshError) {
			return Promise.reject(refreshError);
		}
	}
	if (error.response?.status === 403 && !originalRequest.url?.includes("/users/me")) {
		const accessToken = useAuthStore.getState().accessToken;
		if (accessToken) axios.get(`${API_URL}/users/me`, { headers: { Authorization: `Bearer ${accessToken}` } }).then(({ data }) => {
			const currentUser = useAuthStore.getState().user;
			if (currentUser && currentUser.role !== data.role) {
				useAuthStore.getState().setUser(data);
				window.location.href = "/dashboard";
			}
		}).catch(() => {});
	}
	return Promise.reject(error);
});
//#endregion
export { refreshClient as a, extractErrorMessage as i, apiClient as n, api_client_DJkUESpZ_exports as r, API_URL as t };
