import { o as __toESM } from "../_runtime.mjs";
import { r as create } from "../_libs/zustand.mjs";
import { u as require_react } from "../_libs/@floating-ui/react-dom+[...].mjs";
import { t as useAuthStore } from "./auth-E6d_NOW7.mjs";
import { t as API_URL } from "./api-client-DJkUESpZ.mjs";
import { n as require_jsx_runtime } from "../_libs/@marsidev/react-turnstile+[...].mjs";
import { t as fetchEventSource } from "../_libs/microsoft__fetch-event-source.mjs";
//#region node_modules/.nitro/vite/services/ssr/assets/useAnalyticsStream-DpFV3Eam.js
var import_react = /* @__PURE__ */ __toESM(require_react());
var import_jsx_runtime = require_jsx_runtime();
var useAnalyticsStream = create((set) => ({
	data: null,
	status: "connecting",
	setData: (data) => set({ data }),
	setStatus: (status) => set({ status }),
	processBulkData: (metrics, totals) => set(() => {
		const timeSeries = metrics.map((row) => ({
			date: row.date ?? "",
			api_requests: row.api_requests ?? 0,
			login_successes: row.login_successes ?? 0,
			login_failures: row.login_failures ?? 0,
			registrations: row.registrations ?? 0,
			active_users: row.active_users ?? 0
		}));
		return { data: {
			totals: totals ?? {
				api_requests: 0,
				login_successes: 0,
				login_failures: 0,
				registrations: 0,
				active_users: 0
			},
			timeSeries
		} };
	}),
	processLiveEvent: (event) => set((state) => {
		if (!state.data) return state;
		const et = event.event_type;
		const newData = { ...state.data };
		const newTotals = { ...newData.totals };
		const bumpTimeSeries = (key, amount = 1) => {
			if (newData.timeSeries.length === 0) return;
			const ts = [...newData.timeSeries];
			const last = { ...ts[ts.length - 1] };
			last[key] = (last[key] ?? 0) + amount;
			ts[ts.length - 1] = last;
			newData.timeSeries = ts;
		};
		if (et === "API_REQUEST") {
			newTotals.api_requests += 1;
			bumpTimeSeries("api_requests");
		}
		if (et === "LOGIN_SUCCESS") {
			newTotals.login_successes += 1;
			bumpTimeSeries("login_successes");
		}
		if (et === "LOGIN_FAILED") {
			newTotals.login_failures += 1;
			bumpTimeSeries("login_failures");
		}
		if (et === "REGISTRATION") {
			newTotals.registrations += 1;
			bumpTimeSeries("registrations");
		}
		if (et === "PROJECT_CREATED") {
			if (newTotals.projects_created !== void 0) newTotals.projects_created += 1;
			bumpTimeSeries("projects_created");
		}
		if (et === "EMAIL_SENT") bumpTimeSeries("emails_sent");
		if (et === "EMAIL_FAILED") bumpTimeSeries("emails_failed");
		if (newData.platform_adoption) {
			const pa = { ...newData.platform_adoption };
			if (et === "API_REQUEST") pa.api_requests = (pa.api_requests ?? 0) + 1;
			if (et === "LOGIN_SUCCESS") pa.login_successes = (pa.login_successes ?? 0) + 1;
			if (et === "LOGIN_FAILED") pa.login_failures = (pa.login_failures ?? 0) + 1;
			if (et === "REGISTRATION") pa.registrations = (pa.registrations ?? 0) + 1;
			if (et === "TENANT_ONBOARDED") pa.total_tenants = (pa.total_tenants ?? 0) + 1;
			newData.platform_adoption = pa;
		}
		if (newData.end_user_usage) {
			const eu = { ...newData.end_user_usage };
			if (et === "PROJECT_CREATED") eu.total_projects = (eu.total_projects ?? 0) + 1;
			if (et === "REGISTRATION") eu.registrations = (eu.registrations ?? 0) + 1;
			newData.end_user_usage = eu;
		}
		return { data: {
			...newData,
			totals: newTotals
		} };
	})
}));
function AnalyticsProvider({ children, projectId, scope = "tenant" }) {
	const abortControllerRef = (0, import_react.useRef)(null);
	const token = useAuthStore((state) => state.accessToken);
	const setStatus = useAnalyticsStream((state) => state.setStatus);
	(0, import_react.useEffect)(() => {
		if (!token) return;
		let isMounted = true;
		const streamUrl = scope === "project" && projectId ? `${API_URL}/analytics/projects/${projectId}/events/stream` : scope === "system" ? `${API_URL}/analytics/system/events/stream` : `${API_URL}/analytics/tenants/me/events/stream`;
		const connect = async () => {
			if (!isMounted) return;
			setStatus("connecting");
			abortControllerRef.current = new AbortController();
			try {
				await fetchEventSource(streamUrl, {
					method: "GET",
					headers: { Accept: "text/event-stream" },
					fetch: async (input, init) => {
						let latestToken = useAuthStore.getState().accessToken;
						const headers = {
							...init?.headers,
							Authorization: `Bearer ${latestToken}`
						};
						let response = await fetch(input, {
							...init,
							headers
						});
						if (response.status === 401) try {
							const { refreshToken } = await import("./api-client-DJkUESpZ.mjs").then((n) => n.r).then((n) => n.r);
							latestToken = await refreshToken();
							response = await fetch(input, {
								...init,
								headers: {
									...init?.headers,
									Authorization: `Bearer ${latestToken}`
								}
							});
						} catch {
							useAuthStore.getState().logout();
						}
						return response;
					},
					openWhenHidden: true,
					signal: abortControllerRef.current.signal,
					onopen: async (response) => {
						if (response.ok && response.headers.get("content-type")?.includes("text/event-stream")) setStatus("connected");
						else throw new Error(`Failed to connect: ${response.status}`);
					},
					onmessage: (event) => {
						try {
							if (!event.data) return;
							const parsed = JSON.parse(event.data);
							if (parsed.metrics && Array.isArray(parsed.metrics)) useAnalyticsStream.getState().processBulkData(parsed.metrics, parsed.totals);
							if (parsed.platform_adoption) {
								const current = useAnalyticsStream.getState().data;
								useAnalyticsStream.getState().setData({
									...current ?? {
										totals: {
											api_requests: 0,
											login_successes: 0,
											login_failures: 0,
											registrations: 0,
											active_users: 0
										},
										timeSeries: []
									},
									timeSeries: parsed.metrics?.map((r) => ({
										date: r.date ?? "",
										api_requests: r.api_requests ?? 0,
										login_successes: r.login_successes ?? 0,
										login_failures: r.login_failures ?? 0,
										registrations: r.registrations ?? 0,
										active_users: r.active_users ?? 0
									})) ?? current?.timeSeries ?? [],
									platform_adoption: parsed.platform_adoption,
									end_user_usage: parsed.end_user_usage,
									totals: {
										api_requests: (parsed.platform_adoption?.api_requests ?? 0) + (parsed.end_user_usage?.api_requests ?? 0),
										login_successes: (parsed.platform_adoption?.login_successes ?? 0) + (parsed.end_user_usage?.login_successes ?? 0),
										login_failures: (parsed.platform_adoption?.login_failures ?? 0) + (parsed.end_user_usage?.login_failures ?? 0),
										registrations: parsed.platform_adoption?.registrations ?? 0,
										active_users: parsed.platform_adoption?.active_users ?? 0
									}
								});
							}
							if (parsed.event_type) useAnalyticsStream.getState().processLiveEvent(parsed);
						} catch (e) {
							console.error("Failed to parse SSE data", e);
						}
					},
					onclose: () => {
						setStatus("error");
					},
					onerror: (err) => {
						if (err instanceof Error && err.name === "AbortError") return null;
						if (err?.name === "AbortError") return null;
						console.error("SSE Error:", err);
						setStatus("error");
						return 5e3;
					}
				});
				setTimeout(connect, 5e3);
			} catch (err) {
				if (err instanceof Error && err.name !== "AbortError") {
					setStatus("error");
					setTimeout(connect, 5e3);
				}
			}
		};
		connect();
		return () => {
			isMounted = false;
			abortControllerRef.current?.abort();
		};
	}, [
		token,
		scope,
		setStatus,
		projectId
	]);
	return /* @__PURE__ */ (0, import_jsx_runtime.jsx)(import_jsx_runtime.Fragment, { children });
}
//#endregion
export { useAnalyticsStream as n, AnalyticsProvider as t };
