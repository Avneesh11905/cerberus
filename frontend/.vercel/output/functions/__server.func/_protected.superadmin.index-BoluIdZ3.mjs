import { n as require_jsx_runtime } from "./_libs/@marsidev/react-turnstile+[...].mjs";
import { n as useAnalyticsStream } from "./_ssr/useAnalyticsStream-DpFV3Eam.mjs";
import { F as Globe, I as FolderKanban, c as TrendingUp, k as LogIn, m as ShieldAlert, nt as Activity, r as Users } from "./_libs/lucide-react.mjs";
import { a as XAxis, d as Legend, f as ResponsiveContainer, i as YAxis, l as CartesianGrid, n as BarChart, o as Bar, s as Area, t as AreaChart, u as Tooltip } from "./_libs/recharts+[...].mjs";
import { a as CardHeader, n as CardContent, o as CardTitle, t as Card } from "./_ssr/card-D2S-3Lsc.mjs";
//#region node_modules/.nitro/vite/services/ssr/assets/_protected.superadmin.index-BoluIdZ3.js
var import_jsx_runtime = require_jsx_runtime();
var TOOLTIP_STYLE = {
	contentStyle: {
		backgroundColor: "#FAEED1",
		border: "2px solid #3d405b",
		borderRadius: "8px",
		color: "#3d405b",
		fontWeight: "bold",
		boxShadow: "4px 4px 0px rgba(61, 64, 91, 1)"
	},
	itemStyle: { color: "#3d405b" },
	labelStyle: {
		color: "#3d405b",
		fontWeight: 900,
		marginBottom: "4px"
	}
};
function StatCard({ title, value, sub, icon: Icon, accent = "#3d405b" }) {
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(Card, {
		className: "bg-sand border-2 border-slate shadow-[4px_4px_0px_rgba(30,41,59,1)]",
		children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)(CardHeader, {
			className: "flex flex-row items-center justify-between pb-2",
			children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(CardTitle, {
				className: "text-sm font-bold text-slate/60 uppercase tracking-wider",
				children: title
			}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Icon, {
				className: "w-4 h-4",
				style: { color: accent }
			})]
		}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(CardContent, { children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
			className: "text-3xl font-display font-bold text-slate",
			children: typeof value === "number" ? value.toLocaleString() : value
		}), sub && /* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
			className: "text-xs font-medium text-slate/50 mt-1",
			children: sub
		})] })]
	});
}
function SectionTitle({ children }) {
	return /* @__PURE__ */ (0, import_jsx_runtime.jsx)("h2", {
		className: "text-base font-bold text-slate/50 uppercase tracking-widest mt-2",
		children
	});
}
function EmptyChart({ loading }) {
	return /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
		className: "h-full flex items-center justify-center text-slate/30 font-medium text-sm",
		children: loading ? /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", { className: "animate-spin h-6 w-6 border-3 border-ochre border-t-transparent rounded-full" }) : "No data yet — will appear in real time."
	});
}
function SuperadminAnalyticsPage() {
	const data = useAnalyticsStream((state) => state.data);
	const status = useAnalyticsStream((state) => state.status);
	const isLoading = !data && status === "connecting";
	const pa = data?.platform_adoption;
	const eu = data?.end_user_usage;
	const ts = data?.timeSeries ?? [];
	const totalApiRequests = pa?.api_requests ?? 0;
	const totalLogins = pa?.login_successes ?? 0;
	const totalFailures = pa?.login_failures ?? 0;
	const totalAttempts = totalLogins + totalFailures;
	const errorRate = totalAttempts > 0 ? (totalFailures / totalAttempts * 100).toFixed(1) + "%" : "0.0%";
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
		className: "max-w-7xl mx-auto flex flex-col gap-8 w-full",
		children: [
			/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", { children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("h1", {
				className: "text-2xl font-display font-bold text-slate",
				children: "System Analytics"
			}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
				className: "text-sm font-medium text-slate/50 mt-1",
				children: "Platform-wide live data · all figures from real events"
			})] }),
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)(SectionTitle, { children: "Platform Adoption" }),
			/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
				className: "grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4",
				children: [
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)(StatCard, {
						title: "Tenants",
						value: pa?.total_tenants ?? 0,
						sub: "All time",
						icon: Globe,
						accent: "#E07A5F"
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)(StatCard, {
						title: "Projects",
						value: eu?.total_projects ?? 0,
						sub: "All time",
						icon: FolderKanban,
						accent: "#81B29A"
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)(StatCard, {
						title: "Total Users",
						value: pa?.registrations ?? 0,
						sub: "Registered all time",
						icon: Users,
						accent: "#F2CC8F"
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)(StatCard, {
						title: "Active Users",
						value: pa?.active_users ?? 0,
						sub: "Distinct, last 30d",
						icon: TrendingUp,
						accent: "#3d405b"
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)(StatCard, {
						title: "Total Logins",
						value: totalLogins,
						sub: "Tenant + project, all time",
						icon: LogIn,
						accent: "#81B29A"
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)(StatCard, {
						title: "Error Rate",
						value: errorRate,
						sub: "Login failures / requests",
						icon: ShieldAlert,
						accent: "#E07A5F"
					})
				]
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)(SectionTitle, { children: "End-User Activity" }),
			/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
				className: "grid grid-cols-2 md:grid-cols-4 gap-4",
				children: [
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)(StatCard, {
						title: "API Requests",
						value: totalApiRequests,
						sub: "All projects, all time",
						icon: Activity,
						accent: "#E07A5F"
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)(StatCard, {
						title: "Login Failures",
						value: totalFailures,
						sub: "All projects, all time",
						icon: ShieldAlert,
						accent: "#E07A5F"
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)(StatCard, {
						title: "Project Registrations",
						value: eu?.registrations ?? 0,
						sub: "Users in projects",
						icon: Users,
						accent: "#F2CC8F"
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)(StatCard, {
						title: "Project API Hits",
						value: eu?.api_requests ?? 0,
						sub: "From live_project_metrics",
						icon: Activity,
						accent: "#3d405b"
					})
				]
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)(SectionTitle, { children: "Trends — Last 30 Days" }),
			/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
				className: "grid grid-cols-1 lg:grid-cols-3 gap-6",
				children: [
					/* @__PURE__ */ (0, import_jsx_runtime.jsxs)(Card, {
						className: "lg:col-span-2 bg-sand border-2 border-slate shadow-[4px_4px_0px_rgba(30,41,59,1)]",
						children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(CardHeader, { children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(CardTitle, {
							className: "text-base",
							children: "API Traffic"
						}) }), /* @__PURE__ */ (0, import_jsx_runtime.jsx)(CardContent, {
							className: "h-64",
							children: ts.length === 0 ? /* @__PURE__ */ (0, import_jsx_runtime.jsx)(EmptyChart, { loading: isLoading }) : /* @__PURE__ */ (0, import_jsx_runtime.jsx)(ResponsiveContainer, {
								width: "100%",
								height: "100%",
								children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(AreaChart, {
									data: ts,
									margin: {
										top: 5,
										right: 10,
										bottom: 0,
										left: -20
									},
									children: [
										/* @__PURE__ */ (0, import_jsx_runtime.jsx)("defs", { children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("linearGradient", {
											id: "gApi",
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
											strokeDasharray: "3 3",
											stroke: "#3d405b",
											opacity: .1,
											vertical: false
										}),
										/* @__PURE__ */ (0, import_jsx_runtime.jsx)(XAxis, {
											dataKey: "date",
											fontSize: 10,
											tickLine: false,
											axisLine: false,
											stroke: "#3d405b"
										}),
										/* @__PURE__ */ (0, import_jsx_runtime.jsx)(YAxis, {
											fontSize: 10,
											tickLine: false,
											axisLine: false,
											stroke: "#3d405b"
										}),
										/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Tooltip, { ...TOOLTIP_STYLE }),
										/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Area, {
											type: "monotone",
											dataKey: "api_requests",
											name: "API Requests",
											stroke: "#E07A5F",
											strokeWidth: 2.5,
											fill: "url(#gApi)"
										})
									]
								})
							})
						})]
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsxs)(Card, {
						className: "bg-sand border-2 border-slate shadow-[4px_4px_0px_rgba(30,41,59,1)]",
						children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(CardHeader, { children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(CardTitle, {
							className: "text-base",
							children: "Auth Activity"
						}) }), /* @__PURE__ */ (0, import_jsx_runtime.jsx)(CardContent, {
							className: "h-64",
							children: ts.length === 0 ? /* @__PURE__ */ (0, import_jsx_runtime.jsx)(EmptyChart, { loading: isLoading }) : /* @__PURE__ */ (0, import_jsx_runtime.jsx)(ResponsiveContainer, {
								width: "100%",
								height: "100%",
								children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(BarChart, {
									data: ts,
									margin: {
										top: 5,
										right: 5,
										bottom: 0,
										left: -20
									},
									children: [
										/* @__PURE__ */ (0, import_jsx_runtime.jsx)(CartesianGrid, {
											strokeDasharray: "3 3",
											stroke: "#3d405b",
											opacity: .1,
											vertical: false
										}),
										/* @__PURE__ */ (0, import_jsx_runtime.jsx)(XAxis, {
											dataKey: "date",
											fontSize: 9,
											tickLine: false,
											axisLine: false,
											stroke: "#3d405b"
										}),
										/* @__PURE__ */ (0, import_jsx_runtime.jsx)(YAxis, {
											fontSize: 9,
											tickLine: false,
											axisLine: false,
											stroke: "#3d405b"
										}),
										/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Tooltip, {
											...TOOLTIP_STYLE,
											cursor: {
												fill: "#FAEED1",
												opacity: .4
											}
										}),
										/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Legend, { wrapperStyle: {
											fontSize: "10px",
											fontWeight: 700
										} }),
										/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Bar, {
											dataKey: "login_successes",
											name: "Logins",
											fill: "#81B29A",
											radius: [
												3,
												3,
												0,
												0
											]
										}),
										/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Bar, {
											dataKey: "registrations",
											name: "Registrations",
											fill: "#F2CC8F",
											radius: [
												3,
												3,
												0,
												0
											]
										}),
										/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Bar, {
											dataKey: "login_failures",
											name: "Failures",
											fill: "#E07A5F",
											radius: [
												3,
												3,
												0,
												0
											]
										})
									]
								})
							})
						})]
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsxs)(Card, {
						className: "bg-sand border-2 border-slate shadow-[4px_4px_0px_rgba(30,41,59,1)]",
						children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(CardHeader, { children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(CardTitle, {
							className: "text-base",
							children: "Emails Sent"
						}) }), /* @__PURE__ */ (0, import_jsx_runtime.jsx)(CardContent, {
							className: "h-64",
							children: ts.length === 0 ? /* @__PURE__ */ (0, import_jsx_runtime.jsx)(EmptyChart, { loading: isLoading }) : /* @__PURE__ */ (0, import_jsx_runtime.jsx)(ResponsiveContainer, {
								width: "100%",
								height: "100%",
								children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(AreaChart, {
									data: ts,
									margin: {
										top: 5,
										right: 10,
										bottom: 0,
										left: -20
									},
									children: [
										/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("defs", { children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("linearGradient", {
											id: "gEmail",
											x1: "0",
											y1: "0",
											x2: "0",
											y2: "1",
											children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("stop", {
												offset: "5%",
												stopColor: "#81B29A",
												stopOpacity: .3
											}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("stop", {
												offset: "95%",
												stopColor: "#81B29A",
												stopOpacity: 0
											})]
										}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("linearGradient", {
											id: "gEmailFail",
											x1: "0",
											y1: "0",
											x2: "0",
											y2: "1",
											children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("stop", {
												offset: "5%",
												stopColor: "#E07A5F",
												stopOpacity: .2
											}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("stop", {
												offset: "95%",
												stopColor: "#E07A5F",
												stopOpacity: 0
											})]
										})] }),
										/* @__PURE__ */ (0, import_jsx_runtime.jsx)(CartesianGrid, {
											strokeDasharray: "3 3",
											stroke: "#3d405b",
											opacity: .1,
											vertical: false
										}),
										/* @__PURE__ */ (0, import_jsx_runtime.jsx)(XAxis, {
											dataKey: "date",
											fontSize: 10,
											tickLine: false,
											axisLine: false,
											stroke: "#3d405b"
										}),
										/* @__PURE__ */ (0, import_jsx_runtime.jsx)(YAxis, {
											fontSize: 10,
											tickLine: false,
											axisLine: false,
											stroke: "#3d405b"
										}),
										/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Tooltip, { ...TOOLTIP_STYLE }),
										/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Legend, { wrapperStyle: {
											fontSize: "10px",
											fontWeight: 700
										} }),
										/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Area, {
											type: "monotone",
											dataKey: "emails_sent",
											name: "Sent",
											stroke: "#81B29A",
											strokeWidth: 2,
											fill: "url(#gEmail)"
										}),
										/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Area, {
											type: "monotone",
											dataKey: "emails_failed",
											name: "Failed",
											stroke: "#E07A5F",
											strokeWidth: 2,
											fill: "url(#gEmailFail)"
										})
									]
								})
							})
						})]
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsxs)(Card, {
						className: "lg:col-span-2 bg-sand border-2 border-slate shadow-[4px_4px_0px_rgba(30,41,59,1)]",
						children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(CardHeader, { children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(CardTitle, {
							className: "text-base",
							children: "Growth — Projects Created & Active Users"
						}) }), /* @__PURE__ */ (0, import_jsx_runtime.jsx)(CardContent, {
							className: "h-64",
							children: ts.length === 0 ? /* @__PURE__ */ (0, import_jsx_runtime.jsx)(EmptyChart, { loading: isLoading }) : /* @__PURE__ */ (0, import_jsx_runtime.jsx)(ResponsiveContainer, {
								width: "100%",
								height: "100%",
								children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(AreaChart, {
									data: ts,
									margin: {
										top: 5,
										right: 10,
										bottom: 0,
										left: -20
									},
									children: [
										/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("defs", { children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("linearGradient", {
											id: "gProj",
											x1: "0",
											y1: "0",
											x2: "0",
											y2: "1",
											children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("stop", {
												offset: "5%",
												stopColor: "#F2CC8F",
												stopOpacity: .4
											}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("stop", {
												offset: "95%",
												stopColor: "#F2CC8F",
												stopOpacity: 0
											})]
										}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("linearGradient", {
											id: "gActive",
											x1: "0",
											y1: "0",
											x2: "0",
											y2: "1",
											children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("stop", {
												offset: "5%",
												stopColor: "#3d405b",
												stopOpacity: .2
											}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("stop", {
												offset: "95%",
												stopColor: "#3d405b",
												stopOpacity: 0
											})]
										})] }),
										/* @__PURE__ */ (0, import_jsx_runtime.jsx)(CartesianGrid, {
											strokeDasharray: "3 3",
											stroke: "#3d405b",
											opacity: .1,
											vertical: false
										}),
										/* @__PURE__ */ (0, import_jsx_runtime.jsx)(XAxis, {
											dataKey: "date",
											fontSize: 10,
											tickLine: false,
											axisLine: false,
											stroke: "#3d405b"
										}),
										/* @__PURE__ */ (0, import_jsx_runtime.jsx)(YAxis, {
											fontSize: 10,
											tickLine: false,
											axisLine: false,
											stroke: "#3d405b"
										}),
										/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Tooltip, { ...TOOLTIP_STYLE }),
										/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Legend, { wrapperStyle: {
											fontSize: "10px",
											fontWeight: 700
										} }),
										/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Area, {
											type: "monotone",
											dataKey: "projects_created",
											name: "Projects Created",
											stroke: "#F2CC8F",
											strokeWidth: 2,
											fill: "url(#gProj)"
										}),
										/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Area, {
											type: "monotone",
											dataKey: "active_users",
											name: "Active Users",
											stroke: "#3d405b",
											strokeWidth: 2,
											fill: "url(#gActive)"
										})
									]
								})
							})
						})]
					})
				]
			})
		]
	});
}
//#endregion
export { SuperadminAnalyticsPage as component };
