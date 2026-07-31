import "../_runtime.mjs";
import { u as require_react } from "../_libs/@floating-ui/react-dom+[...].mjs";
import { t as useAuthStore } from "./auth-E6d_NOW7.mjs";
import { a as refreshClient } from "./api-client-DJkUESpZ.mjs";
import { n as require_jsx_runtime } from "../_libs/@marsidev/react-turnstile+[...].mjs";
import { r as TooltipProvider } from "./tooltip-BgfWJfEU.mjs";
import { A as LoaderCircle, E as OctagonX, P as Info, U as CircleCheck, s as TriangleAlert } from "../_libs/lucide-react.mjs";
import { c as HeadContent, d as createRouter, f as Outlet, h as createRootRouteWithContext, j as redirect, m as createFileRoute, p as lazyRouteComponent, s as Scripts } from "../_libs/@tanstack/react-router+[...].mjs";
import { t as Button } from "./button-C-O_Pb_u.mjs";
import { t as Route$15 } from "../_protected.projects._projectId-BPJOfHyM.mjs";
import { t as Toaster } from "../_libs/sonner.mjs";
import { t as Route$16 } from "../_protected.projects._projectId.analytics-DglSHjUP.mjs";
import { t as Route$17 } from "../_protected.projects._projectId.auth-CfTLHld9.mjs";
import { t as Route$18 } from "../_protected.projects._projectId.claims-Bd_s5v_j.mjs";
import { i as object, o as string, r as literal } from "../_libs/zod.mjs";
import { t as Route$19 } from "../_protected.projects._projectId.general-BJh6gl1U.mjs";
import { t as Route$20 } from "../_protected.projects._projectId.security-DTa62ddj.mjs";
import { t as Route$21 } from "../_protected.projects._projectId.users-AA0wXr8R.mjs";
import { t as QueryClient } from "../_libs/tanstack__query-core.mjs";
import { r as QueryClientProvider } from "../_libs/tanstack__react-query.mjs";
import { t as Route$22 } from "../_protected.superadmin.tenants_._tenantId.analytics-CwINoZWC.mjs";
import { t as Route$23 } from "./login-Ch1kjSMw.mjs";
import { t as Route$24 } from "./oauth.callback-BOz15k1E.mjs";
import { t as Route$25 } from "./reset-password-Ds7fBS4O.mjs";
import { i as gsapWithCSS, n as ScrollTrigger, r as Observer, t as ScrollToPlugin } from "../_libs/gsap.mjs";
require_react();
var import_jsx_runtime = require_jsx_runtime();
var Toaster$1 = ({ ...props }) => {
	return /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Toaster, {
		className: "toaster group",
		toastOptions: { classNames: {
			toast: "group toast !bg-vanilla !text-slate !border-2 !border-slate !shadow-[4px_4px_0px_rgba(30,41,59,1)] !font-bold !rounded-xl",
			description: "text-slate/70 font-semibold",
			actionButton: "bg-slate text-vanilla border-2 border-transparent hover:shadow-[2px_2px_0px_rgba(178,165,155,1)]",
			cancelButton: "bg-taupe text-vanilla",
			closeButton: "left-auto right-0 translate-x-[35%] -translate-y-[35%]"
		} },
		icons: {
			success: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(CircleCheck, { className: "size-4 text-sage" }),
			info: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Info, { className: "size-4 text-slate" }),
			warning: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(TriangleAlert, { className: "size-4 text-ochre" }),
			error: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(OctagonX, { className: "size-4 text-terracotta" }),
			loading: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(LoaderCircle, { className: "size-4 animate-spin text-slate" })
		},
		style: {
			"--normal-bg": "var(--warm-sand)",
			"--normal-text": "var(--slate)",
			"--normal-border": "var(--slate)",
			"--border-radius": "0.75rem",
			"--toast-svg-margin-start": "0.5rem",
			"--toast-svg-margin-end": "0.75rem"
		},
		...props
	});
};
var styles_default = "/assets/styles-B940DYyj.css";
var sessionCheckPromise = null;
var checkInitialSession = () => {
	if (typeof window === "undefined") return Promise.resolve(null);
	if (sessionCheckPromise) return sessionCheckPromise;
	sessionCheckPromise = refreshClient.post("/auth/refresh").then((res) => {
		if (res.data.access_token) {
			if (res.data.user) useAuthStore.getState().setAuth(res.data.access_token, res.data.csrf_token, res.data.user);
			else useAuthStore.getState().setAccessToken(res.data.access_token, res.data.csrf_token);
			return res.data.access_token;
		}
		return null;
	}).catch((err) => {
		if (err?.response?.status === 401) useAuthStore.getState().logout();
		return null;
	}).finally(() => {
		sessionCheckPromise = null;
	});
	return sessionCheckPromise;
};
var Route$14 = createRootRouteWithContext()({
	head: () => ({
		meta: [
			{ charSet: "utf-8" },
			{
				name: "viewport",
				content: "width=device-width, initial-scale=1"
			},
			{ title: "Cerberus" }
		],
		links: [{
			rel: "stylesheet",
			href: styles_default
		}, {
			rel: "icon",
			type: "image/x-icon",
			href: "/favicon.ico"
		}]
	}),
	beforeLoad: async () => {
		await checkInitialSession();
	},
	errorComponent: ({ error }) => {
		console.error("Root Error Boundary caught:", error);
		return /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
			className: "min-h-screen bg-vanilla flex flex-col items-center justify-center p-4",
			children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
				className: "flat-card p-8 rounded-xl bg-sand border-taupe text-center max-w-md w-full",
				children: [
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)("h1", {
						className: "text-3xl font-display font-bold text-terracotta mb-4",
						children: "Something went wrong"
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
						className: "text-slate/70 font-medium text-sm mb-8",
						children: error.message || "An unexpected error occurred."
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Button, {
						onClick: () => window.location.href = "/",
						children: "Return Home"
					})
				]
			})
		});
	},
	component: RootComponent,
	notFoundComponent: () => /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
		className: "min-h-screen bg-vanilla flex flex-col items-center justify-center p-4",
		children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
			className: "flat-card p-8 rounded-xl bg-sand border-taupe text-center max-w-md w-full",
			children: [
				/* @__PURE__ */ (0, import_jsx_runtime.jsx)("h1", {
					className: "text-6xl font-display font-bold text-slate mb-4",
					children: "404"
				}),
				/* @__PURE__ */ (0, import_jsx_runtime.jsx)("h2", {
					className: "text-xl font-bold text-slate mb-2",
					children: "Page Not Found"
				}),
				/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
					className: "text-slate/70 font-medium text-sm mb-8",
					children: "We couldn't find the page you were looking for."
				}),
				/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Button, {
					onClick: () => window.location.href = "/",
					children: "Return Home"
				})
			]
		})
	}),
	pendingComponent: () => /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
		className: "min-h-screen bg-vanilla flex flex-col items-center justify-center p-4",
		children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", { className: "w-16 h-16 border-4 border-taupe border-t-terracotta rounded-full animate-spin" })
	})
});
function RootComponent() {
	const queryClient = Route$14.useRouteContext({ select: (ctx) => ctx.queryClient });
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("html", {
		lang: "en",
		className: "snap-y snap-proximity scroll-smooth",
		children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("head", { children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(HeadContent, {}) }), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("body", { children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(QueryClientProvider, {
			client: queryClient,
			children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(TooltipProvider, {
				delayDuration: 100,
				children: [
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Outlet, {}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Toaster$1, {
						position: "bottom-right",
						toastOptions: {
							className: "bg-vanilla border-2 border-slate text-slate font-bold shadow-[4px_4px_0px_var(--taupe)] rounded-xl",
							duration: 4e3
						}
					}),
					false
				]
			})
		}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Scripts, {})] })]
	});
}
var $$splitComponentImporter$12 = () => import("./routes-B07XWKmY.mjs");
gsapWithCSS.registerPlugin(ScrollTrigger, Observer, ScrollToPlugin);
var Route$13 = createFileRoute("/")({ component: lazyRouteComponent($$splitComponentImporter$12, "component") });
function isTokenExpired(token) {
	if (!token) return true;
	try {
		const payloadBase64 = token.split(".")[1];
		if (!payloadBase64) return true;
		const base64 = payloadBase64.replace(/-/g, "+").replace(/_/g, "/");
		const decodedJson = atob(base64);
		const payload = JSON.parse(decodedJson);
		if (!payload.exp) return false;
		const expTime = payload.exp * 1e3;
		return Date.now() >= expTime - 1e4;
	} catch (e) {
		return true;
	}
}
var $$splitComponentImporter$11 = () => import("../_protected-DgSjx8C9.mjs");
var Route$12 = createFileRoute("/_protected")({
	beforeLoad: async ({ location }) => {
		if (typeof window === "undefined") return;
		const accessToken = useAuthStore.getState().accessToken;
		let isValid = !!accessToken;
		if (accessToken && isTokenExpired(accessToken)) try {
			const csrfToken = useAuthStore.getState().csrfToken;
			const { data } = await refreshClient.post("/auth/refresh", {}, { headers: csrfToken ? { "X-CSRF": csrfToken } : void 0 });
			const newAccessToken = data.access_token;
			const newCsrfToken = data.csrf_token;
			if (data.user) useAuthStore.getState().setAuth(newAccessToken, newCsrfToken || "", data.user);
			else useAuthStore.getState().setAccessToken(newAccessToken, newCsrfToken);
			isValid = true;
		} catch (err) {
			useAuthStore.getState().logout();
			isValid = false;
		}
		if (!isValid) throw redirect({
			to: "/login",
			search: { redirect: location.href }
		});
	},
	component: lazyRouteComponent($$splitComponentImporter$11, "component")
});
var $$splitComponentImporter$10 = () => import("./forgot-password-CB0AD5xL.mjs");
var Route$11 = createFileRoute("/forgot-password")({
	beforeLoad: () => {
		if (typeof window === "undefined") return;
		const { accessToken } = useAuthStore.getState();
		if (accessToken) throw redirect({ to: "/" });
	},
	component: lazyRouteComponent($$splitComponentImporter$10, "component")
});
object({ email: string().email("Please enter a valid email address") });
var $$splitComponentImporter$9 = () => import("./register-CnC6cICi.mjs");
var Route$10 = createFileRoute("/register")({
	beforeLoad: () => {
		if (typeof window === "undefined") return;
		if (useAuthStore.getState().accessToken) throw redirect({ to: "/" });
	},
	component: lazyRouteComponent($$splitComponentImporter$9, "component")
});
object({
	name: string().min(2, "Name must be at least 2 characters"),
	email: string().email("Please enter a valid email address"),
	password: string().min(8, "Password must be at least 8 characters"),
	confirmPassword: string()
}).refine((data) => data.password === data.confirmPassword, {
	message: "Passwords don't match",
	path: ["confirmPassword"]
});
var $$splitComponentImporter$8 = () => import("./verify-email-CU58ylmg.mjs");
var Route$9 = createFileRoute("/verify-email")({
	beforeLoad: () => {
		const state = useAuthStore.getState();
		if (state.accessToken) throw redirect({ to: "/" });
		if (!state.unverifiedEmail) throw redirect({ to: "/register" });
	},
	component: lazyRouteComponent($$splitComponentImporter$8, "component")
});
object({
	email: string().email("Please enter a valid email address"),
	token: string().length(6, "Token must be exactly 6 digits")
});
var $$splitComponentImporter$7 = () => import("../_protected.dashboard-DjSJD6tZ.mjs");
var Route$8 = createFileRoute("/_protected/dashboard")({ component: lazyRouteComponent($$splitComponentImporter$7, "component") });
var $$splitComponentImporter$6 = () => import("../_protected.settings-DZMdY-LW.mjs");
var Route$7 = createFileRoute("/_protected/settings")({ component: lazyRouteComponent($$splitComponentImporter$6, "component") });
object({
	name: string().min(1, "Name is required"),
	picture: string().url("Must be a valid URL").optional().or(literal(""))
});
var $$splitComponentImporter$5 = () => import("../_protected.superadmin-DT4y2gLB.mjs");
var Route$6 = createFileRoute("/_protected/superadmin")({
	beforeLoad: () => {
		if (typeof window === "undefined") return;
		if (useAuthStore.getState().user?.role !== "SUPERADMIN") throw redirect({ to: "/dashboard" });
	},
	component: lazyRouteComponent($$splitComponentImporter$5, "component")
});
var $$splitComponentImporter$4 = () => import("../_protected.projects.index-j3CKepSx.mjs");
var Route$5 = createFileRoute("/_protected/projects/")({ component: lazyRouteComponent($$splitComponentImporter$4, "component") });
var $$splitComponentImporter$3 = () => import("../_protected.superadmin.index-BoluIdZ3.mjs");
var Route$4 = createFileRoute("/_protected/superadmin/")({ component: lazyRouteComponent($$splitComponentImporter$3, "component") });
var $$splitComponentImporter$2 = () => import("../_protected.superadmin.logs-ODvUXial.mjs");
var Route$3 = createFileRoute("/_protected/superadmin/logs")({ component: lazyRouteComponent($$splitComponentImporter$2, "component") });
var $$splitComponentImporter$1 = () => import("../_protected.superadmin.tenants-ClVAfUpK.mjs");
var Route$2 = createFileRoute("/_protected/superadmin/tenants")({ component: lazyRouteComponent($$splitComponentImporter$1, "component") });
var $$splitComponentImporter = () => import("../_protected.users.index-5W8nYHYT.mjs");
var Route$1 = createFileRoute("/_protected/users/")({ component: lazyRouteComponent($$splitComponentImporter, "component") });
var Route = createFileRoute("/_protected/projects/$projectId/")({ beforeLoad: ({ params }) => {
	throw redirect({
		to: "/projects/$projectId/analytics",
		params: { projectId: params.projectId }
	});
} });
var IndexRoute = Route$13.update({
	id: "/",
	path: "/",
	getParentRoute: () => Route$14
});
var ProtectedRoute = Route$12.update({
	id: "/_protected",
	getParentRoute: () => Route$14
});
var ForgotPasswordRoute = Route$11.update({
	id: "/forgot-password",
	path: "/forgot-password",
	getParentRoute: () => Route$14
});
var LoginRoute = Route$23.update({
	id: "/login",
	path: "/login",
	getParentRoute: () => Route$14
});
var RegisterRoute = Route$10.update({
	id: "/register",
	path: "/register",
	getParentRoute: () => Route$14
});
var ResetPasswordRoute = Route$25.update({
	id: "/reset-password",
	path: "/reset-password",
	getParentRoute: () => Route$14
});
var VerifyEmailRoute = Route$9.update({
	id: "/verify-email",
	path: "/verify-email",
	getParentRoute: () => Route$14
});
var ProtectedDashboardRoute = Route$8.update({
	id: "/dashboard",
	path: "/dashboard",
	getParentRoute: () => ProtectedRoute
});
var ProtectedSettingsRoute = Route$7.update({
	id: "/settings",
	path: "/settings",
	getParentRoute: () => ProtectedRoute
});
var ProtectedSuperadminRoute = Route$6.update({
	id: "/superadmin",
	path: "/superadmin",
	getParentRoute: () => ProtectedRoute
});
var OauthCallbackRoute = Route$24.update({
	id: "/oauth/callback",
	path: "/oauth/callback",
	getParentRoute: () => Route$14
});
var ProtectedProjectsIndexRoute = Route$5.update({
	id: "/projects/",
	path: "/projects/",
	getParentRoute: () => ProtectedRoute
});
var ProtectedProjectsProjectIdRoute = Route$15.update({
	id: "/projects/$projectId",
	path: "/projects/$projectId",
	getParentRoute: () => ProtectedRoute
});
var ProtectedSuperadminIndexRoute = Route$4.update({
	id: "/",
	path: "/",
	getParentRoute: () => ProtectedSuperadminRoute
});
var ProtectedSuperadminLogsRoute = Route$3.update({
	id: "/logs",
	path: "/logs",
	getParentRoute: () => ProtectedSuperadminRoute
});
var ProtectedSuperadminTenantsRoute = Route$2.update({
	id: "/tenants",
	path: "/tenants",
	getParentRoute: () => ProtectedSuperadminRoute
});
var ProtectedUsersIndexRoute = Route$1.update({
	id: "/users/",
	path: "/users/",
	getParentRoute: () => ProtectedRoute
});
var ProtectedProjectsProjectIdIndexRoute = Route.update({
	id: "/",
	path: "/",
	getParentRoute: () => ProtectedProjectsProjectIdRoute
});
var ProtectedProjectsProjectIdAnalyticsRoute = Route$16.update({
	id: "/analytics",
	path: "/analytics",
	getParentRoute: () => ProtectedProjectsProjectIdRoute
});
var ProtectedProjectsProjectIdAuthRoute = Route$17.update({
	id: "/auth",
	path: "/auth",
	getParentRoute: () => ProtectedProjectsProjectIdRoute
});
var ProtectedProjectsProjectIdClaimsRoute = Route$18.update({
	id: "/claims",
	path: "/claims",
	getParentRoute: () => ProtectedProjectsProjectIdRoute
});
var ProtectedProjectsProjectIdGeneralRoute = Route$19.update({
	id: "/general",
	path: "/general",
	getParentRoute: () => ProtectedProjectsProjectIdRoute
});
var ProtectedProjectsProjectIdSecurityRoute = Route$20.update({
	id: "/security",
	path: "/security",
	getParentRoute: () => ProtectedProjectsProjectIdRoute
});
var ProtectedProjectsProjectIdUsersRoute = Route$21.update({
	id: "/users",
	path: "/users",
	getParentRoute: () => ProtectedProjectsProjectIdRoute
});
var ProtectedSuperadminRouteChildren = {
	ProtectedSuperadminLogsRoute,
	ProtectedSuperadminTenantsRoute,
	ProtectedSuperadminIndexRoute,
	ProtectedSuperadminTenantsTenantIdAnalyticsRoute: Route$22.update({
		id: "/tenants_/$tenantId/analytics",
		path: "/tenants/$tenantId/analytics",
		getParentRoute: () => ProtectedSuperadminRoute
	})
};
var ProtectedSuperadminRouteWithChildren = ProtectedSuperadminRoute._addFileChildren(ProtectedSuperadminRouteChildren);
var ProtectedProjectsProjectIdRouteChildren = {
	ProtectedProjectsProjectIdAnalyticsRoute,
	ProtectedProjectsProjectIdAuthRoute,
	ProtectedProjectsProjectIdClaimsRoute,
	ProtectedProjectsProjectIdGeneralRoute,
	ProtectedProjectsProjectIdSecurityRoute,
	ProtectedProjectsProjectIdUsersRoute,
	ProtectedProjectsProjectIdIndexRoute
};
var ProtectedRouteChildren = {
	ProtectedDashboardRoute,
	ProtectedSettingsRoute,
	ProtectedSuperadminRoute: ProtectedSuperadminRouteWithChildren,
	ProtectedProjectsProjectIdRoute: ProtectedProjectsProjectIdRoute._addFileChildren(ProtectedProjectsProjectIdRouteChildren),
	ProtectedProjectsIndexRoute,
	ProtectedUsersIndexRoute
};
var rootRouteChildren = {
	IndexRoute,
	ProtectedRoute: ProtectedRoute._addFileChildren(ProtectedRouteChildren),
	ForgotPasswordRoute,
	LoginRoute,
	RegisterRoute,
	ResetPasswordRoute,
	VerifyEmailRoute,
	OauthCallbackRoute
};
var routeTree = Route$14._addFileChildren(rootRouteChildren)._addFileTypes();
var queryClient = new QueryClient({ defaultOptions: { queries: {
	retry: false,
	refetchOnWindowFocus: false
} } });
function getRouter() {
	return createRouter({
		routeTree,
		context: { queryClient },
		scrollRestoration: true,
		defaultPreload: "intent",
		defaultPreloadStaleTime: 0
	});
}
//#endregion
export { getRouter, queryClient };
