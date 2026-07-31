import { o as __toESM } from "../_runtime.mjs";
import { u as require_react } from "../_libs/@floating-ui/react-dom+[...].mjs";
import { t as useAuthStore } from "./auth-E6d_NOW7.mjs";
import { t as axios } from "../_libs/axios+[...].mjs";
import { n as apiClient } from "./api-client-DJkUESpZ.mjs";
import { n as require_jsx_runtime } from "../_libs/@marsidev/react-turnstile+[...].mjs";
import { _ as useNavigate } from "../_libs/@tanstack/react-router+[...].mjs";
import { t as Button } from "./button-C-O_Pb_u.mjs";
import { t as AuthLayout } from "./AuthLayout-C9Xn-W31.mjs";
import { t as Route } from "./oauth.callback-BOz15k1E.mjs";
//#region node_modules/.nitro/vite/services/ssr/assets/oauth.callback-CuTci0nL.js
var import_react = /* @__PURE__ */ __toESM(require_react());
var import_jsx_runtime = require_jsx_runtime();
function OAuthCallbackPage() {
	const search = Route.useSearch();
	const navigate = useNavigate();
	const setAuth = useAuthStore((state) => state.setAuth);
	const [error, setError] = (0, import_react.useState)(search.error || null);
	(0, import_react.useEffect)(() => {
		const completeLogin = async () => {
			try {
				if (search.code) {
					const { data } = await apiClient.post("/auth/exchange", { code: search.code });
					setAuth(data.access_token, data.csrf_token, data.user);
					navigate({ to: "/" });
				} else {
					const { data } = await apiClient.get("/users/me");
					setAuth("", "", data);
					navigate({ to: "/" });
				}
			} catch (err) {
				if (axios.isAxiosError(err)) setError(err.response?.data?.detail || "OAuth authentication failed.");
				else setError("OAuth authentication failed.");
			}
		};
		if (!error) completeLogin();
	}, [
		search,
		navigate,
		setAuth,
		error
	]);
	return /* @__PURE__ */ (0, import_jsx_runtime.jsx)(AuthLayout, {
		title: "Authenticating",
		subtitle: "Please wait while we log you in...",
		children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
			className: "flex flex-col items-center justify-center p-8 space-y-4",
			children: error ? /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
				className: "flex flex-col items-center gap-4 w-full max-w-sm",
				children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
					className: "text-terracotta text-sm font-bold text-center",
					children: error
				}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Button, {
					onClick: () => navigate({ to: "/login" }),
					className: "w-full mt-4",
					children: "Back to Login"
				})]
			}) : /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", { className: "animate-spin h-10 w-10 border-4 border-slate border-t-transparent rounded-full" })
		})
	});
}
//#endregion
export { OAuthCallbackPage as component };
