import { m as createFileRoute, p as lazyRouteComponent } from "../_libs/@tanstack/react-router+[...].mjs";
import { i as object, n as boolean, o as string, s as union } from "../_libs/zod.mjs";
//#region node_modules/.nitro/vite/services/ssr/assets/oauth.callback-BOz15k1E.js
var $$splitComponentImporter = () => import("./oauth.callback-CuTci0nL.mjs");
var searchSchema = object({
	code: string().optional(),
	new_user: union([string(), boolean()]).optional(),
	error: string().optional()
});
var Route = createFileRoute("/oauth/callback")({
	component: lazyRouteComponent($$splitComponentImporter, "component"),
	validateSearch: searchSchema
});
//#endregion
export { Route as t };
