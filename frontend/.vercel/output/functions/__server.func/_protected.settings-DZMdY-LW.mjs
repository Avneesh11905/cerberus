import { o as __toESM } from "./_runtime.mjs";
import { u as require_react } from "./_libs/@floating-ui/react-dom+[...].mjs";
import { t as useAuthStore } from "./_ssr/auth-E6d_NOW7.mjs";
import { i as extractErrorMessage, n as apiClient } from "./_ssr/api-client-DJkUESpZ.mjs";
import { n as require_jsx_runtime } from "./_libs/@marsidev/react-turnstile+[...].mjs";
import { D as Monitor, O as LogOut, Y as Check, d as Shield, i as User, l as Trash2, s as TriangleAlert, tt as ArrowLeft, u as Smartphone } from "./_libs/lucide-react.mjs";
import { n as AvatarFallback, r as AvatarImage, t as Avatar } from "./_ssr/avatar-DnS6IaKa.mjs";
import { _ as useNavigate } from "./_libs/@tanstack/react-router+[...].mjs";
import { n as AnimatePresence, t as motion } from "./_libs/framer-motion.mjs";
import { t as Button } from "./_ssr/button-C-O_Pb_u.mjs";
import { t as Input } from "./_ssr/input-DFi7Mh72.mjs";
import { n as toast } from "./_libs/sonner.mjs";
import { a as CardHeader, i as CardFooter, n as CardContent, o as CardTitle, r as CardDescription, t as Card } from "./_ssr/card-D2S-3Lsc.mjs";
import { t as Label } from "./_ssr/label-CFPE1x7g.mjs";
import { a as DialogFooter, c as DialogTrigger, i as DialogDescription, o as DialogHeader, r as DialogContent, s as DialogTitle, t as Dialog$1 } from "./_ssr/dialog-DYmxbvqX.mjs";
import { r as useForm, t as u } from "./_libs/@hookform/resolvers+[...].mjs";
import { i as object, o as string, r as literal } from "./_libs/zod.mjs";
import { t as Checkbox } from "./_ssr/checkbox-BY8mRrC-.mjs";
import { n as GoogleIcon, t as GithubIcon } from "./_ssr/icons-D5yVeA9Y.mjs";
import { i as useQueryClient, n as useQuery, t as useMutation } from "./_libs/tanstack__react-query.mjs";
//#region node_modules/.nitro/vite/services/ssr/assets/_protected.settings-DZMdY-LW.js
var import_react = /* @__PURE__ */ __toESM(require_react());
var import_jsx_runtime = require_jsx_runtime();
var getMe = async () => {
	return (await apiClient.get("/users/me")).data;
};
var updateProfile = async (data) => {
	return (await apiClient.patch("/users/me", data)).data;
};
var deleteMe = async () => {
	return (await apiClient.delete("/users/me")).data;
};
var updatePassword = async (data) => {
	return (await apiClient.patch("/auth/password/", data)).data;
};
var getSessions = async () => {
	return (await apiClient.get("/auth/sessions")).data;
};
var revokeSession = async (familyId) => {
	return (await apiClient.delete(`/auth/sessions/${familyId}`)).data;
};
var revokeAllSessions = async () => {
	return (await apiClient.post("/auth/logout/all")).data;
};
var profileSchema = object({
	name: string().min(1, "Name is required"),
	picture: string().url("Must be a valid URL").optional().or(literal(""))
});
function ProfileTab() {
	const user = useAuthStore((state) => state.user);
	const setUser = useAuthStore((state) => state.setUser);
	const queryClient = useQueryClient();
	const [isSaved, setIsSaved] = (0, import_react.useState)(false);
	const { register, handleSubmit, reset, watch, formState: { errors } } = useForm({
		resolver: u(profileSchema),
		defaultValues: {
			name: user?.name || "",
			picture: user?.picture || ""
		}
	});
	const { data: profile, isLoading } = useQuery({
		queryKey: ["profile"],
		queryFn: getMe
	});
	const hasPassword = profile ? profile.login_methods?.includes("local") : true;
	(0, import_react.useEffect)(() => {
		if (profile) {
			reset({
				name: profile.name || "",
				picture: profile.picture || ""
			});
			const currentUser = useAuthStore.getState().user;
			if (currentUser) setUser({
				...currentUser,
				...profile
			});
		}
	}, [
		profile,
		reset,
		setUser
	]);
	const updateProfileMutation = useMutation({
		mutationFn: updateProfile,
		onSuccess: (data) => {
			setUser({
				...user,
				...data
			});
			queryClient.invalidateQueries({ queryKey: ["profile"] });
			setIsSaved(true);
			setTimeout(() => setIsSaved(false), 2e3);
		},
		onError: (err) => {
			toast.error(extractErrorMessage(err, "Failed to update profile"));
		}
	});
	const receiveUpdatesMutation = useMutation({
		mutationFn: updateProfile,
		onMutate: async (newData) => {
			await queryClient.cancelQueries({ queryKey: ["profile"] });
			const previousProfile = queryClient.getQueryData(["profile"]);
			queryClient.setQueryData(["profile"], (old) => ({
				...old,
				...newData
			}));
			return { previousProfile };
		},
		onSuccess: (data) => {
			setUser({
				...user,
				...data
			});
			queryClient.invalidateQueries({ queryKey: ["profile"] });
		},
		onError: (err, _newData, context) => {
			if (context?.previousProfile) queryClient.setQueryData(["profile"], context.previousProfile);
			toast.error(extractErrorMessage(err, "Failed to update settings"));
		}
	});
	if (isLoading) return /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Card, {
		className: "flat-card border-2 flex items-center justify-center p-12",
		children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", { className: "animate-spin h-8 w-8 border-4 border-slate border-t-transparent rounded-full" })
	});
	const pictureUrl = watch("picture");
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
		className: "space-y-8 animate-in fade-in slide-in-from-bottom-2 duration-300",
		children: [!hasPassword && /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Card, {
			className: "flat-card border-2 border-sunflower/50 bg-sunflower/10",
			children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(CardContent, {
				className: "flex items-start gap-3 p-4",
				children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(TriangleAlert, { className: "w-5 h-5 mt-0.5 shrink-0 text-sunflower" }), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
					className: "text-sm font-bold text-slate",
					children: "Your account doesn't have a password set. We highly recommend setting a password in the Security tab to fully secure your account."
				})]
			})
		}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Card, {
			className: "flat-card border-2",
			children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("form", {
				onSubmit: handleSubmit((data) => updateProfileMutation.mutate(data)),
				children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)(CardHeader, { children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(CardTitle, { children: "Profile Details" }), /* @__PURE__ */ (0, import_jsx_runtime.jsx)(CardDescription, { children: "Update your personal information." })] }), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(CardContent, {
					className: "space-y-6",
					children: [
						/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
							className: "space-y-2",
							children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Label, {
								htmlFor: "picture",
								children: "Profile Picture"
							}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
								className: "flex items-start gap-4",
								children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)(Avatar, {
									className: "w-16 h-16 border-2 border-slate shadow-[2px_2px_0px_rgba(30,41,59,1)] shrink-0",
									children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(AvatarImage, { src: pictureUrl || user?.picture || "" }), /* @__PURE__ */ (0, import_jsx_runtime.jsx)(AvatarFallback, {
										className: "bg-sage/20 text-sage text-2xl font-black",
										children: (user?.name || "U")[0].toUpperCase()
									})]
								}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
									className: "flex-1 space-y-2 mt-1",
									children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Input, {
										id: "picture",
										placeholder: "https://example.com/avatar.jpg",
										...register("picture"),
										className: errors.picture ? "border-terracotta focus-visible:ring-terracotta" : ""
									}), errors.picture && /* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
										className: "text-sm font-bold text-terracotta",
										children: errors.picture.message
									})]
								})]
							})]
						}),
						/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
							className: "grid grid-cols-1 sm:grid-cols-2 gap-6",
							children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
								className: "space-y-2",
								children: [
									/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Label, {
										htmlFor: "email",
										children: "Email"
									}),
									/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Input, {
										id: "email",
										value: profile?.email || user?.email || "",
										disabled: true,
										className: "bg-taupe/10 cursor-not-allowed"
									}),
									/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
										className: "text-xs font-bold text-slate/50",
										children: "Email cannot be changed via the API directly."
									})
								]
							}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
								className: "space-y-2",
								children: [
									/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Label, {
										htmlFor: "name",
										children: "Display Name"
									}),
									/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Input, {
										id: "name",
										...register("name"),
										className: errors.name ? "border-terracotta focus-visible:ring-terracotta" : ""
									}),
									errors.name && /* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
										className: "text-sm font-bold text-terracotta",
										children: errors.name.message
									})
								]
							})]
						}),
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
							className: "flex justify-end pt-2",
							children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Button, {
								type: "submit",
								variant: "primary",
								disabled: updateProfileMutation.isPending,
								children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(AnimatePresence, {
									mode: "wait",
									children: isSaved ? /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(motion.div, {
										initial: {
											opacity: 0,
											y: 10
										},
										animate: {
											opacity: 1,
											y: 0
										},
										exit: {
											opacity: 0,
											y: -10
										},
										className: "flex items-center gap-2",
										children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Check, { className: "w-4 h-4" }), " Saved!"]
									}, "saved") : /* @__PURE__ */ (0, import_jsx_runtime.jsx)(motion.div, {
										initial: {
											opacity: 0,
											y: 10
										},
										animate: {
											opacity: 1,
											y: 0
										},
										exit: {
											opacity: 0,
											y: -10
										},
										children: updateProfileMutation.isPending ? "Saving..." : "Save Changes"
									}, "save")
								})
							})
						}),
						/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
							className: "space-y-2 pt-6 border-t-2 border-taupe/20",
							children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Label, { children: "Account Details" }), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
								className: "flex flex-wrap gap-6 p-4 rounded-xl bg-vanilla border-2 border-taupe/30",
								children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
									className: "flex flex-col gap-1.5",
									children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
										className: "text-xs font-bold text-slate/50 uppercase tracking-wider",
										children: "Login Methods"
									}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
										className: "flex flex-wrap gap-1.5",
										children: [profile?.login_methods?.map((method) => /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("span", {
											className: "flex items-center gap-1.5 px-3 py-1 bg-slate/10 text-slate text-[10px] uppercase tracking-wider font-bold rounded-full border-2 border-slate/20",
											children: [
												method.toLowerCase() === "google" && /* @__PURE__ */ (0, import_jsx_runtime.jsx)(GoogleIcon, { className: "w-3 h-3" }),
												method.toLowerCase() === "github" && /* @__PURE__ */ (0, import_jsx_runtime.jsx)(GithubIcon, { className: "w-3 h-3" }),
												method
											]
										}, method)), (!profile?.login_methods || profile.login_methods.length === 0) && /* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
											className: "text-sm font-medium text-slate/50",
											children: "None"
										})]
									})]
								})
							})]
						}),
						/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
							className: "flex items-start gap-3 p-4 rounded-xl border-2 border-taupe/30 bg-vanilla",
							children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Checkbox, {
								id: "receive_updates",
								checked: profile?.receive_updates ?? false,
								onCheckedChange: (checked) => {
									const newValue = checked === true;
									receiveUpdatesMutation.mutate({ receive_updates: newValue });
								},
								className: "mt-1"
							}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
								className: "space-y-1",
								children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Label, {
									htmlFor: "receive_updates",
									className: "cursor-pointer",
									children: "Receive Email Updates"
								}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
									className: "text-xs font-bold text-slate/60",
									children: "Opt-in to receive product updates, security alerts, and newsletters."
								})]
							})]
						})
					]
				})]
			})
		})]
	});
}
var getPasswordSchema = (hasPassword) => object({
	current_password: hasPassword ? string().min(1, "Current password is required") : string().optional(),
	new_password: string().min(8, "Password must be at least 8 characters"),
	confirm_password: string().min(1, "Please confirm password")
}).refine((data) => data.new_password === data.confirm_password, {
	message: "Passwords don't match",
	path: ["confirm_password"]
});
function ChangePasswordCard() {
	const { data: profile } = useQuery({
		queryKey: ["profile"],
		queryFn: getMe
	});
	const hasPassword = profile ? profile.login_methods?.includes("local") : true;
	const { register, handleSubmit, reset, formState: { errors } } = useForm({ resolver: u((0, import_react.useMemo)(() => getPasswordSchema(hasPassword ?? true), [hasPassword])) });
	const queryClient = useQueryClient();
	const passwordMutation = useMutation({
		mutationFn: updatePassword,
		onSuccess: () => {
			toast.success(hasPassword ? "Password updated successfully" : "Password set successfully");
			queryClient.invalidateQueries({ queryKey: ["profile"] });
			reset();
		},
		onError: (err) => {
			toast.error(extractErrorMessage(err, "Failed to update password"));
		}
	});
	return /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Card, {
		className: "flat-card border-2",
		children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("form", {
			onSubmit: handleSubmit((data) => passwordMutation.mutate(data)),
			children: [
				/* @__PURE__ */ (0, import_jsx_runtime.jsxs)(CardHeader, { children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(CardTitle, { children: hasPassword ? "Change Password" : "Set Password" }), /* @__PURE__ */ (0, import_jsx_runtime.jsx)(CardDescription, { children: hasPassword ? "Ensure your account is using a long, random password to stay secure." : "Add a password to your account so you can log in with email and password." })] }),
				/* @__PURE__ */ (0, import_jsx_runtime.jsxs)(CardContent, {
					className: "space-y-4",
					children: [
						hasPassword && /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
							className: "space-y-2",
							children: [
								/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Label, {
									htmlFor: "current_password",
									children: "Current Password"
								}),
								/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Input, {
									id: "current_password",
									type: "password",
									...register("current_password"),
									className: errors.current_password ? "border-terracotta focus-visible:ring-terracotta" : ""
								}),
								errors.current_password && /* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
									className: "text-sm font-bold text-terracotta",
									children: errors.current_password.message
								})
							]
						}),
						/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
							className: "space-y-2",
							children: [
								/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Label, {
									htmlFor: "new_password",
									children: "New Password"
								}),
								/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Input, {
									id: "new_password",
									type: "password",
									...register("new_password"),
									className: errors.new_password ? "border-terracotta focus-visible:ring-terracotta" : ""
								}),
								errors.new_password && /* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
									className: "text-sm font-bold text-terracotta",
									children: errors.new_password.message
								})
							]
						}),
						/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
							className: "space-y-2",
							children: [
								/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Label, {
									htmlFor: "confirm_password",
									children: "Confirm New Password"
								}),
								/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Input, {
									id: "confirm_password",
									type: "password",
									...register("confirm_password"),
									className: errors.confirm_password ? "border-terracotta focus-visible:ring-terracotta" : ""
								}),
								errors.confirm_password && /* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
									className: "text-sm font-bold text-terracotta",
									children: errors.confirm_password.message
								})
							]
						})
					]
				}),
				/* @__PURE__ */ (0, import_jsx_runtime.jsx)(CardFooter, {
					className: "flex justify-end border-t-2 border-taupe/20 pt-6",
					children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Button, {
						type: "submit",
						variant: "primary",
						disabled: passwordMutation.isPending,
						children: passwordMutation.isPending ? "Updating..." : hasPassword ? "Update Password" : "Set Password"
					})
				})
			]
		})
	});
}
var parseUserAgent = (ua) => {
	if (!ua) return "Unknown Device";
	let os = "Unknown OS";
	if (ua.includes("Win")) os = "Windows";
	else if (ua.includes("Mac")) os = "macOS";
	else if (ua.includes("Linux")) os = "Linux";
	else if (ua.includes("iPhone") || ua.includes("iPad")) os = "iOS";
	else if (ua.includes("Android")) os = "Android";
	let browser = "Browser";
	if (ua.includes("Firefox")) browser = "Firefox";
	else if (ua.includes("Edg")) browser = "Edge";
	else if (ua.includes("Chrome")) browser = "Chrome";
	else if (ua.includes("Safari")) browser = "Safari";
	return `${browser} on ${os}`;
};
function ActiveSessionsCard() {
	const queryClient = useQueryClient();
	const { data: sessions, isLoading } = useQuery({
		queryKey: ["sessions"],
		queryFn: getSessions
	});
	const revokeMutation = useMutation({
		mutationFn: revokeSession,
		onSuccess: () => {
			toast.success("Session revoked");
			queryClient.invalidateQueries({ queryKey: ["sessions"] });
		},
		onError: (err) => toast.error(extractErrorMessage(err, "Failed to revoke session"))
	});
	const revokeAllMutation = useMutation({
		mutationFn: revokeAllSessions,
		onSuccess: () => {
			toast.success("All other sessions revoked");
			queryClient.invalidateQueries({ queryKey: ["sessions"] });
		},
		onError: (err) => toast.error(extractErrorMessage(err, "Failed to revoke all sessions"))
	});
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(Card, {
		className: "flat-card border-2",
		children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)(CardHeader, {
			className: "flex flex-col sm:flex-row sm:items-start justify-between space-y-4 sm:space-y-0",
			children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
				className: "space-y-1.5",
				children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(CardTitle, { children: "Active Sessions" }), /* @__PURE__ */ (0, import_jsx_runtime.jsx)(CardDescription, { children: "Manage devices that are currently logged into your account." })]
			}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(Button, {
				variant: "outline",
				onClick: () => revokeAllMutation.mutate(),
				disabled: revokeAllMutation.isPending || !sessions || sessions.length <= 1,
				className: "shrink-0",
				children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(LogOut, { className: "w-4 h-4 mr-2" }), "Log out all devices"]
			})]
		}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)(CardContent, { children: isLoading ? /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
			className: "flex justify-center p-8",
			children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", { className: "w-8 h-8 border-4 border-slate border-t-transparent rounded-full animate-spin" })
		}) : /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
			className: "space-y-4",
			children: [sessions?.map((session) => /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
				className: "flex flex-col sm:flex-row sm:items-center justify-between p-4 border-2 border-taupe rounded-xl bg-vanilla gap-4 transition-colors",
				children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
					className: "flex items-center gap-4",
					children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
						className: "w-10 h-10 rounded-full bg-sand border-2 border-taupe flex items-center justify-center shrink-0",
						children: session.user_agent?.includes("Mobi") ? /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Smartphone, { className: "w-5 h-5 text-slate" }) : /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Monitor, { className: "w-5 h-5 text-slate" })
					}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", { children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
						className: "flex flex-wrap items-center gap-2 mb-1",
						children: [
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
								className: "font-bold text-slate",
								children: parseUserAgent(session.user_agent)
							}),
							session.auth_provider && /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("span", {
								className: "flex items-center gap-1 px-2 py-0.5 rounded-full bg-slate/10 text-slate text-[10px] uppercase tracking-wider font-bold border-2 border-slate/20",
								children: [
									session.auth_provider.toLowerCase() === "google" && /* @__PURE__ */ (0, import_jsx_runtime.jsx)(GoogleIcon, { className: "w-3 h-3" }),
									session.auth_provider.toLowerCase() === "github" && /* @__PURE__ */ (0, import_jsx_runtime.jsx)(GithubIcon, { className: "w-3 h-3" }),
									session.auth_provider
								]
							}),
							session.is_current && /* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
								className: "px-2 py-0.5 rounded-full bg-sage/20 text-sage text-[10px] uppercase tracking-wider font-bold border-2 border-sage/30",
								children: "Current"
							})
						]
					}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("p", {
						className: "text-sm font-medium text-slate/60",
						children: [
							session.ip_address,
							" • Last active",
							" ",
							session.last_active ? new Date(session.last_active).toLocaleString() : "Unknown"
						]
					})] })]
				}), !session.is_current && /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Button, {
					variant: "destructive",
					onClick: () => revokeMutation.mutate(session.family_id),
					disabled: revokeMutation.isPending,
					children: "Revoke"
				})]
			}, session.family_id)), (!sessions || sessions.length === 0) && /* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
				className: "text-center text-slate/50 font-medium py-4",
				children: "No active sessions found."
			})]
		}) })]
	});
}
function DeleteAccountCard() {
	const logout = useAuthStore((state) => state.logout);
	const navigate = useNavigate();
	const [isOpen, setIsOpen] = (0, import_react.useState)(false);
	const deleteMutation = useMutation({
		mutationFn: deleteMe,
		onSuccess: () => {
			toast.success("Account deleted successfully");
			logout();
			navigate({ to: "/login" });
		},
		onError: (err) => toast.error(extractErrorMessage(err, "Failed to delete account"))
	});
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(Card, {
		className: "border-terracotta overflow-hidden relative",
		children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)(CardHeader, { children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(CardTitle, {
			className: "text-terracotta",
			children: "Danger Zone"
		}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)(CardDescription, { children: "Deactivate your account. You will have 28 days to recover it by logging in again before it is permanently deleted." })] }), /* @__PURE__ */ (0, import_jsx_runtime.jsx)(CardContent, { children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(Dialog$1, {
			open: isOpen,
			onOpenChange: setIsOpen,
			children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(DialogTrigger, {
				asChild: true,
				children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(Button, {
					variant: "destructive",
					children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Trash2, { className: "w-4 h-4 mr-2" }), "Delete Account"]
				})
			}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(DialogContent, {
				className: "sm:max-w-106.25",
				children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)(DialogHeader, { children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)(DialogTitle, {
					className: "text-terracotta flex items-center gap-2",
					children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(TriangleAlert, { className: "w-5 h-5" }), "Delete Account"]
				}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)(DialogDescription, { children: "Are you sure you want to delete your account? Your account will be deactivated and soft-deleted. You can recover it at any time within the next 28 days simply by logging back in. After 28 days, your account and all associated data will be permanently lost." })] }), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(DialogFooter, {
					className: "mt-6 flex gap-3 sm:justify-end",
					children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Button, {
						variant: "outline",
						onClick: () => setIsOpen(false),
						children: "Cancel"
					}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Button, {
						variant: "destructive",
						onClick: () => {
							deleteMutation.mutate();
						},
						disabled: deleteMutation.isPending,
						children: deleteMutation.isPending ? "Deleting..." : "Yes, delete my account"
					})]
				})]
			})]
		}) })]
	});
}
function SecurityTab() {
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
		className: "space-y-8 animate-in fade-in slide-in-from-bottom-2 duration-300",
		children: [
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)(ActiveSessionsCard, {}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)(ChangePasswordCard, {}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)(DeleteAccountCard, {})
		]
	});
}
function SettingsPage() {
	const [activeTab, setActiveTab] = (0, import_react.useState)("profile");
	const user = useAuthStore((state) => state.user);
	const navigate = useNavigate();
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
		className: "max-w-7xl mx-auto flex flex-col md:flex-row gap-8 w-full",
		children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
			className: "w-full md:w-64 shrink-0 flex flex-col gap-8",
			children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
				className: "flex items-center gap-3",
				children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Button, {
					variant: "outline",
					size: "icon",
					className: "border-2 border-slate w-10 h-10 rounded-xl shrink-0",
					onClick: () => navigate({ to: "/dashboard" }),
					children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(ArrowLeft, { className: "w-5 h-5 text-slate" })
				}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", { children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("h1", {
					className: "text-3xl font-display font-bold text-slate tracking-tight",
					children: "Settings"
				}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("p", {
					className: "text-sm font-medium text-slate/60 mt-1 line-clamp-1",
					children: ["Manage preferences for ", user?.name || user?.email]
				})] })]
			}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
				className: "flex flex-col gap-2",
				children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("button", {
					onClick: () => setActiveTab("profile"),
					className: `flex items-center gap-3 px-4 py-3 rounded-xl font-bold transition-all text-left ${activeTab === "profile" ? "bg-slate text-vanilla flat-shadow-taupe border-2 border-slate" : "bg-transparent text-slate hover:bg-taupe/10 border-2 border-transparent hover:border-taupe/20"}`,
					children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(User, { className: "w-5 h-5" }), "Profile"]
				}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("button", {
					onClick: () => setActiveTab("security"),
					className: `flex items-center gap-3 px-4 py-3 rounded-xl font-bold transition-all text-left ${activeTab === "security" ? "bg-slate text-vanilla flat-shadow-taupe border-2 border-slate" : "bg-transparent text-slate hover:bg-taupe/10 border-2 border-transparent hover:border-taupe/20"}`,
					children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Shield, { className: "w-5 h-5" }), "Security"]
				})]
			})]
		}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
			className: "flex-1 min-w-0",
			children: activeTab === "profile" ? /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
				className: "animate-in fade-in slide-in-from-bottom-2 duration-300",
				children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(ProfileTab, {})
			}) : /* @__PURE__ */ (0, import_jsx_runtime.jsx)(SecurityTab, {})
		})]
	});
}
//#endregion
export { SettingsPage as component };
