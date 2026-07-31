import { o as __toESM } from "./_runtime.mjs";
import { u as require_react } from "./_libs/@floating-ui/react-dom+[...].mjs";
import { t as useAuthStore } from "./_ssr/auth-E6d_NOW7.mjs";
import { t as API_URL } from "./_ssr/api-client-DJkUESpZ.mjs";
import { n as require_jsx_runtime } from "./_libs/@marsidev/react-turnstile+[...].mjs";
import { t as fetchEventSource } from "./_libs/microsoft__fetch-event-source.mjs";
import { W as CircleAlert, k as LogIn, nt as Activity, r as Users } from "./_libs/lucide-react.mjs";
import { a as XAxis, d as Legend, f as ResponsiveContainer, i as YAxis, l as CartesianGrid, n as BarChart, o as Bar, s as Area, t as AreaChart, u as Tooltip } from "./_libs/recharts+[...].mjs";
import { t as Route } from "./_protected.projects._projectId.analytics-DglSHjUP.mjs";
import { a as CardHeader, n as CardContent, o as CardTitle, t as Card } from "./_ssr/card-D2S-3Lsc.mjs";
//#region node_modules/.nitro/vite/services/ssr/assets/_protected.projects._projectId.analytics-BGmM0-AO.js
var import_react = /* @__PURE__ */ __toESM(require_react());
var import_jsx_runtime = require_jsx_runtime();
var TOOLTIP_STYLE = {
	contentStyle: {
		backgroundColor: "#FAEED1",
		border: "2px solid #3d405b",
		borderRadius: "8px",
		boxShadow: "4px 4px 0px rgba(61, 64, 91, 1)"
	},
	itemStyle: { fontWeight: 700 },
	labelStyle: {
		fontWeight: 900,
		color: "#3d405b",
		marginBottom: "8px"
	}
};
function AnalyticsTab() {
	const { projectId } = Route.useParams();
	const accessToken = useAuthStore((state) => state.accessToken);
	const [timeSeries, setTimeSeries] = (0, import_react.useState)([]);
	const [totals, setTotals] = (0, import_react.useState)({
		api_requests: 0,
		login_successes: 0,
		login_failures: 0,
		registrations: 0,
		active_users: 0
	});
	(0, import_react.useEffect)(() => {
		if (!accessToken) return;
		let isMounted = true;
		const controller = new AbortController();
		const connectStream = async () => {
			try {
				await fetchEventSource(`${API_URL}/analytics/projects/${projectId}/events/stream`, {
					method: "GET",
					headers: { Authorization: `Bearer ${accessToken}` },
					signal: controller.signal,
					onmessage(ev) {
						if (ev.event === "project_metrics_update" && ev.data) {
							const parsed = JSON.parse(ev.data);
							if (parsed.metrics && Array.isArray(parsed.metrics)) {
								setTimeSeries(parsed.metrics);
								if (parsed.totals) setTotals(parsed.totals);
							}
							if (parsed.event_type) {
								setTotals((prev) => {
									const next = { ...prev };
									if (parsed.event_type === "API_REQUEST") next.api_requests += 1;
									else if (parsed.event_type === "LOGIN_SUCCESS") next.login_successes += 1;
									else if (parsed.event_type === "LOGIN_FAILED") next.login_failures += 1;
									else if (parsed.event_type === "REGISTRATION") next.registrations += 1;
									return next;
								});
								setTimeSeries((prev) => {
									if (prev.length === 0) return prev;
									const last = { ...prev[prev.length - 1] };
									if (parsed.event_type === "API_REQUEST") last.api_requests += 1;
									else if (parsed.event_type === "LOGIN_SUCCESS") last.login_successes += 1;
									else if (parsed.event_type === "LOGIN_FAILED") last.login_failures += 1;
									else if (parsed.event_type === "REGISTRATION") last.registrations += 1;
									return [...prev.slice(0, -1), last];
								});
							}
						}
					},
					onerror(err) {
						if (err instanceof Error && err.name === "AbortError") return;
						if (err?.name === "AbortError") return;
						console.error("SSE Error:", err);
						if (isMounted) setTimeout(connectStream, 5e3);
					},
					onclose() {
						if (isMounted) setTimeout(connectStream, 5e3);
					}
				});
			} catch (err) {
				console.error("Failed to connect to SSE:", err);
			}
		};
		connectStream();
		return () => {
			isMounted = false;
			controller.abort();
		};
	}, [projectId, accessToken]);
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
		className: "flex flex-col gap-8 w-full animate-in fade-in slide-in-from-bottom-2 duration-300",
		children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
			className: "grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6",
			children: [
				/* @__PURE__ */ (0, import_jsx_runtime.jsxs)(Card, {
					className: "bg-sand",
					children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(CardHeader, {
						className: "pb-2",
						children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(CardTitle, {
							className: "text-lg flex items-center gap-2 text-slate/70",
							children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Activity, { className: "w-5 h-5 text-terracotta" }), " API Requests"]
						})
					}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(CardContent, { children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
						className: "text-4xl font-black text-slate",
						children: totals.api_requests.toLocaleString()
					}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
						className: "text-xs text-slate/50 font-medium mt-1",
						children: "Last 30 days"
					})] })]
				}),
				/* @__PURE__ */ (0, import_jsx_runtime.jsxs)(Card, {
					className: "bg-sand",
					children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(CardHeader, {
						className: "pb-2",
						children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(CardTitle, {
							className: "text-lg flex items-center gap-2 text-slate/70",
							children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(LogIn, { className: "w-5 h-5 text-sage" }), " Total Logins"]
						})
					}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(CardContent, { children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
						className: "text-4xl font-black text-slate",
						children: totals.login_successes.toLocaleString()
					}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
						className: "text-xs text-slate/50 font-medium mt-1",
						children: "Last 30 days"
					})] })]
				}),
				/* @__PURE__ */ (0, import_jsx_runtime.jsxs)(Card, {
					className: "bg-sand",
					children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(CardHeader, {
						className: "pb-2",
						children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(CardTitle, {
							className: "text-lg flex items-center gap-2 text-slate/70",
							children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Users, { className: "w-5 h-5 text-ochre" }), " Registrations"]
						})
					}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(CardContent, { children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
						className: "text-4xl font-black text-slate",
						children: totals.registrations.toLocaleString()
					}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
						className: "text-xs text-slate/50 font-medium mt-1",
						children: "Last 30 days"
					})] })]
				}),
				/* @__PURE__ */ (0, import_jsx_runtime.jsxs)(Card, {
					className: "bg-sand",
					children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(CardHeader, {
						className: "pb-2",
						children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(CardTitle, {
							className: "text-lg flex items-center gap-2 text-slate/70",
							children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(CircleAlert, { className: "w-5 h-5 text-slate" }), " Active Users"]
						})
					}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(CardContent, { children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
						className: "text-4xl font-black text-slate",
						children: totals.active_users.toLocaleString()
					}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
						className: "text-xs text-slate/50 font-medium mt-1",
						children: "Distinct, last 30 days"
					})] })]
				})
			]
		}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
			className: "grid grid-cols-1 lg:grid-cols-3 gap-6",
			children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)(Card, {
				className: "lg:col-span-2 bg-sand shadow-[4px_4px_0px_rgba(30,41,59,1)] border-2 border-slate",
				children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(CardHeader, { children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(CardTitle, { children: "API Traffic" }) }), /* @__PURE__ */ (0, import_jsx_runtime.jsx)(CardContent, {
					className: "h-72",
					children: timeSeries.length === 0 ? /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
						className: "h-full flex items-center justify-center text-slate/40 font-medium",
						children: "No events yet — data will appear in real time."
					}) : /* @__PURE__ */ (0, import_jsx_runtime.jsx)(ResponsiveContainer, {
						width: "100%",
						height: "100%",
						children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(AreaChart, {
							data: timeSeries,
							margin: {
								top: 5,
								right: 10,
								bottom: 5,
								left: -20
							},
							children: [
								/* @__PURE__ */ (0, import_jsx_runtime.jsx)("defs", { children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("linearGradient", {
									id: "projColorRequests",
									x1: "0",
									y1: "0",
									x2: "0",
									y2: "1",
									children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("stop", {
										offset: "5%",
										stopColor: "#E07A5F",
										stopOpacity: .3
									}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("stop", {
										offset: "95%",
										stopColor: "#E07A5F",
										stopOpacity: 0
									})]
								}) }),
								/* @__PURE__ */ (0, import_jsx_runtime.jsx)(CartesianGrid, {
									stroke: "#3d405b",
									strokeDasharray: "5 5",
									opacity: .1
								}),
								/* @__PURE__ */ (0, import_jsx_runtime.jsx)(XAxis, {
									dataKey: "date",
									stroke: "#3d405b",
									tick: {
										fill: "#3d405b",
										fontWeight: 600
									},
									tickMargin: 10,
									fontSize: 11
								}),
								/* @__PURE__ */ (0, import_jsx_runtime.jsx)(YAxis, {
									stroke: "#3d405b",
									tick: {
										fill: "#3d405b",
										fontWeight: 600
									},
									fontSize: 11
								}),
								/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Tooltip, { ...TOOLTIP_STYLE }),
								/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Area, {
									type: "monotone",
									dataKey: "api_requests",
									name: "API Requests",
									stroke: "#E07A5F",
									strokeWidth: 3,
									fill: "url(#projColorRequests)",
									dot: { r: 3 },
									activeDot: { r: 5 }
								})
							]
						})
					})
				})]
			}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(Card, {
				className: "bg-sand shadow-[4px_4px_0px_rgba(30,41,59,1)] border-2 border-slate",
				children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(CardHeader, { children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(CardTitle, { children: "Auth Activity" }) }), /* @__PURE__ */ (0, import_jsx_runtime.jsx)(CardContent, {
					className: "h-72",
					children: timeSeries.length === 0 ? /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
						className: "h-full flex items-center justify-center text-slate/40 font-medium text-sm text-center",
						children: "No auth events yet."
					}) : /* @__PURE__ */ (0, import_jsx_runtime.jsx)(ResponsiveContainer, {
						width: "100%",
						height: "100%",
						children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(BarChart, {
							data: timeSeries,
							margin: {
								top: 5,
								right: 5,
								bottom: 5,
								left: -20
							},
							children: [
								/* @__PURE__ */ (0, import_jsx_runtime.jsx)(CartesianGrid, {
									stroke: "#3d405b",
									strokeDasharray: "5 5",
									opacity: .1
								}),
								/* @__PURE__ */ (0, import_jsx_runtime.jsx)(XAxis, {
									dataKey: "date",
									stroke: "#3d405b",
									fontSize: 10,
									tickLine: false
								}),
								/* @__PURE__ */ (0, import_jsx_runtime.jsx)(YAxis, {
									stroke: "#3d405b",
									fontSize: 10,
									tickLine: false
								}),
								/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Tooltip, {
									...TOOLTIP_STYLE,
									cursor: {
										fill: "#FAEED1",
										opacity: .5
									}
								}),
								/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Legend, { wrapperStyle: {
									fontSize: "11px",
									fontWeight: 700
								} }),
								/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Bar, {
									dataKey: "login_successes",
									name: "Logins",
									fill: "#81B29A",
									radius: [
										4,
										4,
										0,
										0
									]
								}),
								/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Bar, {
									dataKey: "registrations",
									name: "Registrations",
									fill: "#F2CC8F",
									radius: [
										4,
										4,
										0,
										0
									]
								}),
								/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Bar, {
									dataKey: "login_failures",
									name: "Failures",
									fill: "#E07A5F",
									radius: [
										4,
										4,
										0,
										0
									]
								})
							]
						})
					})
				})]
			})]
		})]
	});
}
//#endregion
export { AnalyticsTab as component };
