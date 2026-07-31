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
import { t as Route } from "./reset-password-Ds7fBS4O.mjs";
//#region node_modules/.nitro/vite/services/ssr/assets/reset-password-Xpa0V1j0.js
var import_react = /* @__PURE__ */ __toESM(require_react());
var import_jsx_runtime = require_jsx_runtime();
var resetSchema = object({
	password: string().min(8, "Password must be at least 8 characters"),
	confirmPassword: string()
}).refine((data) => data.password === data.confirmPassword, {
	message: "Passwords don't match",
	path: ["confirmPassword"]
});
function ResetPasswordPage() {
	const search = Route.useSearch();
	const navigate = useNavigate();
	const [authMessage, setAuthMessage] = (0, import_react.useState)(null);
	const { register, handleSubmit, formState: { errors } } = useForm({ resolver: u(resetSchema) });
	const resetMutation = useMutation({
		mutationFn: async (data) => {
			return (await apiClient.post("/auth/password/reset", {
				token: search.token,
				new_password: data.password
			})).data;
		},
		onSuccess: () => {
			setAuthMessage({
				type: "success",
				text: "Password reset successfully! You can now log in."
			});
			setTimeout(() => navigate({ to: "/login" }), 2e3);
		},
		onError: (error) => {
			setAuthMessage({
				type: "error",
				text: extractErrorMessage(error, "Failed to reset password")
			});
		}
	});
	const onSubmit = (data) => {
		if (!search.token) {
			setAuthMessage({
				type: "error",
				text: "Missing reset token in URL."
			});
			return;
		}
		setAuthMessage(null);
		resetMutation.mutate(data);
	};
	return /* @__PURE__ */ (0, import_jsx_runtime.jsx)(AuthLayout, {
		title: "Reset Password",
		subtitle: "Enter your new password below",
		children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("form", {
			onSubmit: handleSubmit(onSubmit),
			className: "space-y-5",
			children: [
				/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
					className: "space-y-2",
					children: [
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Label, {
							htmlFor: "password",
							children: "New Password"
						}),
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Input, {
							id: "password",
							type: "password",
							placeholder: "Min. 8 characters",
							...register("password")
						}),
						errors.password && /* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
							className: "text-terracotta text-sm font-medium",
							children: errors.password.message
						})
					]
				}),
				/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
					className: "space-y-2",
					children: [
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Label, {
							htmlFor: "confirmPassword",
							children: "Confirm Password"
						}),
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Input, {
							id: "confirmPassword",
							type: "password",
							...register("confirmPassword")
						}),
						errors.confirmPassword && /* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
							className: "text-terracotta text-sm font-medium",
							children: errors.confirmPassword.message
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
					disabled: resetMutation.isPending || !search.token,
					children: resetMutation.isPending ? "Resetting..." : "Reset Password"
				})
			]
		})
	});
}
//#endregion
export { ResetPasswordPage as component };
