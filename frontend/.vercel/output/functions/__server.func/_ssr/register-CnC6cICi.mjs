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
import { t as PasswordInput } from "./password-input-wO7IT-9k.mjs";
//#region node_modules/.nitro/vite/services/ssr/assets/register-CnC6cICi.js
var import_react = /* @__PURE__ */ __toESM(require_react());
var import_jsx_runtime = require_jsx_runtime();
var registerSchema = object({
	name: string().min(2, "Name must be at least 2 characters"),
	email: string().email("Please enter a valid email address"),
	password: string().min(8, "Password must be at least 8 characters"),
	confirmPassword: string()
}).refine((data) => data.password === data.confirmPassword, {
	message: "Passwords don't match",
	path: ["confirmPassword"]
});
function RegisterPage() {
	const navigate = useNavigate();
	const setUnverifiedEmail = useAuthStore((state) => state.setUnverifiedEmail);
	const setOtpExpiresAt = useAuthStore((state) => state.setOtpExpiresAt);
	const setResendAvailableAt = useAuthStore((state) => state.setResendAvailableAt);
	const accessToken = useAuthStore((state) => state.accessToken);
	const [turnstileToken, setTurnstileToken] = (0, import_react.useState)(null);
	const [authError, setAuthError] = (0, import_react.useState)(null);
	const [pendingAction, setPendingAction] = (0, import_react.useState)(null);
	const [pendingRegisterData, setPendingRegisterData] = (0, import_react.useState)(null);
	(0, import_react.useEffect)(() => {
		if (accessToken) navigate({ to: "/" });
	}, [accessToken, navigate]);
	const { register, handleSubmit, formState: { errors } } = useForm({ resolver: u(registerSchema) });
	const registerMutation = useMutation({
		mutationFn: async (data) => {
			if (!turnstileToken) throw new Error("Please complete the captcha");
			const { confirmPassword, ...backendData } = data;
			return (await apiClient.post("/auth/register", {
				...backendData,
				turnstile_token: turnstileToken
			})).data;
		},
		onSuccess: (data, variables) => {
			setUnverifiedEmail(variables.email);
			if (data.expires_in_seconds) setOtpExpiresAt(Date.now() + data.expires_in_seconds * 1e3);
			setResendAvailableAt(null);
			navigate({ to: "/verify-email" });
		},
		onError: (error) => {
			setAuthError(extractErrorMessage(error, "Registration failed"));
		}
	});
	(0, import_react.useEffect)(() => {
		if (turnstileToken && pendingAction) {
			if (pendingAction === "register" && pendingRegisterData) registerMutation.mutate(pendingRegisterData);
			else if (pendingAction === "google" || pendingAction === "github") window.location.href = `${API_URL}/auth/tenant/login/${pendingAction}`;
			setPendingAction(null);
			setPendingRegisterData(null);
		}
	}, [
		turnstileToken,
		pendingAction,
		pendingRegisterData,
		registerMutation
	]);
	const onSubmit = (data) => {
		setAuthError(null);
		if (!turnstileToken) {
			setPendingAction("register");
			setPendingRegisterData(data);
			return;
		}
		registerMutation.mutate(data);
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
		title: "Create an Account",
		subtitle: "Join Cerberus to manage your data",
		children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("form", {
			onSubmit: handleSubmit(onSubmit),
			className: "space-y-4",
			children: [
				/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
					className: "space-y-1.5",
					children: [
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Label, {
							htmlFor: "name",
							children: "Name"
						}),
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Input, {
							id: "name",
							type: "text",
							placeholder: "John Doe",
							...register("name")
						}),
						errors.name && /* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
							className: "text-terracotta text-xs font-medium",
							children: errors.name.message
						})
					]
				}),
				/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
					className: "space-y-1.5",
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
							className: "text-terracotta text-xs font-medium",
							children: errors.email.message
						})
					]
				}),
				/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
					className: "grid grid-cols-1 sm:grid-cols-2 gap-4",
					children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
						className: "space-y-1.5",
						children: [
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Label, {
								htmlFor: "password",
								children: "Password"
							}),
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)(PasswordInput, {
								id: "password",
								placeholder: "Min. 8 chars",
								...register("password")
							}),
							errors.password && /* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
								className: "text-terracotta text-xs font-medium",
								children: errors.password.message
							})
						]
					}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
						className: "space-y-1.5",
						children: [
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Label, {
								htmlFor: "confirmPassword",
								children: "Confirm Password"
							}),
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)(PasswordInput, {
								id: "confirmPassword",
								placeholder: "Confirm",
								...register("confirmPassword")
							}),
							errors.confirmPassword && /* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
								className: "text-terracotta text-xs font-medium",
								children: errors.confirmPassword.message
							})
						]
					})]
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
					disabled: registerMutation.isPending || pendingAction !== null && pendingAction !== "register",
					children: registerMutation.isPending || pendingAction === "register" ? /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
						className: "flex items-center space-x-2",
						children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", { className: "w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" }), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", { children: "Creating account..." })]
					}) : "Sign up"
				}),
				/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
					className: "relative my-4",
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
						"Already have an account?",
						" ",
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
							onClick: () => navigate({ to: "/login" }),
							className: "text-slate hover:underline font-bold cursor-pointer",
							children: "Log in"
						})
					]
				})
			]
		})
	});
}
//#endregion
export { RegisterPage as component };
