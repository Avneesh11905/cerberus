import { t as useAuthStore } from "./auth-E6d_NOW7.mjs";
import { j as redirect, m as createFileRoute, p as lazyRouteComponent } from "../_libs/@tanstack/react-router+[...].mjs";
import { i as object, o as string } from "../_libs/zod.mjs";
//#region node_modules/.nitro/vite/services/ssr/assets/login-Ch1kjSMw.js
var $$splitComponentImporter = () => import("./login-BzyRonXM.mjs");
var Route = createFileRoute("/login")({
	validateSearch: object({ redirect: string().optional().catch("") }),
	beforeLoad: ({ search }) => {
		if (typeof window === "undefined") return;
		if (useAuthStore.getState().accessToken) throw redirect({ to: search.redirect || "/" });
	},
	component: lazyRouteComponent($$splitComponentImporter, "component")
});
object({
	email: string().email("Please enter a valid email address"),
	password: string().min(1, "Password is required")
});
//#endregion
export { Route as t };
