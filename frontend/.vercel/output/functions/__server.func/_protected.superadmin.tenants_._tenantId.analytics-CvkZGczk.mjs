import { o as __toESM } from "./_runtime.mjs";
import { u as require_react } from "./_libs/@floating-ui/react-dom+[...].mjs";
import { n as apiClient } from "./_ssr/api-client-DJkUESpZ.mjs";
import { n as require_jsx_runtime } from "./_libs/@marsidev/react-turnstile+[...].mjs";
import { W as CircleAlert, k as LogIn, nt as Activity, r as Users, tt as ArrowLeft } from "./_libs/lucide-react.mjs";
import { y as useRouter } from "./_libs/@tanstack/react-router+[...].mjs";
import { t as Button } from "./_ssr/button-C-O_Pb_u.mjs";
import { a as XAxis, c as Line, f as ResponsiveContainer, i as YAxis, l as CartesianGrid, r as LineChart, u as Tooltip } from "./_libs/recharts+[...].mjs";
import { n as toast } from "./_libs/sonner.mjs";
import { a as CardHeader, n as CardContent, o as CardTitle, t as Card } from "./_ssr/card-D2S-3Lsc.mjs";
import { t as Route } from "./_protected.superadmin.tenants_._tenantId.analytics-CwINoZWC.mjs";
//#region node_modules/.nitro/vite/services/ssr/assets/_protected.superadmin.tenants_._tenantId.analytics-CvkZGczk.js
var import_react = /* @__PURE__ */ __toESM(require_react());
var import_jsx_runtime = require_jsx_runtime();
var getTenantAnalytics = async (tenantId, startDate, endDate) => {
	const params = new URLSearchParams();
	if (startDate) params.append("start_date", startDate);
	if (endDate) params.append("end_date", endDate);
	const query = params.toString() ? `?${params.toString()}` : "";
	const { data } = await apiClient.get(`/analytics/tenants/${tenantId}${query}`);
	return data.metrics;
};
function SuperadminTenantAnalyticsPage() {
	const { tenantId } = Route.useParams();
	const router = useRouter();
	const [metrics, setMetrics] = (0, import_react.useState)([]);
	const [loading, setLoading] = (0, import_react.useState)(true);
	(0, import_react.useEffect)(() => {
		const fetchData = async () => {
			setLoading(true);
			try {
				const metricsData = await getTenantAnalytics(tenantId);
				setMetrics(metricsData);
			} catch (err) {
				toast.error("Failed to load tenant analytics");
			} finally {
				setLoading(false);
			}
		};
		fetchData();
	}, [tenantId]);
	if (loading) return /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
		className: "flex items-center justify-center h-full min-h-100",
		children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Activity, { className: "w-8 h-8 animate-spin text-terracotta" })
	});
	const totalRequests = metrics.reduce((acc, curr) => acc + curr.api_requests, 0);
	const totalLogins = metrics.reduce((acc, curr) => acc + curr.login_successes, 0);
	const totalRegistrations = metrics.reduce((acc, curr) => acc + curr.registrations, 0);
	const activeUsers = metrics.length > 0 ? metrics[metrics.length - 1].active_users : 0;
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
		className: "max-w-7xl mx-auto flex flex-col gap-8 w-full",
		children: [
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
				className: "mb-6",
				children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(Button, {
					variant: "outline",
					onClick: () => router.navigate({ to: "/superadmin/tenants" }),
					className: "font-bold border-2",
					children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(ArrowLeft, { className: "w-4 h-4 mr-2" }), " Back to Tenants"]
				})
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
				className: "flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 border-b-2 border-slate/30 pb-6 mb-8",
				children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", { children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("h1", {
					className: "text-4xl font-display font-black tracking-tight text-slate",
					children: "Tenant Analytics"
				}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("p", {
					className: "text-slate/70 font-semibold mt-2 font-mono",
					children: ["ID: ", tenantId]
				})] })
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
				className: "grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8",
				children: [
					/* @__PURE__ */ (0, import_jsx_runtime.jsxs)(Card, {
						className: "bg-sand border-2 border-slate shadow-[4px_4px_0px_rgba(30,41,59,1)]",
						children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(CardHeader, {
							className: "pb-2",
							children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(CardTitle, {
								className: "text-lg flex items-center gap-2 text-slate/70",
								children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Activity, { className: "w-5 h-5 text-terracotta" }), " Total API Requests"]
							})
						}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)(CardContent, { children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
							className: "text-4xl font-black text-slate",
							children: totalRequests.toLocaleString()
						}) })]
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsxs)(Card, {
						className: "bg-sand border-2 border-slate shadow-[4px_4px_0px_rgba(30,41,59,1)]",
						children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(CardHeader, {
							className: "pb-2",
							children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(CardTitle, {
								className: "text-lg flex items-center gap-2 text-slate/70",
								children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(LogIn, { className: "w-5 h-5 text-sage" }), " Total Logins"]
							})
						}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)(CardContent, { children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
							className: "text-4xl font-black text-slate",
							children: totalLogins.toLocaleString()
						}) })]
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsxs)(Card, {
						className: "bg-sand border-2 border-slate shadow-[4px_4px_0px_rgba(30,41,59,1)]",
						children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(CardHeader, {
							className: "pb-2",
							children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(CardTitle, {
								className: "text-lg flex items-center gap-2 text-slate/70",
								children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Users, { className: "w-5 h-5 text-ochre" }), " Registrations"]
							})
						}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)(CardContent, { children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
							className: "text-4xl font-black text-slate",
							children: totalRegistrations.toLocaleString()
						}) })]
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsxs)(Card, {
						className: "bg-sand border-2 border-slate shadow-[4px_4px_0px_rgba(30,41,59,1)]",
						children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(CardHeader, {
							className: "pb-2",
							children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(CardTitle, {
								className: "text-lg flex items-center gap-2 text-slate/70",
								children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(CircleAlert, { className: "w-5 h-5 text-slate" }), " Active Users"]
							})
						}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)(CardContent, { children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
							className: "text-4xl font-black text-slate",
							children: activeUsers.toLocaleString()
						}) })]
					})
				]
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
				className: "grid grid-cols-1 gap-8",
				children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(Card, {
					className: "bg-sand h-125 flex flex-col border-2 border-slate shadow-[8px_8px_0px_rgba(30,41,59,1)]",
					children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(CardHeader, { children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(CardTitle, { children: "30-Day Activity" }) }), /* @__PURE__ */ (0, import_jsx_runtime.jsx)(CardContent, {
						className: "flex-1",
						children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(ResponsiveContainer, {
							width: "100%",
							height: "100%",
							children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(LineChart, {
								data: metrics,
								margin: {
									top: 5,
									right: 20,
									bottom: 5,
									left: 0
								},
								children: [
									/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Line, {
										type: "monotone",
										dataKey: "api_requests",
										stroke: "#E07A5F",
										strokeWidth: 3,
										dot: {
											r: 4,
											strokeWidth: 2
										},
										activeDot: { r: 6 },
										name: "API Requests"
									}),
									/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Line, {
										type: "monotone",
										dataKey: "login_successes",
										stroke: "#81B29A",
										strokeWidth: 3,
										dot: {
											r: 4,
											strokeWidth: 2
										},
										activeDot: { r: 6 },
										name: "Logins"
									}),
									/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Line, {
										type: "monotone",
										dataKey: "registrations",
										stroke: "#F2CC8F",
										strokeWidth: 3,
										dot: {
											r: 4,
											strokeWidth: 2
										},
										activeDot: { r: 6 },
										name: "Registrations"
									}),
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
										tickMargin: 10
									}),
									/* @__PURE__ */ (0, import_jsx_runtime.jsx)(YAxis, {
										stroke: "#3d405b",
										tick: {
											fill: "#3d405b",
											fontWeight: 600
										}
									}),
									/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Tooltip, {
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
									})
								]
							})
						})
					})]
				})
			})
		]
	});
}
//#endregion
export { SuperadminTenantAnalyticsPage as component };
