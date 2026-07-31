import { m as createFileRoute, p as lazyRouteComponent } from "../_libs/@tanstack/react-router+[...].mjs";
import { i as object, o as string } from "../_libs/zod.mjs";
//#region node_modules/.nitro/vite/services/ssr/assets/reset-password-Ds7fBS4O.js
var $$splitComponentImporter = () => import("./reset-password-Xpa0V1j0.mjs");
var searchSchema = object({ token: string().optional() });
var Route = createFileRoute("/reset-password")({
	component: lazyRouteComponent($$splitComponentImporter, "component"),
	validateSearch: searchSchema
});
object({
	password: string().min(8, "Password must be at least 8 characters"),
	confirmPassword: string()
}).refine((data) => data.password === data.confirmPassword, {
	message: "Passwords don't match",
	path: ["confirmPassword"]
});
//#endregion
export { Route as t };
