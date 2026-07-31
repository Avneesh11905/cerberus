import { n as clsx } from "./_libs/class-variance-authority+clsx.mjs";
import { n as require_jsx_runtime } from "./_libs/@marsidev/react-turnstile+[...].mjs";
import { Z as ChartColumn, r as Users, tt as ArrowLeft, y as ScrollText } from "./_libs/lucide-react.mjs";
import { f as Outlet, l as useLocation, y as useRouter } from "./_libs/@tanstack/react-router+[...].mjs";
import { t as Button } from "./_ssr/button-C-O_Pb_u.mjs";
//#region node_modules/.nitro/vite/services/ssr/assets/_protected.superadmin-DT4y2gLB.js
var import_jsx_runtime = require_jsx_runtime();
function SuperadminLayout() {
	const location = useLocation();
	const router = useRouter();
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
		className: "max-w-7xl mx-auto flex flex-col gap-8 w-full",
		children: [
			/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
				className: "flex items-center gap-4",
				children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Button, {
					variant: "outline",
					size: "icon",
					className: "border-2 border-slate w-10 h-10 rounded-xl",
					onClick: () => router.navigate({ to: "/dashboard" }),
					children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(ArrowLeft, { className: "w-5 h-5 text-slate" })
				}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", { children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("h1", {
					className: "text-3xl font-display font-bold text-slate",
					children: "Superadmin Portal"
				}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
					className: "text-slate/60 mt-1",
					children: "Platform management and analytics"
				})] })]
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
				className: "flex border-b-2 border-taupe/30",
				children: [
					{
						name: "Analytics",
						href: "/superadmin",
						icon: ChartColumn,
						exact: true
					},
					{
						name: "Tenants",
						href: "/superadmin/tenants",
						icon: Users,
						exact: false
					},
					{
						name: "System Logs",
						href: "/superadmin/logs",
						icon: ScrollText,
						exact: false
					}
				].map((item) => {
					return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("span", {
						onClick: () => router.navigate({ to: item.href }),
						className: clsx("flex items-center gap-2 px-6 py-3 font-semibold transition-colors border-b-2 -mb-0.5 cursor-pointer", (item.exact ? location.pathname === item.href : location.pathname.startsWith(item.href)) ? "border-ochre text-ochre" : "border-transparent text-slate/70 hover:text-slate hover:bg-taupe/10"),
						children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(item.icon, { className: "w-4 h-4" }), item.name]
					}, item.name);
				})
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
				className: "pt-2",
				children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Outlet, {})
			})
		]
	});
}
//#endregion
export { SuperadminLayout as component };
