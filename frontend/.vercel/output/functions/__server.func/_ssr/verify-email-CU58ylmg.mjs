import { o as __toESM } from "../_runtime.mjs";
import { u as require_react } from "../_libs/@floating-ui/react-dom+[...].mjs";
import { t as useAuthStore } from "./auth-E6d_NOW7.mjs";
import { i as extractErrorMessage, n as apiClient } from "./api-client-DJkUESpZ.mjs";
import { t as cn } from "./utils-DgjCne0W.mjs";
import { n as require_jsx_runtime, t as S } from "../_libs/@marsidev/react-turnstile+[...].mjs";
import { _ as useNavigate } from "../_libs/@tanstack/react-router+[...].mjs";
import { t as Button } from "./button-C-O_Pb_u.mjs";
import { t as Input } from "./input-DFi7Mh72.mjs";
import { t as Label } from "./label-CFPE1x7g.mjs";
import { n as Controller, r as useForm, t as u } from "../_libs/@hookform/resolvers+[...].mjs";
import { i as object, o as string } from "../_libs/zod.mjs";
import { t as useMutation } from "../_libs/tanstack__react-query.mjs";
import { t as AuthLayout } from "./AuthLayout-C9Xn-W31.mjs";
import { n as jt, t as Lt } from "../_libs/input-otp.mjs";
//#region node_modules/.nitro/vite/services/ssr/assets/verify-email-CU58ylmg.js
var import_react = /* @__PURE__ */ __toESM(require_react());
var import_jsx_runtime = require_jsx_runtime();
function InputOTP({ className, containerClassName, ...props }) {
	return /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Lt, {
		"data-slot": "input-otp",
		containerClassName: cn("flex items-center gap-2 has-disabled:opacity-50", containerClassName),
		className: cn("disabled:cursor-not-allowed", className),
		...props
	});
}
function InputOTPGroup({ className, ...props }) {
	return /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
		"data-slot": "input-otp-group",
		className: cn("flex items-center", className),
		...props
	});
}
function InputOTPSlot({ index, className, ...props }) {
	const { char, hasFakeCaret, isActive } = import_react.useContext(jt).slots[index];
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
		"data-slot": "input-otp-slot",
		"data-active": isActive,
		className: cn("relative flex h-12 w-12 items-center justify-center border-y-2 border-r-2 border-taupe bg-vanilla text-slate text-lg font-medium transition-all outline-none first:rounded-l-md first:border-l-2 last:rounded-r-md data-[active=true]:z-10 data-[active=true]:border-slate data-[active=true]:ring-2 data-[active=true]:ring-slate/20", className),
		...props,
		children: [char, hasFakeCaret && /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
			className: "pointer-events-none absolute inset-0 flex items-center justify-center",
			children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", { className: "h-5 w-0.5 animate-caret-blink bg-slate duration-1000" })
		})]
	});
}
var verifySchema = object({
	email: string().email("Please enter a valid email address"),
	token: string().length(6, "Token must be exactly 6 digits")
});
function VerifyEmailPage() {
	const navigate = useNavigate();
	const unverifiedEmail = useAuthStore((state) => state.unverifiedEmail);
	const setUnverifiedEmail = useAuthStore((state) => state.setUnverifiedEmail);
	const setVerifiedEmail = useAuthStore((state) => state.setVerifiedEmail);
	const otpExpiresAt = useAuthStore((state) => state.otpExpiresAt);
	const setOtpExpiresAt = useAuthStore((state) => state.setOtpExpiresAt);
	const resendAvailableAt = useAuthStore((state) => state.resendAvailableAt);
	const setResendAvailableAt = useAuthStore((state) => state.setResendAvailableAt);
	const accessToken = useAuthStore((state) => state.accessToken);
	const [authMessage, setAuthMessage] = (0, import_react.useState)(null);
	const [showCaptchaForResend, setShowCaptchaForResend] = (0, import_react.useState)(false);
	const [countdown, setCountdown] = (0, import_react.useState)(0);
	const [timeLeft, setTimeLeft] = (0, import_react.useState)(null);
	const [isRedirecting, setIsRedirecting] = (0, import_react.useState)(false);
	(0, import_react.useEffect)(() => {
		if (accessToken) navigate({ to: "/" });
	}, [accessToken, navigate]);
	(0, import_react.useEffect)(() => {
		if (!resendAvailableAt) {
			setCountdown(0);
			return;
		}
		const calculateCountdown = () => {
			const remaining = Math.max(0, Math.floor((resendAvailableAt - Date.now()) / 1e3));
			setCountdown(remaining);
			return remaining;
		};
		calculateCountdown();
		const timer = setInterval(() => {
			if (calculateCountdown() <= 0) clearInterval(timer);
		}, 1e3);
		return () => clearInterval(timer);
	}, [resendAvailableAt]);
	(0, import_react.useEffect)(() => {
		if (!otpExpiresAt) return;
		const calculateTimeLeft = () => {
			const remaining = Math.max(0, Math.floor((otpExpiresAt - Date.now()) / 1e3));
			setTimeLeft(remaining);
			return remaining;
		};
		calculateTimeLeft();
		const timer = setInterval(() => {
			if (calculateTimeLeft() <= 0) clearInterval(timer);
		}, 1e3);
		return () => clearInterval(timer);
	}, [otpExpiresAt]);
	const formatTime = (seconds) => {
		return `${Math.floor(seconds / 60)}:${(seconds % 60).toString().padStart(2, "0")}`;
	};
	const { control, register, handleSubmit, formState: { errors }, watch } = useForm({
		resolver: u(verifySchema),
		defaultValues: { email: unverifiedEmail || "" }
	});
	const formEmail = watch("email");
	const verifyMutation = useMutation({
		mutationFn: async (data) => {
			return (await apiClient.post("/auth/verify-email", {
				email: data.email,
				otp: data.token
			})).data;
		},
		onSuccess: () => {
			setIsRedirecting(true);
			setVerifiedEmail(unverifiedEmail);
			setUnverifiedEmail(null);
			setTimeout(() => navigate({ to: "/login" }), 2e3);
		},
		onError: (error) => {
			setAuthMessage({
				type: "error",
				text: extractErrorMessage(error, "Verification failed")
			});
		}
	});
	const resendMutation = useMutation({
		mutationFn: async ({ email, token }) => {
			if (!token) throw new Error("Please complete the captcha to resend");
			return (await apiClient.post("/auth/verify-email/resend", {
				email,
				turnstile_token: token
			})).data;
		},
		onSuccess: (data) => {
			setAuthMessage({
				type: "success",
				text: "A new code has been sent to your email."
			});
			if (data.expires_in_seconds) setOtpExpiresAt(Date.now() + data.expires_in_seconds * 1e3);
			setResendAvailableAt(Date.now() + (data.resend_cooldown_seconds || 60) * 1e3);
			setShowCaptchaForResend(false);
		},
		onError: (error) => {
			setAuthMessage({
				type: "error",
				text: extractErrorMessage(error, "Failed to resend code")
			});
			setShowCaptchaForResend(false);
		}
	});
	const onSubmit = (data) => {
		setAuthMessage(null);
		verifyMutation.mutate(data);
	};
	if (isRedirecting) return /* @__PURE__ */ (0, import_jsx_runtime.jsx)(AuthLayout, {
		title: "Email Verified!",
		subtitle: "Redirecting to login...",
		children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
			className: "flex flex-col items-center justify-center p-8 space-y-4",
			children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", { className: "animate-spin h-10 w-10 border-4 border-slate border-t-transparent rounded-full" })
		})
	});
	return /* @__PURE__ */ (0, import_jsx_runtime.jsx)(AuthLayout, {
		title: "Verify your Email",
		subtitle: "Enter your email and the 6-digit code",
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
							className: "flex justify-between items-end",
							children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Label, {
								htmlFor: "token",
								children: "6-Digit OTP"
							}), timeLeft !== null && /* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
								className: `text-xs font-medium ${timeLeft > 0 ? "text-sage" : "text-terracotta"}`,
								children: timeLeft > 0 ? `Code expires in ${formatTime(timeLeft)}` : "Code expired"
							})]
						}),
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
							className: "flex justify-center w-full",
							children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Controller, {
								control,
								name: "token",
								render: ({ field }) => /* @__PURE__ */ (0, import_jsx_runtime.jsx)(InputOTP, {
									maxLength: 6,
									...field,
									children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(InputOTPGroup, { children: [
										/* @__PURE__ */ (0, import_jsx_runtime.jsx)(InputOTPSlot, { index: 0 }),
										/* @__PURE__ */ (0, import_jsx_runtime.jsx)(InputOTPSlot, { index: 1 }),
										/* @__PURE__ */ (0, import_jsx_runtime.jsx)(InputOTPSlot, { index: 2 }),
										/* @__PURE__ */ (0, import_jsx_runtime.jsx)(InputOTPSlot, { index: 3 }),
										/* @__PURE__ */ (0, import_jsx_runtime.jsx)(InputOTPSlot, { index: 4 }),
										/* @__PURE__ */ (0, import_jsx_runtime.jsx)(InputOTPSlot, { index: 5 })
									] })
								})
							})
						}),
						errors.token && /* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
							className: "text-terracotta text-sm font-medium",
							children: errors.token.message
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
					disabled: verifyMutation.isPending,
					children: verifyMutation.isPending ? "Verifying..." : "Verify Email"
				}),
				/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
					className: "mt-6 text-center text-sm font-medium text-slate min-h-10 flex items-center justify-center",
					children: showCaptchaForResend ? /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
						className: "flex justify-center w-full",
						children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
							className: "text-sm font-medium text-slate",
							children: "Verifying..."
						}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)(S, {
							siteKey: "0x4AAAAAAD8HZQAnZBTjBILX".replace(/^["']|["']$/g, "").trim() || "1x00000000000000000000AA",
							onSuccess: (token) => {
								if (formEmail) resendMutation.mutate({
									email: formEmail,
									token
								});
							},
							options: { size: "invisible" }
						})]
					}) : /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", { children: [
						"Didn't receive a code?",
						" ",
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)("button", {
							type: "button",
							onClick: () => {
								if (!formEmail) {
									setAuthMessage({
										type: "error",
										text: "Please enter your email above to resend the code."
									});
									return;
								}
								setShowCaptchaForResend(true);
							},
							disabled: resendMutation.isPending || countdown > 0,
							className: "text-slate hover:underline font-bold disabled:opacity-50 disabled:no-underline",
							children: resendMutation.isPending ? "Sending..." : countdown > 0 ? `Resend (${countdown}s)` : "Resend"
						})
					] })
				})
			]
		})
	});
}
//#endregion
export { VerifyEmailPage as component };
