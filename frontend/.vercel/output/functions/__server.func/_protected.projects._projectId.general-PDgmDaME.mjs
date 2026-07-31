import { o as __toESM } from "./_runtime.mjs";
import { u as require_react } from "./_libs/@floating-ui/react-dom+[...].mjs";
import { i as extractErrorMessage } from "./_ssr/api-client-DJkUESpZ.mjs";
import { n as require_jsx_runtime } from "./_libs/@marsidev/react-turnstile+[...].mjs";
import { Y as Check, b as Save, l as Trash2, s as TriangleAlert, x as RefreshCw } from "./_libs/lucide-react.mjs";
import { n as AnimatePresence, t as motion } from "./_libs/framer-motion.mjs";
import { t as Button } from "./_ssr/button-C-O_Pb_u.mjs";
import { t as Input } from "./_ssr/input-DFi7Mh72.mjs";
import { n as useProject } from "./_ssr/ProjectContext-Dh_Z2-MY.mjs";
import { f as updateProjectEnvironment, p as updateProjectFrontendUrl } from "./_ssr/projects-B5Nezf2L.mjs";
import { n as toast } from "./_libs/sonner.mjs";
import { a as CardHeader, i as CardFooter, n as CardContent, o as CardTitle, r as CardDescription, t as Card } from "./_ssr/card-D2S-3Lsc.mjs";
import { t as Label } from "./_ssr/label-CFPE1x7g.mjs";
import { a as DialogFooter, i as DialogDescription, o as DialogHeader, r as DialogContent, s as DialogTitle, t as Dialog$1 } from "./_ssr/dialog-DYmxbvqX.mjs";
import { t as Route } from "./_protected.projects._projectId.general-BJh6gl1U.mjs";
//#region node_modules/.nitro/vite/services/ssr/assets/_protected.projects._projectId.general-PDgmDaME.js
var import_react = /* @__PURE__ */ __toESM(require_react());
var import_jsx_runtime = require_jsx_runtime();
function GeneralTab() {
	const { projectId } = Route.useParams();
	const { project, fetchProject } = useProject();
	const [environment, setEnvironment] = (0, import_react.useState)("development");
	const [frontendUrl, setFrontendUrl] = (0, import_react.useState)("");
	const [savingGeneral, setSavingGeneral] = (0, import_react.useState)(false);
	const [generalSaved, setGeneralSaved] = (0, import_react.useState)(false);
	const [generalErrors, setGeneralErrors] = (0, import_react.useState)({});
	const [showEnvConfirm, setShowEnvConfirm] = (0, import_react.useState)(false);
	const [isDeleteProjectModalOpen, setIsDeleteProjectModalOpen] = (0, import_react.useState)(false);
	(0, import_react.useEffect)(() => {
		setEnvironment(project.environment);
		setFrontendUrl(project.frontend_url || "");
	}, [project]);
	const handleSaveGeneral = async (e) => {
		e.preventDefault();
		setGeneralErrors({});
		let hasErrors = false;
		const errors = {};
		if (frontendUrl && !frontendUrl.match(/^https?:\/\/.+/)) {
			errors.frontendUrl = "Must be a valid URL starting with http:// or https://";
			hasErrors = true;
		}
		if (hasErrors) {
			setGeneralErrors(errors);
			return;
		}
		setSavingGeneral(true);
		try {
			if (frontendUrl !== project.frontend_url) await updateProjectFrontendUrl(projectId, frontendUrl);
			setGeneralSaved(true);
			await fetchProject(false);
			setTimeout(() => setGeneralSaved(false), 2e3);
		} catch (error) {
			toast.error(extractErrorMessage(error, "Failed to save general settings"));
		} finally {
			setSavingGeneral(false);
		}
	};
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
		className: "animate-in fade-in slide-in-from-bottom-2 duration-300",
		children: [
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)("form", {
				onSubmit: handleSaveGeneral,
				children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(Card, { children: [
					/* @__PURE__ */ (0, import_jsx_runtime.jsxs)(CardHeader, { children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(CardTitle, { children: "General Information" }), /* @__PURE__ */ (0, import_jsx_runtime.jsx)(CardDescription, { children: "Update your project's core details." })] }),
					/* @__PURE__ */ (0, import_jsx_runtime.jsxs)(CardContent, {
						className: "space-y-6",
						children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
							className: "space-y-2",
							children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Label, { children: "Environment" }), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
								className: "flex flex-col sm:flex-row sm:items-center justify-between p-6 border-2 border-slate bg-vanilla rounded-xl transition-colors shadow-[4px_4px_0px_rgba(30,41,59,1)] gap-4",
								children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
									className: "flex-1",
									children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
										className: "flex items-center gap-2",
										children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", { className: `w-3 h-3 rounded-full ${environment === "production" ? "bg-sage" : "bg-ochre"}` }), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("h4", {
											className: "font-bold text-lg capitalize text-slate",
											children: environment
										})]
									}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
										className: "text-sm font-semibold text-slate/70 mt-1 max-w-lg",
										children: environment === "development" ? "Running in dev mode. Limits and caching are relaxed." : "Running in production mode. Strict limits applied."
									})]
								}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(Button, {
									type: "button",
									variant: "outline",
									onClick: () => setShowEnvConfirm(true),
									className: "shrink-0 bg-vanilla",
									children: [
										"Switch to",
										" ",
										environment === "development" ? "Production" : "Development"
									]
								})]
							})]
						}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
							className: "space-y-2",
							children: [
								/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Label, {
									htmlFor: "frontendUrl",
									children: "Frontend Application URL"
								}),
								/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Input, {
									id: "frontendUrl",
									value: frontendUrl,
									onChange: (e) => {
										setFrontendUrl(e.target.value);
										setGeneralErrors({
											...generalErrors,
											frontendUrl: ""
										});
									},
									placeholder: "https://myapp.com",
									className: generalErrors.frontendUrl ? "border-terracotta focus-visible:ring-terracotta" : ""
								}),
								generalErrors.frontendUrl && /* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
									className: "text-sm font-bold text-terracotta",
									children: generalErrors.frontendUrl
								}),
								/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
									className: "text-xs text-slate/70 font-semibold",
									children: "Where users should be redirected after successful authentication flows."
								})
							]
						})]
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)(CardFooter, {
						className: "flex justify-end border-t-2 border-taupe/20 pt-6",
						children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(Button, {
							type: "submit",
							disabled: savingGeneral || generalSaved,
							className: `relative overflow-hidden w-37.5 transition-all duration-300 ${generalSaved ? "bg-sage! text-vanilla! border-sage!" : ""}`,
							children: [
								/* @__PURE__ */ (0, import_jsx_runtime.jsx)(AnimatePresence, {
									mode: "wait",
									children: savingGeneral ? /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(motion.div, {
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
										children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(RefreshCw, { className: "w-4 h-4 animate-spin" }), "Saving..."]
									}, "saving") : generalSaved ? /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(motion.div, {
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
										children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Check, { className: "w-4 h-4" }), "Saved!"]
									}, "saved") : /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(motion.div, {
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
										children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Save, { className: "w-4 h-4" }), "Save Changes"]
									}, "default")
								}),
								/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
									className: "invisible flex items-center justify-center gap-2",
									children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Save, { className: "w-4 h-4" }), "Save Changes"]
								}),
								generalSaved && /* @__PURE__ */ (0, import_jsx_runtime.jsx)(motion.div, {
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
						})
					})
				] })
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsxs)(Card, {
				className: "mt-8 border-terracotta overflow-hidden relative",
				children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)(CardHeader, { children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(CardTitle, {
					className: "text-terracotta",
					children: "Danger Zone"
				}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)(CardDescription, { children: "Deleting this project will permanently remove all associated users, sessions, and configurations." })] }), /* @__PURE__ */ (0, import_jsx_runtime.jsx)(CardContent, { children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(Button, {
					variant: "destructive",
					onClick: () => setIsDeleteProjectModalOpen(true),
					children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Trash2, { className: "w-4 h-4 mr-2" }), "Delete Project"]
				}) })]
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Dialog$1, {
				open: showEnvConfirm,
				onOpenChange: setShowEnvConfirm,
				children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(DialogContent, {
					className: "sm:max-w-106.25 border-2 border-slate bg-vanilla p-0 overflow-hidden shadow-[8px_8px_0px_rgba(30,41,59,1)]",
					children: [
						/* @__PURE__ */ (0, import_jsx_runtime.jsxs)(DialogHeader, {
							className: "p-6 bg-sand border-b-2 border-slate",
							children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(DialogTitle, {
								className: "text-2xl font-black text-slate",
								children: "Change Environment"
							}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(DialogDescription, {
								className: "font-semibold text-slate/70",
								children: [
									"Are you sure you want to switch to",
									" ",
									environment === "development" ? "Production" : "Development",
									"?"
								]
							})]
						}),
						/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
							className: "p-6 text-sm text-slate font-semibold",
							children: [environment === "development" ? /* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", { children: "Switching to production will enforce strict rate limits and caching." }) : /* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", { children: "Switching to development will relax security constraints and rate limits." }), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
								className: "mt-2 text-terracotta",
								children: "This change will take effect immediately."
							})]
						}),
						/* @__PURE__ */ (0, import_jsx_runtime.jsxs)(DialogFooter, {
							className: "p-6 bg-sand border-t-2 border-slate flex justify-end",
							children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Button, {
								type: "button",
								variant: "outline",
								onClick: () => setShowEnvConfirm(false),
								children: "Cancel"
							}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Button, {
								type: "button",
								onClick: async () => {
									const newEnv = environment === "development" ? "production" : "development";
									try {
										await updateProjectEnvironment(projectId, newEnv);
										setEnvironment(newEnv);
										fetchProject(false);
									} catch (error) {
										toast.error(extractErrorMessage(error, "Failed to update environment"));
									} finally {
										setShowEnvConfirm(false);
									}
								},
								children: "Confirm Change"
							})]
						})
					]
				})
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Dialog$1, {
				open: isDeleteProjectModalOpen,
				onOpenChange: setIsDeleteProjectModalOpen,
				children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(DialogContent, {
					className: "sm:max-w-md",
					children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)(DialogHeader, { children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)(DialogTitle, {
						className: "text-2xl font-black text-terracotta flex items-center gap-2",
						children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(TriangleAlert, { className: "w-6 h-6" }), " Delete Project?"]
					}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(DialogDescription, {
						className: "text-slate/80 font-semibold pt-4",
						children: [
							"Are you absolutely sure you want to delete this project? This action is",
							" ",
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)("strong", {
								className: "text-terracotta",
								children: "permanent and cannot be undone"
							}),
							". All users, settings, and keys will be destroyed."
						]
					})] }), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(DialogFooter, {
						className: "mt-6 flex justify-end gap-2",
						children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Button, {
							variant: "outline",
							onClick: () => setIsDeleteProjectModalOpen(false),
							children: "Cancel"
						}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Button, {
							variant: "destructive",
							onClick: () => {
								toast.error("Project deletion is not fully implemented in this demo.");
								setIsDeleteProjectModalOpen(false);
							},
							children: "Yes, Delete Project"
						})]
					})]
				})
			})
		]
	});
}
//#endregion
export { GeneralTab as component };
