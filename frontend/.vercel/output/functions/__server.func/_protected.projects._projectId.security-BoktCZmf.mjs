import { o as __toESM } from "./_runtime.mjs";
import { u as require_react } from "./_libs/@floating-ui/react-dom+[...].mjs";
import { t as axios } from "./_libs/axios+[...].mjs";
import { i as extractErrorMessage } from "./_ssr/api-client-DJkUESpZ.mjs";
import { n as handleDownloadPem } from "./_ssr/utils-DgjCne0W.mjs";
import { n as require_jsx_runtime } from "./_libs/@marsidev/react-turnstile+[...].mjs";
import { C as Plus, L as Eye, R as EyeOff, Y as Check, l as Trash2, s as TriangleAlert, x as RefreshCw } from "./_libs/lucide-react.mjs";
import { n as AnimatePresence, t as motion } from "./_libs/framer-motion.mjs";
import { n as CopyButton, r as DownloadButton, t as Button } from "./_ssr/button-C-O_Pb_u.mjs";
import { t as Input } from "./_ssr/input-DFi7Mh72.mjs";
import { n as useProject } from "./_ssr/ProjectContext-Dh_Z2-MY.mjs";
import { g as updateProjectOrigins, l as rotateApiKey, u as rotateJwtSecret } from "./_ssr/projects-B5Nezf2L.mjs";
import { n as toast } from "./_libs/sonner.mjs";
import { a as CardHeader, n as CardContent, o as CardTitle, r as CardDescription, t as Card } from "./_ssr/card-D2S-3Lsc.mjs";
import { t as Label } from "./_ssr/label-CFPE1x7g.mjs";
import { a as DialogFooter, i as DialogDescription, o as DialogHeader, r as DialogContent, s as DialogTitle, t as Dialog$1 } from "./_ssr/dialog-DYmxbvqX.mjs";
import { t as Route } from "./_protected.projects._projectId.security-DTa62ddj.mjs";
//#region node_modules/.nitro/vite/services/ssr/assets/_protected.projects._projectId.security-BoktCZmf.js
var import_react = /* @__PURE__ */ __toESM(require_react());
var import_jsx_runtime = require_jsx_runtime();
function SecurityTab() {
	const { projectId } = Route.useParams();
	const { project, publicKey, fetchProject } = useProject();
	const [allowedOrigins, setAllowedOrigins] = (0, import_react.useState)([]);
	const [newOrigin, setNewOrigin] = (0, import_react.useState)("");
	const [originError, setOriginError] = (0, import_react.useState)("");
	const [savingOrigins, setSavingOrigins] = (0, import_react.useState)(false);
	const [originToDelete, setOriginToDelete] = (0, import_react.useState)(null);
	const [isRotateApiConfirmOpen, setIsRotateApiConfirmOpen] = (0, import_react.useState)(false);
	const [isApiKeyModalOpen, setIsApiKeyModalOpen] = (0, import_react.useState)(false);
	const [rotatedApiKey, setRotatedApiKey] = (0, import_react.useState)("");
	const [isRotateRsaConfirmOpen, setIsRotateRsaConfirmOpen] = (0, import_react.useState)(false);
	const [rsaRotated, setRsaRotated] = (0, import_react.useState)(false);
	const [isPublicKeyVisible, setIsPublicKeyVisible] = (0, import_react.useState)(false);
	(0, import_react.useEffect)(() => {
		setAllowedOrigins(project.allowed_origins);
	}, [project]);
	const handleAddOrigin = async () => {
		if (!newOrigin.trim()) return;
		try {
			new URL(newOrigin);
		} catch {
			setOriginError("Must be a valid URL (e.g., https://example.com)");
			return;
		}
		if (allowedOrigins.length >= 5) {
			setOriginError("Maximum of 5 origins allowed.");
			return;
		}
		setSavingOrigins(true);
		setOriginError("");
		const originWithoutPath = new URL(newOrigin).origin;
		const updatedOrigins = [...allowedOrigins, originWithoutPath];
		try {
			await updateProjectOrigins(projectId, updatedOrigins);
			setAllowedOrigins(updatedOrigins);
			setNewOrigin("");
			fetchProject(false);
		} catch (error) {
			if (axios.isAxiosError(error) && error.response?.status === 422 && error.response.data.detail[0]?.msg) setOriginError(error.response.data.detail[0].msg);
			else toast.error(extractErrorMessage(error, "Failed to add origin"));
		} finally {
			setSavingOrigins(false);
		}
	};
	const handleRemoveOrigin = async () => {
		if (!originToDelete) return;
		const updatedOrigins = allowedOrigins.filter((o) => o !== originToDelete);
		setSavingOrigins(true);
		try {
			await updateProjectOrigins(projectId, updatedOrigins);
			setAllowedOrigins(updatedOrigins);
			setOriginToDelete(null);
			fetchProject(false);
		} catch (err) {
			toast.error(extractErrorMessage(err, "Failed to remove origin"));
		} finally {
			setSavingOrigins(false);
		}
	};
	const handleRotateApiKey = async () => {
		try {
			const data = await rotateApiKey(projectId);
			setRotatedApiKey(data.api_key);
			setIsRotateApiConfirmOpen(false);
			setIsApiKeyModalOpen(true);
			fetchProject(false);
		} catch (err) {
			toast.error(extractErrorMessage(err, "Failed to rotate API Key"));
		}
	};
	const handleRotateJwtSecret = async () => {
		try {
			await rotateJwtSecret(projectId);
			setIsRotateRsaConfirmOpen(false);
			setRsaRotated(true);
			setTimeout(() => setRsaRotated(false), 2e3);
			fetchProject(false);
		} catch (err) {
			toast.error(extractErrorMessage(err, "Failed to rotate RSA Keys"));
		}
	};
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
		className: "flex flex-col gap-6 w-full animate-in fade-in slide-in-from-bottom-2 duration-300",
		children: [
			/* @__PURE__ */ (0, import_jsx_runtime.jsxs)(Card, { children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)(CardHeader, { children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(CardTitle, { children: "CORS & Origins" }), /* @__PURE__ */ (0, import_jsx_runtime.jsx)(CardDescription, { children: "Control which domains can make API requests using this project's keys." })] }), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(CardContent, {
				className: "space-y-4",
				children: [
					/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
						className: "flex gap-2 items-center mb-2",
						children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Input, {
							placeholder: "https://myapp.com",
							value: newOrigin,
							onChange: (e) => {
								setNewOrigin(e.target.value);
								setOriginError("");
							},
							onKeyDown: (e) => e.key === "Enter" && handleAddOrigin(),
							disabled: allowedOrigins.length >= 5,
							className: originError ? "border-terracotta focus-visible:ring-terracotta" : ""
						}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(Button, {
							type: "button",
							variant: "primary",
							onClick: handleAddOrigin,
							disabled: savingOrigins || !newOrigin.trim() || allowedOrigins.length >= 5,
							className: "shrink-0",
							children: [savingOrigins ? /* @__PURE__ */ (0, import_jsx_runtime.jsx)(RefreshCw, { className: "w-4 h-4 animate-spin mr-2" }) : /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Plus, { className: "w-4 h-4 mr-2" }), "Add Origin"]
						})]
					}),
					originError && /* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
						className: "text-sm font-bold text-terracotta mb-2",
						children: originError
					}),
					allowedOrigins.length >= 5 && /* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
						className: "text-sm font-bold text-terracotta mb-6",
						children: "Maximum of 5 origins allowed."
					}),
					allowedOrigins.length < 5 && /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", { className: "mb-6" }),
					/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
						className: "space-y-3",
						children: [allowedOrigins.map((origin, idx) => /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
							className: "flex justify-between items-center bg-vanilla border-2 border-slate shadow-[2px_2px_0px_rgba(30,41,59,1)] p-3 rounded-xl",
							children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
								className: "font-mono text-sm font-bold text-slate px-2",
								children: origin
							}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Button, {
								type: "button",
								variant: "destructive",
								size: "icon",
								className: "h-8 w-8 shrink-0",
								onClick: () => setOriginToDelete(origin),
								disabled: savingOrigins,
								children: savingOrigins && originToDelete === origin ? /* @__PURE__ */ (0, import_jsx_runtime.jsx)(RefreshCw, { className: "w-4 h-4 animate-spin" }) : /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Trash2, { className: "w-4 h-4" })
							})]
						}, idx)), allowedOrigins.length === 0 && /* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
							className: "text-sm font-semibold text-slate/50 p-6 border-2 border-dashed border-slate/30 rounded-xl bg-taupe/5 text-center",
							children: "No origins allowed yet."
						})]
					})
				]
			})] }),
			/* @__PURE__ */ (0, import_jsx_runtime.jsxs)(Card, { children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)(CardHeader, { children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(CardTitle, { children: "Key Management" }), /* @__PURE__ */ (0, import_jsx_runtime.jsx)(CardDescription, { children: "Rotate your API keys and JWT signing secrets." })] }), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(CardContent, {
				className: "space-y-6",
				children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
					className: "flex flex-col sm:flex-row sm:items-center justify-between p-6 border-2 border-slate bg-vanilla rounded-xl shadow-[4px_4px_0px_rgba(30,41,59,1)] gap-4",
					children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
						className: "flex-1",
						children: [
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)("h4", {
								className: "font-bold text-slate text-lg",
								children: "API Key"
							}),
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
								className: "text-sm font-semibold text-slate/70 mt-1 max-w-lg",
								children: "Used for backend API integrations. The plaintext key is only shown once when rotated."
							}),
							project.api_key_last_rotated && /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("p", {
								className: "text-xs font-semibold text-slate/50 mt-2",
								children: [
									"Last rotated:",
									" ",
									new Date(project.api_key_last_rotated).toLocaleString()
								]
							})
						]
					}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(Button, {
						variant: "destructive",
						onClick: () => setIsRotateApiConfirmOpen(true),
						className: "gap-2 shrink-0",
						children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(RefreshCw, { className: "w-4 h-4" }), " Rotate Key"]
					})]
				}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
					className: "flex flex-col p-6 border-2 border-slate bg-vanilla rounded-xl shadow-[4px_4px_0px_rgba(30,41,59,1)] gap-4",
					children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
						className: "flex flex-col sm:flex-row sm:items-start justify-between gap-4",
						children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
							className: "flex-1",
							children: [
								/* @__PURE__ */ (0, import_jsx_runtime.jsx)("h4", {
									className: "font-bold text-slate text-lg",
									children: "JWT Public Key (RSA PEM)"
								}),
								/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
									className: "text-sm font-semibold text-slate/70 mt-1 max-w-lg",
									children: "Used to verify the signatures of JWTs issued by Cerberus to your users. This is safe to share."
								}),
								project.jwt_secret_last_rotated && /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("p", {
									className: "text-xs font-semibold text-slate/50 mt-2",
									children: [
										"Last rotated:",
										" ",
										new Date(project.jwt_secret_last_rotated).toLocaleString()
									]
								})
							]
						}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(Button, {
							variant: "destructive",
							onClick: () => setIsRotateRsaConfirmOpen(true),
							disabled: rsaRotated,
							className: `gap-2 shrink-0 relative overflow-hidden transition-all duration-300 w-35 ${rsaRotated ? "bg-terracotta! text-vanilla! border-terracotta!" : ""}`,
							children: [
								/* @__PURE__ */ (0, import_jsx_runtime.jsx)(AnimatePresence, {
									mode: "wait",
									children: rsaRotated ? /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(motion.div, {
										initial: {
											opacity: 0,
											scale: .5
										},
										animate: {
											opacity: 1,
											scale: 1
										},
										exit: {
											opacity: 0,
											scale: .8
										},
										className: "flex items-center justify-center gap-2 absolute inset-0",
										children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Check, { className: "w-4 h-4" }), "Rotated!"]
									}, "rotated") : /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(motion.div, {
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
										className: "flex items-center justify-center gap-2 absolute inset-0",
										children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(RefreshCw, { className: "w-4 h-4" }), " Rotate Keys"]
									}, "default")
								}),
								/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
									className: "invisible flex items-center justify-center gap-2",
									children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(RefreshCw, { className: "w-4 h-4" }), " Rotate Keys"]
								}),
								rsaRotated && /* @__PURE__ */ (0, import_jsx_runtime.jsx)(motion.div, {
									initial: {
										scale: 0,
										opacity: .4
									},
									animate: {
										scale: 3,
										opacity: 0
									},
									transition: {
										duration: .6,
										ease: "easeOut"
									},
									className: "absolute inset-0 bg-vanilla rounded-full origin-center pointer-events-none"
								})
							]
						})]
					}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
						className: "mt-2",
						children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
							className: "relative",
							children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("pre", {
								className: "w-full min-h-30 border-2 border-slate bg-taupe/10 px-4 py-4 text-xs font-mono rounded-xl overflow-hidden whitespace-pre-wrap break-all leading-relaxed",
								children: isPublicKeyVisible ? publicKey : publicKey.replace(/(?<=-----BEGIN PUBLIC KEY-----\n)[\s\S]*?(?=\n-----END PUBLIC KEY-----)/, "****************************************************************\n****************************************************************\n****************************************************************\n****************************************************************")
							}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
								className: "absolute top-2 right-2 flex gap-3",
								children: [
									/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Button, {
										variant: "outline",
										size: "icon",
										className: "h-8 w-8 bg-vanilla shrink-0",
										onClick: () => setIsPublicKeyVisible(!isPublicKeyVisible),
										title: isPublicKeyVisible ? "Hide Key" : "Show Key",
										children: isPublicKeyVisible ? /* @__PURE__ */ (0, import_jsx_runtime.jsx)(EyeOff, { className: "w-4 h-4" }) : /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Eye, { className: "w-4 h-4" })
									}),
									/* @__PURE__ */ (0, import_jsx_runtime.jsx)(CopyButton, {
										value: publicKey,
										variant: "outline",
										size: "icon",
										className: "h-8 w-8 bg-vanilla shrink-0",
										title: "Copy Key"
									}),
									/* @__PURE__ */ (0, import_jsx_runtime.jsx)(DownloadButton, {
										onDownload: () => handleDownloadPem(publicKey, `${project.name.replace(/\s+/g, "_").toLowerCase()}_public_key.pem`),
										variant: "outline",
										size: "icon",
										className: "h-8 w-8 bg-vanilla shrink-0",
										title: "Download PEM"
									})
								]
							})]
						})
					})]
				})]
			})] }),
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Dialog$1, {
				open: !!originToDelete,
				onOpenChange: (open) => !open && setOriginToDelete(null),
				children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(DialogContent, {
					className: "sm:max-w-md",
					children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)(DialogHeader, { children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)(DialogTitle, {
						className: "text-2xl font-black text-terracotta flex items-center gap-2",
						children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(TriangleAlert, { className: "w-6 h-6" }), " Remove Origin?"]
					}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(DialogDescription, {
						className: "text-slate/80 font-semibold pt-4",
						children: [
							"Are you sure you want to remove",
							" ",
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)("strong", {
								className: "break-all",
								children: originToDelete
							}),
							" from your allowed origins? This domain will immediately lose access to the API."
						]
					})] }), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(DialogFooter, {
						className: "mt-6 flex justify-end gap-2",
						children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Button, {
							variant: "outline",
							onClick: () => setOriginToDelete(null),
							children: "Cancel"
						}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(Button, {
							variant: "destructive",
							onClick: handleRemoveOrigin,
							disabled: savingOrigins,
							children: [savingOrigins ? /* @__PURE__ */ (0, import_jsx_runtime.jsx)(RefreshCw, { className: "w-4 h-4 animate-spin mr-2" }) : null, "Remove"]
						})]
					})]
				})
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Dialog$1, {
				open: isRotateApiConfirmOpen,
				onOpenChange: setIsRotateApiConfirmOpen,
				children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(DialogContent, {
					className: "sm:max-w-md",
					children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)(DialogHeader, { children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)(DialogTitle, {
						className: "text-2xl font-black text-terracotta flex items-center gap-2",
						children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(TriangleAlert, { className: "w-6 h-6" }), " Rotate API Key?"]
					}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(DialogDescription, {
						className: "text-slate/80 font-semibold pt-4",
						children: [
							"Are you sure you want to rotate the API Key? This action will",
							" ",
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)("strong", {
								className: "text-terracotta",
								children: "instantly break"
							}),
							" any existing backend integrations using the old key."
						]
					})] }), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(DialogFooter, {
						className: "mt-6 flex justify-end gap-2",
						children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Button, {
							variant: "outline",
							onClick: () => setIsRotateApiConfirmOpen(false),
							children: "Cancel"
						}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Button, {
							variant: "destructive",
							onClick: handleRotateApiKey,
							children: "Yes, Rotate Key"
						})]
					})]
				})
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Dialog$1, {
				open: isRotateRsaConfirmOpen,
				onOpenChange: setIsRotateRsaConfirmOpen,
				children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(DialogContent, {
					className: "sm:max-w-md",
					children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)(DialogHeader, { children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)(DialogTitle, {
						className: "text-2xl font-black text-terracotta flex items-center gap-2",
						children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(TriangleAlert, { className: "w-6 h-6" }), " Rotate RSA Keys?"]
					}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(DialogDescription, {
						className: "text-slate/80 font-semibold pt-4",
						children: [
							"Are you sure you want to rotate the RSA Keys? This will",
							" ",
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)("strong", {
								className: "text-terracotta",
								children: "instantly invalidate"
							}),
							" ",
							"all active user sessions for this project."
						]
					})] }), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(DialogFooter, {
						className: "mt-6 flex justify-end gap-2",
						children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Button, {
							variant: "outline",
							onClick: () => setIsRotateRsaConfirmOpen(false),
							children: "Cancel"
						}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Button, {
							variant: "destructive",
							onClick: handleRotateJwtSecret,
							children: "Yes, Rotate Keys"
						})]
					})]
				})
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Dialog$1, {
				open: isApiKeyModalOpen,
				onOpenChange: setIsApiKeyModalOpen,
				children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(DialogContent, {
					className: "sm:max-w-xl",
					children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
						className: "space-y-6",
						children: [
							/* @__PURE__ */ (0, import_jsx_runtime.jsxs)(DialogHeader, { children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(DialogTitle, {
								className: "text-2xl font-black text-slate flex items-center gap-2",
								children: "API Key Rotated!"
							}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(DialogDescription, {
								className: "text-terracotta font-bold flex items-start gap-2 mt-2 bg-terracotta/10 p-3 border-2 border-terracotta rounded-xl",
								children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(TriangleAlert, { className: "w-5 h-5 shrink-0 mt-0.5" }), "Warning: This is the ONLY time you will see this new API Key. Please copy it or download the JSON file now."]
							})] }),
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
								className: "space-y-4",
								children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
									className: "space-y-2",
									children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Label, {
										className: "text-slate font-bold",
										children: "New API Key (Keep Secret)"
									}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
										className: "flex gap-2",
										children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Input, {
											value: rotatedApiKey,
											readOnly: true,
											className: "font-mono bg-taupe/10 border-2 border-slate/20 text-slate"
										}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)(CopyButton, {
											value: rotatedApiKey,
											className: "h-10 w-10"
										})]
									})]
								})
							}),
							/* @__PURE__ */ (0, import_jsx_runtime.jsxs)(DialogFooter, {
								className: "sm:justify-between flex-row items-center",
								children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(DownloadButton, {
									size: "default",
									variant: "outline",
									onDownload: () => {
										const blob = new Blob([JSON.stringify({
											project_id: project.id,
											project_name: project.name,
											api_key: rotatedApiKey,
											rotated_at: (/* @__PURE__ */ new Date()).toISOString()
										}, null, 2)], { type: "application/json" });
										const url = URL.createObjectURL(blob);
										const a = document.createElement("a");
										a.href = url;
										a.download = `cerberus_${project.name.replace(/\s+/g, "_").toLowerCase()}_api_key.json`;
										document.body.appendChild(a);
										a.click();
										document.body.removeChild(a);
										URL.revokeObjectURL(url);
									},
									className: "gap-2",
									title: "Download JSON",
									children: "Download JSON"
								}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Button, {
									onClick: () => setIsApiKeyModalOpen(false),
									children: "I've stored it safely"
								})]
							})
						]
					})
				})
			})
		]
	});
}
//#endregion
export { SecurityTab as component };
