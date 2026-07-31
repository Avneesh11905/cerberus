import { t as useAuthStore } from "./_ssr/auth-E6d_NOW7.mjs";
import { n as apiClient } from "./_ssr/api-client-DJkUESpZ.mjs";
import { n as clsx } from "./_libs/class-variance-authority+clsx.mjs";
import { n as require_jsx_runtime } from "./_libs/@marsidev/react-turnstile+[...].mjs";
import { i as TooltipTrigger, n as TooltipContent, t as Tooltip$1 } from "./_ssr/tooltip-BgfWJfEU.mjs";
import { n as useAnalyticsStream, t as AnalyticsProvider } from "./_ssr/useAnalyticsStream-DpFV3Eam.mjs";
import { I as FolderKanban, M as LayoutDashboard, O as LogOut, S as RefreshCcw, d as Shield, et as ArrowRight, h as Settings, nt as Activity, r as Users, tt as ArrowLeft } from "./_libs/lucide-react.mjs";
import { a as ContextMenuTrigger, n as ContextMenuContent, r as ContextMenuItem, t as ContextMenu$1 } from "./_ssr/context-menu-Dw6tfCxT.mjs";
import { n as AvatarFallback, r as AvatarImage, t as Avatar } from "./_ssr/avatar-DnS6IaKa.mjs";
import { a as DropdownMenuSeparator, i as DropdownMenuLabel, n as DropdownMenuContent, o as DropdownMenuTrigger, r as DropdownMenuItem, t as DropdownMenu } from "./_ssr/dropdown-menu-BwIF-xpi.mjs";
import { _ as useNavigate, f as Outlet, g as Navigate, l as useLocation } from "./_libs/@tanstack/react-router+[...].mjs";
//#region node_modules/.nitro/vite/services/ssr/assets/_protected-DgSjx8C9.js
var import_jsx_runtime = require_jsx_runtime();
function StreamIndicator() {
	const status = useAnalyticsStream((state) => state.status);
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(Tooltip$1, { children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(TooltipTrigger, {
		asChild: true,
		children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
			className: "flex items-center gap-2 cursor-help",
			children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Activity, { className: "w-4 h-4 text-slate/50" }), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", { className: clsx("w-2.5 h-2.5 rounded-full shadow-[0_0_8px_rgba(0,0,0,0.2)]", status === "connected" ? "bg-sage" : status === "connecting" ? "bg-ochre animate-pulse" : "bg-terracotta") })]
		})
	}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)(TooltipContent, {
		side: "bottom",
		align: "center",
		children: status === "connected" ? "Live Stream Active" : status === "connecting" ? "Connecting..." : "Stream Disconnected"
	})] });
}
function Navbar() {
	const user = useAuthStore((state) => state.user);
	const logout = useAuthStore((state) => state.logout);
	const navigate = useNavigate();
	const location = useLocation();
	if (!user) return null;
	const handleLogout = async () => {
		try {
			await apiClient.post("/auth/logout");
		} catch (e) {
			console.error("Logout request failed", e);
		} finally {
			logout();
		}
	};
	const showStreamIndicator = location.pathname === "/dashboard" || location.pathname === "/superadmin" || location.pathname.startsWith("/superadmin/tenants/") && location.pathname.endsWith("/analytics");
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("header", {
		className: "h-16 bg-vanilla border-b-2 border-taupe/30 flex items-center justify-between px-6 shrink-0 z-50 relative",
		children: [
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
				className: "flex items-center flex-1",
				children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
					onClick: () => navigate({ to: "/dashboard" }),
					className: "text-xl font-display font-bold text-slate tracking-tight cursor-pointer",
					children: "Cerberus"
				})
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("nav", {
				className: "hidden md:flex items-center justify-center gap-8",
				children: [
					/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("span", {
						onClick: () => navigate({ to: "/dashboard" }),
						className: clsx("text-sm font-bold flex items-center gap-2 transition-colors cursor-pointer", location.pathname.startsWith("/dashboard") ? "text-slate" : "text-slate/70 hover:text-slate"),
						children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(LayoutDashboard, { className: "w-4 h-4" }), "Dashboard"]
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("span", {
						onClick: () => navigate({ to: "/projects" }),
						className: clsx("text-sm font-bold flex items-center gap-2 transition-colors cursor-pointer", location.pathname.startsWith("/projects") ? "text-slate" : "text-slate/70 hover:text-slate"),
						children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(FolderKanban, { className: "w-4 h-4" }), "Projects"]
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("span", {
						onClick: () => navigate({ to: "/users" }),
						className: clsx("text-sm font-bold flex items-center gap-2 transition-colors cursor-pointer", location.pathname.startsWith("/users") ? "text-slate" : "text-slate/70 hover:text-slate"),
						children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Users, { className: "w-4 h-4" }), "Global Users"]
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("span", {
						onClick: () => navigate({ to: "/settings" }),
						className: clsx("text-sm font-bold flex items-center gap-2 transition-colors cursor-pointer", location.pathname.startsWith("/settings") ? "text-slate" : "text-slate/70 hover:text-slate"),
						children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Settings, { className: "w-4 h-4" }), "Settings"]
					})
				]
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
				className: "flex items-center justify-end gap-6 flex-1",
				children: [showStreamIndicator && /* @__PURE__ */ (0, import_jsx_runtime.jsx)(StreamIndicator, {}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(DropdownMenu, { children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(DropdownMenuTrigger, {
					asChild: true,
					children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(Avatar, {
						className: "w-8 h-8 cursor-pointer hover:-translate-y-0.5 hover:-translate-x-0.5 transition-transform outline-none select-none",
						children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(AvatarImage, {
							src: user.picture || void 0,
							alt: "Profile",
							className: "select-none pointer-events-none"
						}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)(AvatarFallback, { children: ((typeof user.name === "string" ? user.name[0] : "") || user.email[0] || "U").toUpperCase() })]
					})
				}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(DropdownMenuContent, {
					align: "end",
					className: "w-56 mt-2",
					children: [
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)(DropdownMenuLabel, { children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
							className: "flex flex-col space-y-1",
							children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
								className: "text-sm font-medium leading-none text-slate",
								children: typeof user.name === "object" ? user.name.value || JSON.stringify(user.name) : user.name || "User"
							}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
								className: "text-xs leading-none text-slate/50",
								children: typeof user.email === "object" ? user.email.value || JSON.stringify(user.email) : user.email
							})]
						}) }),
						user.role === "SUPERADMIN" && /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(import_jsx_runtime.Fragment, { children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(DropdownMenuSeparator, {}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(DropdownMenuItem, {
							className: "text-ochre focus:text-ochre cursor-pointer",
							onClick: () => navigate({ to: "/superadmin" }),
							children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Shield, { className: "w-4 h-4 mr-2" }), "Superadmin"]
						})] }),
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)(DropdownMenuSeparator, {}),
						/* @__PURE__ */ (0, import_jsx_runtime.jsxs)(DropdownMenuItem, {
							className: "text-terracotta focus:text-vanilla focus:bg-terracotta cursor-pointer",
							onClick: handleLogout,
							children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(LogOut, { className: "w-4 h-4 mr-2" }), "Log out"]
						})
					]
				})] })]
			})
		]
	});
}
function ProtectedLayout() {
	const location = useLocation();
	if (!useAuthStore((state) => state.accessToken)) return /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Navigate, {
		to: "/login",
		search: { redirect: location.pathname }
	});
	let scope = "tenant";
	let projectId = void 0;
	if (location.pathname.startsWith("/superadmin")) scope = "system";
	else if (location.pathname.startsWith("/projects/") && !location.pathname.endsWith("/settings")) {
		const parts = location.pathname.split("/");
		if (parts.length >= 3 && parts[2] !== "") {
			scope = "project";
			projectId = parts[2];
		}
	}
	return /* @__PURE__ */ (0, import_jsx_runtime.jsx)(AnalyticsProvider, {
		scope,
		projectId,
		children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
			className: "fixed inset-0 bg-vanilla flex overflow-hidden",
			children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
				className: "flex-1 flex flex-col min-w-0",
				children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Navbar, {}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(ContextMenu$1, { children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(ContextMenuTrigger, {
					asChild: true,
					children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)("main", {
						className: "flex-1 overflow-y-auto bg-vanilla p-6 sm:p-8",
						children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Outlet, {})
					})
				}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(ContextMenuContent, {
					className: "w-56 bg-vanilla border-2 border-slate rounded-xl shadow-[4px_4px_0px_rgba(96,114,116,1)] p-1 z-[100]",
					children: [
						/* @__PURE__ */ (0, import_jsx_runtime.jsxs)(ContextMenuItem, {
							className: "font-bold cursor-pointer rounded-lg px-3 py-2 hover:bg-sand focus:bg-sand",
							onClick: () => window.history.back(),
							children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(ArrowLeft, { className: "w-4 h-4 mr-2" }), " Go Back"]
						}),
						/* @__PURE__ */ (0, import_jsx_runtime.jsxs)(ContextMenuItem, {
							className: "font-bold cursor-pointer rounded-lg px-3 py-2 hover:bg-sand focus:bg-sand",
							onClick: () => window.history.forward(),
							children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(ArrowRight, { className: "w-4 h-4 mr-2" }), " Go Forward"]
						}),
						/* @__PURE__ */ (0, import_jsx_runtime.jsxs)(ContextMenuItem, {
							className: "font-bold cursor-pointer rounded-lg px-3 py-2 hover:bg-sand focus:bg-sand",
							onClick: () => window.location.reload(),
							children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(RefreshCcw, { className: "w-4 h-4 mr-2" }), " Reload Page"]
						})
					]
				})] })]
			})
		})
	});
}
//#endregion
export { ProtectedLayout as component };
