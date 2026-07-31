import { o as __toESM } from "../_runtime.mjs";
import { u as require_react } from "../_libs/@floating-ui/react-dom+[...].mjs";
import { t as useAuthStore } from "./auth-E6d_NOW7.mjs";
import { i as extractErrorMessage, n as apiClient, t as API_URL } from "./api-client-DJkUESpZ.mjs";
import { n as require_jsx_runtime, t as S } from "../_libs/@marsidev/react-turnstile+[...].mjs";
import { _ as useNavigate } from "../_libs/@tanstack/react-router+[...].mjs";
import { t as Button } from "./button-C-O_Pb_u.mjs";
import { t as Input } from "./input-DFi7Mh72.mjs";
import { t as Label } from "./label-CFPE1x7g.mjs";
import { r as useForm, t as u } from "../_libs/@hookform/resolvers+[...].mjs";
import { i as object, o as string } from "../_libs/zod.mjs";
import { n as GoogleIcon, t as GithubIcon } from "./icons-D5yVeA9Y.mjs";
import { t as useMutation } from "../_libs/tanstack__react-query.mjs";
import { t as AuthLayout } from "./AuthLayout-C9Xn-W31.mjs";
import { t as Route } from "./login-Ch1kjSMw.mjs";
import { t as PasswordInput } from "./password-input-wO7IT-9k.mjs";
//#region node_modules/.nitro/vite/services/ssr/assets/login-BzyRonXM.js
var import_react = /* @__PURE__ */ __toESM(require_react());
var import_jsx_runtime = require_jsx_runtime();
var loginSchema = object({
	email: string().email("Please enter a valid email address"),
	password: string().min(1, "Password is required")
});
function LoginPage() {
	const navigate = useNavigate();
	const setAuth = useAuthStore((state) => state.setAuth);
	const accessToken = useAuthStore((state) => state.accessToken);
	const [turnstileToken, setTurnstileToken] = (0, import_react.useState)(null);
	const [authError, setAuthError] = (0, import_react.useState)(null);
	const [pendingAction, setPendingAction] = (0, import_react.useState)(null);
	const [pendingLoginData, setPendingLoginData] = (0, import_react.useState)(null);
	const verifiedEmail = useAuthStore((state) => state.verifiedEmail);
	const search = Route.useSearch();
	(0, import_react.useEffect)(() => {
		if (accessToken) navigate({ to: search.redirect || "/" });
	}, [
		accessToken,
		navigate,
		search.redirect
	]);
	const { register, handleSubmit, formState: { errors } } = useForm({
		resolver: u(loginSchema),
		defaultValues: { email: verifiedEmail || "" }
	});
	const loginMutation = useMutation({
		mutationFn: async (data) => {
			if (!turnstileToken) throw new Error("Please complete the captcha");
			return (await apiClient.post("/auth/login", {
				...data,
				turnstile_token: turnstileToken
			})).data;
		},
		onSuccess: (data) => {
			setAuth(data.access_token, data.csrf_token, data.user);
			navigate({ to: search.redirect || "/" });
		},
		onError: (error) => {
			setAuthError(extractErrorMessage(error, "Login failed"));
		}
	});
	(0, import_react.useEffect)(() => {
		if (turnstileToken && pendingAction) {
			if (pendingAction === "login" && pendingLoginData) loginMutation.mutate(pendingLoginData);
			else if (pendingAction === "google" || pendingAction === "github") window.location.href = `${API_URL}/auth/tenant/login/${pendingAction}`;
			setPendingAction(null);
			setPendingLoginData(null);
		}
	}, [
		turnstileToken,
		pendingAction,
		pendingLoginData,
		loginMutation
	]);
	const onSubmit = (data) => {
		setAuthError(null);
		if (!turnstileToken) {
			setPendingAction("login");
			setPendingLoginData(data);
			return;
		}
		loginMutation.mutate(data);
	};
	const handleOAuth = (provider) => {
		if (!turnstileToken) {
			setPendingAction(provider);
			return;
		}
		window.location.href = `${API_URL}/auth/tenant/login/${provider}`;
	};
	if (accessToken) return null;
	return /* @__PURE__ */ (0, import_jsx_runtime.jsx)(AuthLayout, {
		title: verifiedEmail ? "Welcome to Cerberus" : "Welcome Back",
		subtitle: verifiedEmail ? "Please log in to access your dashboard" : "Log in to Cerberus Dashboard",
		children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("form", {
			onSubmit: handleSubmit(onSubmit),
			className: "space-y-5",
			children: [
				/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
					className: "space-y-2",
					children: [
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Label, {
							htmlFor: "email",
							children: "Email"
						}),
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Input, {
							id: "email",
							type: "email",
							placeholder: "you@example.com",
							...register("email")
						}),
						errors.email && /* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
							className: "text-terracotta text-sm font-medium",
							children: errors.email.message
						})
					]
				}),
				/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
					className: "space-y-2",
					children: [
						/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
							className: "flex items-center justify-between",
							children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Label, {
								htmlFor: "password",
								children: "Password"
							}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
								onClick: () => navigate({ to: "/forgot-password" }),
								className: "text-sm text-slate font-bold hover:underline cursor-pointer",
								children: "Forgot password?"
							})]
						}),
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)(PasswordInput, {
							id: "password",
							...register("password")
						}),
						errors.password && /* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
							className: "text-terracotta text-sm font-medium",
							children: errors.password.message
						})
					]
				}),
				authError && /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
					className: "p-3 bg-terracotta/10 border border-terracotta/20 rounded-md",
					children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
						className: "text-terracotta text-sm font-bold text-center",
						children: authError
					})
				}),
				/* @__PURE__ */ (0, import_jsx_runtime.jsx)(S, {
					siteKey: "0x4AAAAAAD8HZQAnZBTjBILX".replace(/^["']|["']$/g, "").trim() || "1x00000000000000000000AA",
					onSuccess: (token) => setTurnstileToken(token),
					options: { size: "invisible" }
				}),
				/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Button, {
					type: "submit",
					className: "w-full mt-4",
					disabled: loginMutation.isPending || pendingAction !== null && pendingAction !== "login",
					children: loginMutation.isPending || pendingAction === "login" ? /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
						className: "flex items-center space-x-2",
						children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", { className: "w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" }), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", { children: "Logging in..." })]
					}) : "Log in"
				}),
				/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
					className: "relative my-6",
					children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
						className: "absolute inset-0 flex items-center",
						children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", { className: "w-full border-t border-taupe" })
					}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
						className: "relative flex justify-center text-xs uppercase",
						children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
							className: "bg-sand px-2 text-slate font-bold",
							children: "Or continue with"
						})
					})]
				}),
				/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
					className: "grid grid-cols-1 sm:grid-cols-2 gap-3 sm:gap-4",
					children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Button, {
						variant: "outline",
						type: "button",
						disabled: pendingAction !== null && pendingAction !== "google",
						onClick: () => handleOAuth("google"),
						className: "flex items-center justify-center space-x-2",
						children: pendingAction === "google" ? /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", { className: "w-4 h-4 border-2 border-slate border-t-transparent rounded-full animate-spin" }) : /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(import_jsx_runtime.Fragment, { children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(GoogleIcon, { className: "w-5 h-5" }), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
							className: "font-semibold text-[13px] tracking-wide",
							children: "Google"
						})] })
					}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Button, {
						variant: "outline",
						type: "button",
						disabled: pendingAction !== null && pendingAction !== "github",
						onClick: () => handleOAuth("github"),
						className: "flex items-center justify-center space-x-2",
						children: pendingAction === "github" ? /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", { className: "w-4 h-4 border-2 border-slate border-t-transparent rounded-full animate-spin" }) : /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(import_jsx_runtime.Fragment, { children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(GithubIcon, { className: "w-5 h-5 text-slate" }), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
							className: "font-semibold text-[13px] tracking-wide",
							children: "GitHub"
						})] })
					})]
				}),
				/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
					className: "mt-6 text-center text-sm font-medium text-slate",
					children: [
						"Don't have an account?",
						" ",
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
							onClick: () => navigate({ to: "/register" }),
							className: "text-slate hover:underline font-bold cursor-pointer",
							children: "Sign up"
						})
					]
				})
			]
		})
	});
}
//#endregion
export { LoginPage as component };
