import "./_runtime.mjs";
import { u as require_react } from "./_libs/@floating-ui/react-dom+[...].mjs";
import { n as require_jsx_runtime } from "./_libs/@marsidev/react-turnstile+[...].mjs";
import { n as useAnalyticsStream } from "./_ssr/useAnalyticsStream-DpFV3Eam.mjs";
import { I as FolderKanban, k as LogIn, m as ShieldAlert, nt as Activity, r as Users, tt as ArrowLeft } from "./_libs/lucide-react.mjs";
import { _ as useNavigate, y as useRouter } from "./_libs/@tanstack/react-router+[...].mjs";
import { t as Button } from "./_ssr/button-C-O_Pb_u.mjs";
import { a as XAxis, d as Legend, f as ResponsiveContainer, i as YAxis, l as CartesianGrid, n as BarChart, o as Bar, s as Area, t as AreaChart, u as Tooltip } from "./_libs/recharts+[...].mjs";
require_react();
var import_jsx_runtime = require_jsx_runtime();
function StatCard({ title, value, icon: Icon, subtitle }) {
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
		className: "bg-sand rounded-xl border-2 border-slate p-6 shadow-[4px_4px_0px_rgba(30,41,59,1)] flex flex-col",
		children: [
			/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
				className: "flex justify-between items-start mb-4",
				children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("h3", {
					className: "text-slate font-bold",
					children: title
				}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
					className: "p-2 bg-taupe/10 rounded-lg border-2 border-slate",
					children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Icon, { className: "w-5 h-5 text-slate" })
				})]
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
				className: "text-3xl font-display font-bold text-slate mb-1",
				children: typeof value === "number" ? value.toLocaleString() : value
			}),
			subtitle && /* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
				className: "text-sm font-medium text-slate/50",
				children: subtitle
			})
		]
	});
}
function DashboardPage() {
	const data = useAnalyticsStream((state) => state.data);
	const status = useAnalyticsStream((state) => state.status);
	const navigate = useNavigate();
	const router = useRouter();
	if (!data && status === "connecting") return /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
		className: "flex flex-col items-center justify-center p-8 space-y-4 h-full",
		children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", { className: "animate-spin h-10 w-10 border-4 border-slate border-t-transparent rounded-full" })
	});
	const totals = data?.totals;
	const timeSeries = data?.timeSeries ?? [];
	const errorRate = totals && totals.api_requests > 0 ? (totals.login_failures / totals.api_requests * 100).toFixed(1) + "%" : "0%";
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
		className: "max-w-7xl mx-auto flex flex-col gap-8 w-full",
		children: [
			/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
				className: "flex justify-between items-end",
				children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
					className: "flex items-center gap-4",
					children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Button, {
						variant: "outline",
						size: "icon",
						className: "border-2 border-slate w-10 h-10 rounded-xl",
						onClick: () => router.navigate({ to: "/" }),
						children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(ArrowLeft, { className: "w-5 h-5 text-slate" })
					}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", { children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("h1", {
						className: "text-3xl font-display font-bold text-slate mb-2",
						children: "Dashboard Overview"
					}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
						className: "text-slate/70 font-medium",
						children: "Real-time metrics for your infrastructure — last 30 days."
					})] })]
				}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(Button, {
					variant: "primary",
					onClick: () => navigate({ to: "/projects" }),
					className: "hidden sm:flex items-center gap-2",
					children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(FolderKanban, { className: "w-4 h-4" }), "View Projects"]
				})]
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
				className: "grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6",
				children: [
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)(StatCard, {
						title: "Total API Requests",
						value: totals?.api_requests ?? 0,
						icon: Activity,
						subtitle: "Last 30 days"
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)(StatCard, {
						title: "Active Users",
						value: totals?.active_users ?? 0,
						icon: Users,
						subtitle: "Distinct users, last 30d"
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)(StatCard, {
						title: "Total Logins",
						value: totals?.login_successes ?? 0,
						icon: LogIn,
						subtitle: "Last 30 days"
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)(StatCard, {
						title: "Error Rate",
						value: errorRate,
						icon: ShieldAlert,
						subtitle: "Login failures / requests"
					})
				]
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
				className: "grid grid-cols-1 lg:grid-cols-3 gap-6",
				children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
					className: "lg:col-span-2 bg-sand rounded-xl border-2 border-slate p-6 shadow-[4px_4px_0px_rgba(30,41,59,1)]",
					children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("h2", {
						className: "text-xl font-bold text-slate mb-6",
						children: "API Traffic — Last 30 Days"
					}), timeSeries.length === 0 ? /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
						className: "h-80 flex items-center justify-center text-slate/40 font-medium",
						children: "No data yet — events will appear here in real time."
					}) : /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
						className: "h-80 w-full",
						children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(ResponsiveContainer, {
							width: "100%",
							height: "100%",
							children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(AreaChart, {
								data: timeSeries,
								margin: {
									top: 10,
									right: 10,
									left: -20,
									bottom: 0
								},
								children: [
									/* @__PURE__ */ (0, import_jsx_runtime.jsx)("defs", { children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("linearGradient", {
										id: "colorRequests",
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
										vertical: false
									}),
									/* @__PURE__ */ (0, import_jsx_runtime.jsx)(XAxis, {
										dataKey: "date",
										stroke: "#3d405b",
										fontSize: 12,
										tickLine: false,
										axisLine: false
									}),
									/* @__PURE__ */ (0, import_jsx_runtime.jsx)(YAxis, {
										stroke: "#3d405b",
										fontSize: 12,
										tickLine: false,
										axisLine: false
									}),
									/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Tooltip, {
										contentStyle: {
											backgroundColor: "#FAEED1",
											border: "2px solid #3d405b",
											borderRadius: "8px",
											color: "#3d405b",
											fontWeight: "bold",
											boxShadow: "4px 4px 0px rgba(61, 64, 91, 1)"
										},
										itemStyle: { color: "#3d405b" }
									}),
									/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Area, {
										type: "monotone",
										dataKey: "api_requests",
										name: "API Requests",
										stroke: "#E07A5F",
										strokeWidth: 3,
										fillOpacity: 1,
										fill: "url(#colorRequests)"
									})
								]
							})
						})
					})]
				}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
					className: "bg-sand rounded-xl border-2 border-slate p-6 shadow-[4px_4px_0px_rgba(30,41,59,1)]",
					children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("h2", {
						className: "text-xl font-bold text-slate mb-6",
						children: "Auth Activity"
					}), timeSeries.length === 0 ? /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
						className: "h-80 flex items-center justify-center text-slate/40 font-medium text-center text-sm",
						children: "No auth events yet."
					}) : /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
						className: "h-80 w-full",
						children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(ResponsiveContainer, {
							width: "100%",
							height: "100%",
							children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(BarChart, {
								data: timeSeries,
								margin: {
									top: 0,
									right: 0,
									left: -20,
									bottom: 0
								},
								children: [
									/* @__PURE__ */ (0, import_jsx_runtime.jsx)(CartesianGrid, {
										strokeDasharray: "3 3",
										stroke: "#3d405b",
										vertical: false
									}),
									/* @__PURE__ */ (0, import_jsx_runtime.jsx)(XAxis, {
										dataKey: "date",
										stroke: "#3d405b",
										fontSize: 10,
										tickLine: false,
										axisLine: false
									}),
									/* @__PURE__ */ (0, import_jsx_runtime.jsx)(YAxis, {
										stroke: "#3d405b",
										fontSize: 10,
										tickLine: false,
										axisLine: false
									}),
									/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Tooltip, {
										cursor: {
											fill: "#FAEED1",
											opacity: .5
										},
										contentStyle: {
											backgroundColor: "#FAEED1",
											border: "2px solid #3d405b",
											borderRadius: "8px",
											color: "#3d405b",
											fontWeight: "bold",
											boxShadow: "4px 4px 0px rgba(61, 64, 91, 1)"
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
			})
		]
	});
}
//#endregion
export { DashboardPage as component };
