import { o as __toESM } from "../_runtime.mjs";
import { u as require_react } from "../_libs/@floating-ui/react-dom+[...].mjs";
import { i as extractErrorMessage, n as apiClient } from "./api-client-DJkUESpZ.mjs";
import { n as require_jsx_runtime } from "../_libs/@marsidev/react-turnstile+[...].mjs";
import { _ as useNavigate } from "../_libs/@tanstack/react-router+[...].mjs";
import { t as Button } from "./button-C-O_Pb_u.mjs";
import { t as Input } from "./input-DFi7Mh72.mjs";
import { t as Label } from "./label-CFPE1x7g.mjs";
import { r as useForm, t as u } from "../_libs/@hookform/resolvers+[...].mjs";
import { i as object, o as string } from "../_libs/zod.mjs";
import { t as useMutation } from "../_libs/tanstack__react-query.mjs";
import { t as AuthLayout } from "./AuthLayout-C9Xn-W31.mjs";
//#region node_modules/.nitro/vite/services/ssr/assets/forgot-password-CB0AD5xL.js
var import_react = /* @__PURE__ */ __toESM(require_react());
var import_jsx_runtime = require_jsx_runtime();
var forgotSchema = object({ email: string().email("Please enter a valid email address") });
function ForgotPasswordPage() {
	const navigate = useNavigate();
	const [authMessage, setAuthMessage] = (0, import_react.useState)(null);
	const { register, handleSubmit, formState: { errors } } = useForm({ resolver: u(forgotSchema) });
	const forgotMutation = useMutation({
		mutationFn: async (data) => {
			return (await apiClient.post("/auth/password/forgot", data)).data;
		},
		onSuccess: () => {
			setAuthMessage({
				type: "success",
				text: "If an account exists, a password reset link has been sent to the email."
			});
		},
		onError: (error) => {
			setAuthMessage({
				type: "error",
				text: extractErrorMessage(error, "Failed to send reset link")
			});
		}
	});
	const onSubmit = (data) => {
		setAuthMessage(null);
		forgotMutation.mutate(data);
	};
	return /* @__PURE__ */ (0, import_jsx_runtime.jsx)(AuthLayout, {
		title: "Forgot Password",
		subtitle: "Enter your email to receive a reset link",
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
				authMessage && /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
					className: `p-3 rounded-md border text-sm font-bold text-center ${authMessage.type === "error" ? "bg-terracotta/10 border-terracotta/20 text-terracotta" : "bg-sage/10 border-sage/20 text-sage"}`,
					children: authMessage.text
				}),
				/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Button, {
					type: "submit",
					className: "w-full mt-4",
					disabled: forgotMutation.isPending,
					children: forgotMutation.isPending ? "Sending..." : "Send Reset Link"
				}),
				/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
					className: "mt-6 text-center text-sm font-medium text-slate",
					children: [
						"Remembered your password?",
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
export { ForgotPasswordPage as component };
