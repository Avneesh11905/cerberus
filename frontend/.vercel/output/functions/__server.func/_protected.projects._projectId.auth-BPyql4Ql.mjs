import { o as __toESM } from "./_runtime.mjs";
import { u as require_react } from "./_libs/@floating-ui/react-dom+[...].mjs";
import { t as axios } from "./_libs/axios+[...].mjs";
import { i as extractErrorMessage, t as API_URL } from "./_ssr/api-client-DJkUESpZ.mjs";
import { n as require_jsx_runtime } from "./_libs/@marsidev/react-turnstile+[...].mjs";
import { C as Plus, d as Shield, l as Trash2, s as TriangleAlert, x as RefreshCw } from "./_libs/lucide-react.mjs";
import { n as CopyButton, t as Button } from "./_ssr/button-C-O_Pb_u.mjs";
import { t as Input } from "./_ssr/input-DFi7Mh72.mjs";
import { n as useProject } from "./_ssr/ProjectContext-Dh_Z2-MY.mjs";
import { h as updateProjectOAuth } from "./_ssr/projects-B5Nezf2L.mjs";
import { n as toast } from "./_libs/sonner.mjs";
import { a as CardHeader, n as CardContent, o as CardTitle, r as CardDescription, t as Card } from "./_ssr/card-D2S-3Lsc.mjs";
import { t as Route } from "./_protected.projects._projectId.auth-CfTLHld9.mjs";
import { t as Label } from "./_ssr/label-CFPE1x7g.mjs";
import { a as DialogFooter, i as DialogDescription, o as DialogHeader, r as DialogContent, s as DialogTitle, t as Dialog$1 } from "./_ssr/dialog-DYmxbvqX.mjs";
import { a as SelectValue, i as SelectTrigger, n as SelectContent, r as SelectItem, t as Select$1 } from "./_ssr/select-O4KC7wrJ.mjs";
//#region node_modules/.nitro/vite/services/ssr/assets/_protected.projects._projectId.auth-BPyql4Ql.js
var import_react = /* @__PURE__ */ __toESM(require_react());
var import_jsx_runtime = require_jsx_runtime();
function AuthTab() {
	const { projectId } = Route.useParams();
	const { project, fetchProject } = useProject();
	const [allowedProviders, setAllowedProviders] = (0, import_react.useState)([]);
	const [githubClientId, setGithubClientId] = (0, import_react.useState)("");
	const [githubClientSecret, setGithubClientSecret] = (0, import_react.useState)("");
	const [googleClientId, setGoogleClientId] = (0, import_react.useState)("");
	const [googleClientSecret, setGoogleClientSecret] = (0, import_react.useState)("");
	const [savingAuth, setSavingAuth] = (0, import_react.useState)(false);
	const [authErrors, setAuthErrors] = (0, import_react.useState)({});
	const [isProviderModalOpen, setIsProviderModalOpen] = (0, import_react.useState)(false);
	const [editingProvider, setEditingProvider] = (0, import_react.useState)(null);
	const [modalProvider, setModalProvider] = (0, import_react.useState)("");
	const [modalClientId, setModalClientId] = (0, import_react.useState)("");
	const [modalClientSecret, setModalClientSecret] = (0, import_react.useState)("");
	const [providerToDelete, setProviderToDelete] = (0, import_react.useState)(null);
	(0, import_react.useEffect)(() => {
		const providers = [];
		if (project.oauth_config.github.enabled) {
			providers.push("github");
			setGithubClientId(project.oauth_config.github.client_id || "");
		}
		if (project.oauth_config.google.enabled) {
			providers.push("google");
			setGoogleClientId(project.oauth_config.google.client_id || "");
		}
		setAllowedProviders(providers);
	}, [project]);
	const openAddProviderModal = () => {
		setEditingProvider(null);
		setModalProvider("");
		setModalClientId("");
		setModalClientSecret("");
		setIsProviderModalOpen(true);
	};
	const openEditProviderModal = (provider) => {
		setEditingProvider(provider);
		setModalProvider(provider);
		if (provider === "github") {
			setModalClientId(githubClientId);
			setModalClientSecret(githubClientSecret);
		} else if (provider === "google") {
			setModalClientId(googleClientId);
			setModalClientSecret(googleClientSecret);
		}
		setIsProviderModalOpen(true);
	};
	const handleModalSave = async () => {
		if (!modalProvider) {
			setAuthErrors({ provider: "Please select a provider" });
			return;
		}
		setSavingAuth(true);
		setAuthErrors({});
		const newAllowedProviders = allowedProviders.includes(modalProvider) ? allowedProviders : [...allowedProviders, modalProvider];
		const newGithubClientId = modalProvider === "github" ? modalClientId : githubClientId;
		const newGithubClientSecret = modalProvider === "github" ? modalClientSecret : githubClientSecret;
		const newGoogleClientId = modalProvider === "google" ? modalClientId : googleClientId;
		const newGoogleClientSecret = modalProvider === "google" ? modalClientSecret : googleClientSecret;
		try {
			await updateProjectOAuth(projectId, { oauth_config: {
				github: {
					enabled: newAllowedProviders.includes("github"),
					client_id: newGithubClientId || void 0,
					client_secret: newGithubClientSecret || void 0
				},
				google: {
					enabled: newAllowedProviders.includes("google"),
					client_id: newGoogleClientId || void 0,
					client_secret: newGoogleClientSecret || void 0
				}
			} });
			setAllowedProviders(newAllowedProviders);
			if (modalProvider === "github") {
				setGithubClientId(newGithubClientId);
				setGithubClientSecret("");
			} else if (modalProvider === "google") {
				setGoogleClientId(newGoogleClientId);
				setGoogleClientSecret("");
			}
			setIsProviderModalOpen(false);
			fetchProject(false);
		} catch (error) {
			if (axios.isAxiosError(error) && error.response?.status === 422 && Array.isArray(error.response.data.detail)) {
				const errors = {};
				error.response.data.detail.forEach((d) => {
					if (d.loc.length >= 4 && d.loc[1] === "oauth_config") {
						const provider = d.loc[2];
						const field = d.loc[3];
						errors[`${provider}_${field}`] = d.msg;
					} else {
						const field = d.loc[d.loc.length - 1];
						errors[field] = d.msg;
					}
				});
				setAuthErrors(errors);
			} else toast.error(extractErrorMessage(error, "Failed to update auth settings"));
		} finally {
			setSavingAuth(false);
		}
	};
	const removeProvider = async () => {
		if (!providerToDelete) return;
		setSavingAuth(true);
		const newAllowedProviders = allowedProviders.filter((p) => p !== providerToDelete);
		let ghId = githubClientId || void 0;
		let ghSecret = githubClientSecret || void 0;
		let ggId = googleClientId || void 0;
		let ggSecret = googleClientSecret || void 0;
		if (providerToDelete === "github") {
			ghId = null;
			ghSecret = null;
		} else if (providerToDelete === "google") {
			ggId = null;
			ggSecret = null;
		}
		try {
			await updateProjectOAuth(projectId, { oauth_config: {
				github: {
					enabled: newAllowedProviders.includes("github"),
					client_id: ghId,
					client_secret: ghSecret
				},
				google: {
					enabled: newAllowedProviders.includes("google"),
					client_id: ggId,
					client_secret: ggSecret
				}
			} });
			setAllowedProviders(newAllowedProviders);
			if (providerToDelete === "github") {
				setGithubClientId("");
				setGithubClientSecret("");
			} else if (providerToDelete === "google") {
				setGoogleClientId("");
				setGoogleClientSecret("");
			}
			setProviderToDelete(null);
			fetchProject(false);
		} catch (error) {
			toast.error(extractErrorMessage(error, "Failed to save provider"));
		} finally {
			setSavingAuth(false);
		}
	};
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
		className: "flex flex-col gap-8 w-full animate-in fade-in slide-in-from-bottom-2 duration-300",
		children: [
			/* @__PURE__ */ (0, import_jsx_runtime.jsxs)(Card, { children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)(CardHeader, {
				className: "flex flex-row items-start justify-between space-y-0",
				children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
					className: "space-y-1.5",
					children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(CardTitle, { children: "OAuth Providers" }), /* @__PURE__ */ (0, import_jsx_runtime.jsx)(CardDescription, { children: "Configure third-party social logins for your project." })]
				}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(Button, {
					type: "button",
					onClick: openAddProviderModal,
					className: "gap-2",
					children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Plus, { className: "w-4 h-4" }), " Add Provider"]
				})]
			}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)(CardContent, {
				className: "space-y-6",
				children: allowedProviders.length === 0 ? /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
					className: "flex flex-col items-center justify-center p-12 border-2 border-dashed border-taupe bg-taupe/5 rounded-xl",
					children: [
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Shield, { className: "w-12 h-12 text-taupe mb-4" }),
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)("h3", {
							className: "text-lg font-bold text-slate mb-2",
							children: "No Providers Configured"
						}),
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
							className: "text-sm font-semibold text-slate/70 text-center max-w-md",
							children: "You haven't added any social login providers yet. Add a provider to allow your users to sign in with their existing accounts."
						})
					]
				}) : /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
					className: "space-y-4",
					children: allowedProviders.map((provider) => /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
						className: "flex flex-col sm:flex-row sm:items-center justify-between p-5 border-2 border-slate rounded-xl bg-vanilla shadow-[4px_4px_0px_rgba(30,41,59,1)] gap-4",
						children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
							className: "flex items-center gap-4",
							children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
								className: "flex-1",
								children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("h4", {
									className: "text-lg font-black text-slate capitalize",
									children: [provider, " Login"]
								}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("p", {
									className: "text-sm font-semibold text-slate/70",
									children: [
										"Users can sign in with their",
										" ",
										provider.charAt(0).toUpperCase() + provider.slice(1),
										" ",
										"accounts."
									]
								})]
							}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
								className: "flex flex-col gap-1 mt-3 p-3 bg-taupe/10 border-2 border-slate/10 rounded-xl",
								children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
									className: "text-xs font-bold text-slate/70 uppercase",
									children: "Callback URL"
								}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
									className: "flex items-center gap-2",
									children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("code", {
										className: "flex-1 text-xs font-mono bg-vanilla px-2 py-1.5 rounded-lg border border-slate/10 break-all",
										children: `${API_URL}/auth/callback/${provider}`
									}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)(CopyButton, { value: `${API_URL}/auth/callback/${provider}` })]
								})]
							})]
						}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
							className: "flex items-center gap-2 shrink-0",
							children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Button, {
								type: "button",
								variant: "outline",
								size: "sm",
								onClick: () => openEditProviderModal(provider),
								children: "Edit"
							}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Button, {
								type: "button",
								variant: "destructive",
								size: "sm",
								onClick: () => setProviderToDelete(provider),
								disabled: savingAuth,
								children: savingAuth && providerToDelete === provider ? /* @__PURE__ */ (0, import_jsx_runtime.jsx)(RefreshCw, { className: "w-4 h-4 animate-spin" }) : /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Trash2, { className: "w-4 h-4" })
							})]
						})]
					}, provider))
				})
			})] }),
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Dialog$1, {
				open: isProviderModalOpen,
				onOpenChange: setIsProviderModalOpen,
				children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(DialogContent, {
					className: "sm:max-w-106.25 border-2 border-slate bg-vanilla p-0 overflow-hidden shadow-[8px_8px_0px_rgba(30,41,59,1)]",
					children: [
						/* @__PURE__ */ (0, import_jsx_runtime.jsxs)(DialogHeader, {
							className: "p-6 bg-sand border-b-2 border-slate",
							children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(DialogTitle, {
								className: "text-2xl font-black text-slate",
								children: editingProvider ? `Edit ${editingProvider.charAt(0).toUpperCase() + editingProvider.slice(1)}` : "Add Provider"
							}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)(DialogDescription, {
								className: "font-semibold text-slate/70",
								children: editingProvider ? "Update the OAuth credentials." : "Select a provider and enter the credentials to enable social login."
							})]
						}),
						/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
							className: "p-6 space-y-4",
							children: [
								!editingProvider && /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
									className: "space-y-2",
									children: [
										/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Label, { children: "Provider" }),
										/* @__PURE__ */ (0, import_jsx_runtime.jsxs)(Select$1, {
											value: modalProvider,
											onValueChange: (val) => {
												setModalProvider(val);
												setAuthErrors({
													...authErrors,
													provider: ""
												});
											},
											children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(SelectTrigger, {
												className: authErrors.provider ? "border-terracotta focus:ring-terracotta" : "",
												children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(SelectValue, { placeholder: "Select a provider" })
											}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(SelectContent, { children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(SelectItem, {
												value: "github",
												disabled: allowedProviders.includes("github"),
												children: "GitHub"
											}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)(SelectItem, {
												value: "google",
												disabled: allowedProviders.includes("google"),
												children: "Google"
											})] })]
										}),
										authErrors.provider && /* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
											className: "text-sm font-bold text-terracotta",
											children: authErrors.provider
										})
									]
								}),
								modalProvider && /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
									className: "space-y-2 pb-2 mb-2 border-b-2 border-slate/10",
									children: [
										/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Label, { children: "Callback URL" }),
										/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
											className: "flex items-center justify-between gap-2 p-2 bg-taupe/10 border-2 border-slate/20 rounded-xl",
											children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("code", {
												className: "text-xs font-mono truncate max-w-70",
												children: `http://localhost:8000/v1/auth/callback/${modalProvider}`
											}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)(CopyButton, { value: `http://localhost:8000/v1/auth/callback/${modalProvider}` })]
										}),
										/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("p", {
											className: "text-xs font-semibold text-slate/60",
											children: [
												"Set this as the Authorized Redirect URI in your",
												" ",
												modalProvider.charAt(0).toUpperCase() + modalProvider.slice(1),
												" ",
												"console."
											]
										})
									]
								}),
								/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
									className: "space-y-2",
									children: [
										/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Label, { children: "Client ID" }),
										/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Input, {
											value: modalClientId,
											onChange: (e) => {
												setModalClientId(e.target.value);
												if (modalProvider) setAuthErrors({
													...authErrors,
													[`${modalProvider}_client_id`]: ""
												});
											},
											placeholder: "Client ID",
											className: authErrors[`${modalProvider}_client_id`] ? "border-terracotta focus-visible:ring-terracotta" : ""
										}),
										authErrors[`${modalProvider}_client_id`] && /* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
											className: "text-sm font-bold text-terracotta",
											children: authErrors[`${modalProvider}_client_id`]
										})
									]
								}),
								/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
									className: "space-y-2",
									children: [
										/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Label, { children: "Client Secret" }),
										/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Input, {
											type: "password",
											value: modalClientSecret,
											onChange: (e) => {
												setModalClientSecret(e.target.value);
												if (modalProvider) setAuthErrors({
													...authErrors,
													[`${modalProvider}_client_secret`]: ""
												});
											},
											placeholder: "Client Secret",
											className: authErrors[`${modalProvider}_client_secret`] ? "border-terracotta focus-visible:ring-terracotta" : ""
										}),
										authErrors[`${modalProvider}_client_secret`] && /* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
											className: "text-sm font-bold text-terracotta",
											children: authErrors[`${modalProvider}_client_secret`]
										})
									]
								})
							]
						}),
						/* @__PURE__ */ (0, import_jsx_runtime.jsxs)(DialogFooter, {
							className: "p-6 bg-sand border-t-2 border-slate flex justify-end",
							children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Button, {
								type: "button",
								variant: "outline",
								onClick: () => setIsProviderModalOpen(false),
								children: "Cancel"
							}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Button, {
								type: "button",
								onClick: handleModalSave,
								disabled: savingAuth,
								children: savingAuth ? /* @__PURE__ */ (0, import_jsx_runtime.jsx)(RefreshCw, { className: "w-4 h-4 animate-spin" }) : editingProvider ? "Save Changes" : "Add Provider"
							})]
						})
					]
				})
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Dialog$1, {
				open: !!providerToDelete,
				onOpenChange: (open) => !open && setProviderToDelete(null),
				children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(DialogContent, {
					className: "sm:max-w-md",
					children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)(DialogHeader, { children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)(DialogTitle, {
						className: "text-2xl font-black text-terracotta flex items-center gap-2",
						children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(TriangleAlert, { className: "w-6 h-6" }), " Remove Provider?"]
					}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(DialogDescription, {
						className: "text-slate/80 font-semibold pt-4",
						children: [
							"Are you sure you want to remove the",
							" ",
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)("strong", {
								className: "capitalize",
								children: providerToDelete
							}),
							" ",
							"provider? Users relying on this provider will no longer be able to log in."
						]
					})] }), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(DialogFooter, {
						className: "mt-6 flex justify-end gap-2",
						children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Button, {
							variant: "outline",
							onClick: () => setProviderToDelete(null),
							children: "Cancel"
						}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(Button, {
							variant: "destructive",
							onClick: removeProvider,
							disabled: savingAuth,
							children: [savingAuth ? /* @__PURE__ */ (0, import_jsx_runtime.jsx)(RefreshCw, { className: "w-4 h-4 animate-spin mr-2" }) : null, "Remove"]
						})]
					})]
				})
			})
		]
	});
}
//#endregion
export { AuthTab as component };
