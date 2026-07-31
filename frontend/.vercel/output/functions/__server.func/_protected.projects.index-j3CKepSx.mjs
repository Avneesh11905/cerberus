import { o as __toESM } from "./_runtime.mjs";
import { u as require_react } from "./_libs/@floating-ui/react-dom+[...].mjs";
import { i as extractErrorMessage } from "./_ssr/api-client-DJkUESpZ.mjs";
import { n as require_jsx_runtime } from "./_libs/@marsidev/react-turnstile+[...].mjs";
import { $ as CalendarDays, C as Plus, K as ChevronRight, L as Eye, R as EyeOff, S as RefreshCcw, T as Pen, V as Copy, l as Trash2, nt as Activity, p as ShieldCheck, q as ChevronLeft, s as TriangleAlert, tt as ArrowLeft } from "./_libs/lucide-react.mjs";
import { a as ContextMenuTrigger, i as ContextMenuSeparator, n as ContextMenuContent, r as ContextMenuItem, t as ContextMenu$1 } from "./_ssr/context-menu-Dw6tfCxT.mjs";
import { y as useRouter } from "./_libs/@tanstack/react-router+[...].mjs";
import { n as CopyButton, r as DownloadButton, t as Button } from "./_ssr/button-C-O_Pb_u.mjs";
import { t as Input } from "./_ssr/input-DFi7Mh72.mjs";
import { m as updateProjectName, n as deleteProject, s as getProjects, t as createProject } from "./_ssr/projects-B5Nezf2L.mjs";
import { n as toast } from "./_libs/sonner.mjs";
import { a as CardHeader, n as CardContent, o as CardTitle, t as Card } from "./_ssr/card-D2S-3Lsc.mjs";
import { t as Label } from "./_ssr/label-CFPE1x7g.mjs";
import { a as DialogFooter, c as DialogTrigger, i as DialogDescription, n as DialogClose, o as DialogHeader, r as DialogContent, s as DialogTitle, t as Dialog$1 } from "./_ssr/dialog-DYmxbvqX.mjs";
import { t as Skeleton } from "./_ssr/skeleton-Jd4K_fyE.mjs";
//#region node_modules/.nitro/vite/services/ssr/assets/_protected.projects.index-j3CKepSx.js
var import_react = /* @__PURE__ */ __toESM(require_react());
var import_jsx_runtime = require_jsx_runtime();
function ProjectsIndexPage() {
	const router = useRouter();
	const [projects, setProjects] = (0, import_react.useState)([]);
	const [loading, setLoading] = (0, import_react.useState)(true);
	const [page, setPage] = (0, import_react.useState)(1);
	const [size] = (0, import_react.useState)(20);
	const [total, setTotal] = (0, import_react.useState)(0);
	const [isDialogOpen, setIsDialogOpen] = (0, import_react.useState)(false);
	const [newProjectName, setNewProjectName] = (0, import_react.useState)("");
	const [creating, setCreating] = (0, import_react.useState)(false);
	const [createdCredentials, setCreatedCredentials] = (0, import_react.useState)(null);
	const [showApiKey, setShowApiKey] = (0, import_react.useState)(false);
	const [showPublicKey, setShowPublicKey] = (0, import_react.useState)(false);
	const [projectToRename, setProjectToRename] = (0, import_react.useState)(null);
	const [renameValue, setRenameValue] = (0, import_react.useState)("");
	const [isRenaming, setIsRenaming] = (0, import_react.useState)(false);
	const [projectToDelete, setProjectToDelete] = (0, import_react.useState)(null);
	const [isDeleting, setIsDeleting] = (0, import_react.useState)(false);
	const handleDownloadApiKey = () => {
		if (!createdCredentials) return;
		const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify({ api_key: createdCredentials.api_key }, null, 2));
		const downloadAnchorNode = document.createElement("a");
		downloadAnchorNode.setAttribute("href", dataStr);
		downloadAnchorNode.setAttribute("download", `${createdCredentials.name.replace(/\s+/g, "_").toLowerCase()}_api_key.json`);
		document.body.appendChild(downloadAnchorNode);
		downloadAnchorNode.click();
		downloadAnchorNode.remove();
	};
	const handleDownloadPublicKey = () => {
		if (!createdCredentials) return;
		const dataStr = "data:application/x-pem-file;charset=utf-8," + encodeURIComponent(createdCredentials.public_key);
		const downloadAnchorNode = document.createElement("a");
		downloadAnchorNode.setAttribute("href", dataStr);
		downloadAnchorNode.setAttribute("download", `${createdCredentials.name.replace(/\s+/g, "_").toLowerCase()}_public_key.pem`);
		document.body.appendChild(downloadAnchorNode);
		downloadAnchorNode.click();
		downloadAnchorNode.remove();
	};
	const fetchProjects = async () => {
		try {
			setLoading(true);
			const data = await getProjects({
				page,
				size
			});
			setProjects(data.items);
			setTotal(data.total);
		} catch (err) {
			toast.error(extractErrorMessage(err, "Failed to fetch projects"));
		} finally {
			setLoading(false);
		}
	};
	(0, import_react.useEffect)(() => {
		fetchProjects();
	}, [page, size]);
	const handleCreateProject = async (e) => {
		e.preventDefault();
		if (!newProjectName.trim()) return;
		setCreating(true);
		try {
			const res = await createProject({
				name: newProjectName,
				environment: "development"
			});
			setCreatedCredentials({
				api_key: res.api_key,
				public_key: res.public_key,
				name: res.name
			});
			setShowApiKey(false);
			setShowPublicKey(false);
			setNewProjectName("");
			fetchProjects();
		} catch (err) {
			toast.error(extractErrorMessage(err, "Failed to create project"));
		} finally {
			setCreating(false);
		}
	};
	const handleRenameProject = async (e) => {
		e.preventDefault();
		if (!projectToRename || !renameValue.trim()) return;
		setIsRenaming(true);
		try {
			await updateProjectName(projectToRename.id, renameValue.trim());
			setProjectToRename(null);
			fetchProjects();
		} catch (err) {
			toast.error(extractErrorMessage(err, "Failed to rename project"));
		} finally {
			setIsRenaming(false);
		}
	};
	const handleDeleteProject = async () => {
		if (!projectToDelete) return;
		setIsDeleting(true);
		try {
			await deleteProject(projectToDelete.id);
			setProjectToDelete(null);
			fetchProjects();
		} catch (err) {
			toast.error(extractErrorMessage(err, "Failed to delete project"));
		} finally {
			setIsDeleting(false);
		}
	};
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(ContextMenu$1, { children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(ContextMenuTrigger, {
		asChild: true,
		children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
			className: "w-full min-h-[calc(100vh-100px)] pb-10 flex flex-col px-4 sm:px-6 lg:px-8",
			children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
				className: "max-w-7xl mx-auto flex flex-col gap-8 w-full",
				children: [
					/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
						className: "flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mt-6",
						children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
							className: "flex items-center gap-4",
							children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Button, {
								variant: "outline",
								size: "icon",
								className: "border-2 border-slate w-10 h-10 rounded-xl",
								onClick: () => router.navigate({ to: "/dashboard" }),
								children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(ArrowLeft, { className: "w-5 h-5 text-slate" })
							}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", { children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("h1", {
								className: "text-3xl font-display font-black tracking-tight text-slate",
								children: "Projects"
							}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
								className: "text-slate/70 font-semibold mt-1",
								children: "Manage your applications and environments."
							})] })]
						}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(Dialog$1, {
							open: isDialogOpen,
							onOpenChange: setIsDialogOpen,
							children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(DialogTrigger, {
								asChild: true,
								children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(Button, {
									variant: "primary",
									className: "gap-2",
									onClick: () => setCreatedCredentials(null),
									children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Plus, { className: "w-4 h-4" }), "New Project"]
								})
							}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)(DialogContent, {
								className: "sm:max-w-xl",
								children: createdCredentials ? /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
									className: "space-y-6",
									children: [
										/* @__PURE__ */ (0, import_jsx_runtime.jsxs)(DialogHeader, { children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)(DialogTitle, {
											className: "text-2xl font-black text-slate flex items-center gap-2",
											children: [
												"Project Created:",
												" ",
												/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
													className: "text-sage",
													children: createdCredentials.name
												})
											]
										}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(DialogDescription, {
											className: "text-terracotta font-bold flex items-start gap-2 mt-2 bg-terracotta/10 p-3 border-2 border-terracotta rounded-xl",
											children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(TriangleAlert, { className: "w-5 h-5 shrink-0 mt-0.5" }), "Warning: This is the ONLY time you will see this API Key. Please copy it or download the JSON file now. If you lose it, you will need to rotate the key."]
										})] }),
										/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
											className: "space-y-4",
											children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
												className: "space-y-2",
												children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Label, {
													className: "text-slate font-bold",
													children: "API Key (Keep Secret)"
												}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
													className: "flex gap-2",
													children: [
														/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Input, {
															type: showApiKey ? "text" : "password",
															value: createdCredentials.api_key,
															readOnly: true,
															className: "font-mono bg-taupe/10 rounded-xl"
														}),
														/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Button, {
															variant: "outline",
															type: "button",
															className: "rounded-xl px-3",
															onClick: () => setShowApiKey(!showApiKey),
															children: showApiKey ? /* @__PURE__ */ (0, import_jsx_runtime.jsx)(EyeOff, { className: "w-4 h-4" }) : /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Eye, { className: "w-4 h-4" })
														}),
														/* @__PURE__ */ (0, import_jsx_runtime.jsx)(CopyButton, { value: createdCredentials.api_key })
													]
												})]
											}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
												className: "space-y-2",
												children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Label, {
													className: "text-slate font-bold",
													children: "JWT Public Key (RSA PEM)"
												}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
													className: "relative",
													children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("pre", {
														className: "w-full min-h-30 border-2 border-slate bg-taupe/10 px-4 py-4 text-xs font-mono rounded-xl overflow-hidden whitespace-pre-wrap break-all leading-relaxed",
														children: showPublicKey ? createdCredentials.public_key : createdCredentials.public_key.replace(/(?<=-----BEGIN PUBLIC KEY-----\n)[\s\S]*?(?=\n-----END PUBLIC KEY-----)/, "****************************************************************\n****************************************************************\n****************************************************************\n****************************************************************")
													}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
														className: "absolute top-2 right-2 flex gap-3",
														children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Button, {
															type: "button",
															variant: "outline",
															size: "icon",
															className: "h-8 w-8 bg-vanilla shrink-0",
															onClick: () => setShowPublicKey(!showPublicKey),
															title: showPublicKey ? "Hide Key" : "Show Key",
															children: showPublicKey ? /* @__PURE__ */ (0, import_jsx_runtime.jsx)(EyeOff, { className: "w-4 h-4" }) : /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Eye, { className: "w-4 h-4" })
														}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)(CopyButton, {
															value: createdCredentials.public_key,
															variant: "outline",
															size: "icon",
															className: "h-8 w-8 bg-vanilla shrink-0",
															title: "Copy Key"
														})]
													})]
												})]
											})]
										}),
										/* @__PURE__ */ (0, import_jsx_runtime.jsxs)(DialogFooter, {
											className: "flex flex-col sm:flex-row gap-4 sm:gap-2 sm:justify-between border-t-2 border-taupe/20 pt-4 mt-6",
											children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
												className: "flex gap-2",
												children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(DownloadButton, {
													variant: "outline",
													size: "default",
													onDownload: handleDownloadApiKey,
													className: "gap-2",
													children: "API Key (JSON)"
												}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)(DownloadButton, {
													variant: "outline",
													size: "default",
													onDownload: handleDownloadPublicKey,
													className: "gap-2",
													children: "Public Key (PEM)"
												})]
											}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Button, {
												onClick: () => {
													setIsDialogOpen(false);
													setCreatedCredentials(null);
												},
												children: "I've Saved Them"
											})]
										})
									]
								}) : /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("form", {
									onSubmit: handleCreateProject,
									children: [
										/* @__PURE__ */ (0, import_jsx_runtime.jsxs)(DialogHeader, { children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(DialogTitle, { children: "Create New Project" }), /* @__PURE__ */ (0, import_jsx_runtime.jsx)(DialogDescription, { children: "Enter a name for your new Cerberus integration project." })] }),
										/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
											className: "py-6 space-y-4",
											children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
												className: "space-y-2",
												children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Label, {
													htmlFor: "name",
													children: "Project Name"
												}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Input, {
													id: "name",
													placeholder: "e.g. Acme Dashboard",
													value: newProjectName,
													onChange: (e) => setNewProjectName(e.target.value),
													autoFocus: true
												})]
											})
										}),
										/* @__PURE__ */ (0, import_jsx_runtime.jsxs)(DialogFooter, { children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(DialogClose, {
											asChild: true,
											children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Button, {
												variant: "outline",
												type: "button",
												children: "Cancel"
											})
										}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Button, {
											type: "submit",
											disabled: creating || !newProjectName.trim(),
											children: creating ? "Creating..." : "Create Project"
										})] })
									]
								})
							})]
						})]
					}),
					loading ? /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
						className: "grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6",
						children: [
							1,
							2,
							3
						].map((i) => /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(Card, {
							className: "relative overflow-hidden flex flex-col justify-between min-h-60 border-taupe/40 shadow-none bg-vanilla",
							children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)(CardHeader, {
								className: "pb-4",
								children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
									className: "flex justify-between items-start mb-2",
									children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Skeleton, { className: "w-20 h-6 rounded-none" })
								}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Skeleton, { className: "w-3/4 h-8 mt-2" })]
							}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(CardContent, {
								className: "flex flex-col gap-4 py-4",
								children: [
									/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
										className: "flex items-center gap-3",
										children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Skeleton, { className: "w-4 h-4 shrink-0" }), /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Skeleton, { className: "w-1/2 h-4" })]
									}),
									/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
										className: "flex items-center gap-3",
										children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Skeleton, { className: "w-4 h-4 shrink-0" }), /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Skeleton, { className: "w-5/12 h-4" })]
									}),
									/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
										className: "flex items-center gap-3",
										children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Skeleton, { className: "w-4 h-4 shrink-0" }), /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Skeleton, { className: "w-2/3 h-4" })]
									})
								]
							})]
						}, i))
					}) : projects.length === 0 ? /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
						className: "flex flex-col items-center justify-center p-12 border-2 border-dashed border-taupe bg-sand text-center",
						children: [
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)(FolderKanban$1, { className: "w-12 h-12 text-slate/50 mb-4" }),
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)("h3", {
								className: "text-xl font-bold text-slate mb-2",
								children: "No Projects Found"
							}),
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
								className: "text-slate/70 mb-6 font-semibold max-w-sm",
								children: "Create your first project to start authenticating users and managing environments."
							}),
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Button, {
								onClick: () => setIsDialogOpen(true),
								children: "Create Project"
							})
						]
					}) : /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
						className: "grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6",
						children: projects.map((project) => /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(ContextMenu$1, { children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(ContextMenuTrigger, {
							asChild: true,
							children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
								onClick: () => router.navigate({
									to: "/projects/$projectId",
									params: { projectId: project.id }
								}),
								onKeyDown: (e) => {
									if (e.key === "Enter" || e.key === " ") {
										e.preventDefault();
										router.navigate({
											to: "/projects/$projectId",
											params: { projectId: project.id }
										});
									}
								},
								role: "button",
								tabIndex: 0,
								className: "block group h-full outline-none focus-visible:ring-2 focus-visible:ring-slate cursor-pointer",
								children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(Card, {
									className: "relative overflow-hidden flex flex-col justify-between h-full hover:bg-sand/80 transition-all duration-300 ease-out group-hover:-translate-y-1 group-hover:shadow-[4px_4px_0px_0px_var(--taupe)]",
									children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)(CardHeader, {
										className: "pb-4",
										children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
											className: "flex justify-between items-start mb-2",
											children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
												className: "flex items-center gap-1.5 px-2.5 py-0.5 rounded-none border-2 border-slate text-xs font-bold uppercase bg-vanilla text-slate",
												children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", { className: `w-2 h-2 rounded-full ${project.environment === "production" ? "bg-sage" : "bg-ochre"}` }), project.environment]
											})
										}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)(CardTitle, {
											className: "text-2xl mt-2 line-clamp-1 transition-colors group-hover:text-sage",
											children: project.name
										})]
									}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(CardContent, {
										className: "flex flex-col gap-3 py-4",
										children: [
											/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
												className: "flex items-center gap-3 text-sm font-semibold text-slate/80",
												children: [
													/* @__PURE__ */ (0, import_jsx_runtime.jsx)(ShieldCheck, { className: "w-4 h-4 text-taupe" }),
													Object.values(project.oauth_config).filter((c) => c.enabled).length,
													" ",
													"Auth Providers"
												]
											}),
											/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
												className: "flex items-center gap-3 text-sm font-semibold text-slate/80",
												children: [
													/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Activity, { className: "w-4 h-4 text-taupe" }),
													project.allowed_origins.length,
													" Allowed Origins"
												]
											}),
											/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
												className: "flex items-center gap-3 text-sm font-semibold text-slate/80",
												children: [
													/* @__PURE__ */ (0, import_jsx_runtime.jsx)(CalendarDays, { className: "w-4 h-4 text-taupe" }),
													"Created",
													" ",
													new Date(project.created_at).toLocaleDateString()
												]
											})
										]
									})]
								})
							})
						}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(ContextMenuContent, {
							className: "w-48 bg-vanilla border-2 border-slate rounded-xl shadow-[4px_4px_0px_rgba(96,114,116,1)] overflow-hidden p-1 z-60",
							children: [
								/* @__PURE__ */ (0, import_jsx_runtime.jsxs)(ContextMenuItem, {
									className: "font-bold cursor-pointer rounded-lg px-3 py-2 hover:bg-sand focus:bg-sand",
									onClick: () => {
										navigator.clipboard.writeText(project.id);
										toast.success("Project ID copied to clipboard");
									},
									children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Copy, { className: "w-4 h-4 mr-2" }), " Copy Project ID"]
								}),
								/* @__PURE__ */ (0, import_jsx_runtime.jsx)(ContextMenuSeparator, { className: "bg-slate/10 my-1" }),
								/* @__PURE__ */ (0, import_jsx_runtime.jsxs)(ContextMenuItem, {
									className: "font-bold cursor-pointer rounded-lg px-3 py-2 hover:bg-sand focus:bg-sand",
									onClick: () => {
										setProjectToRename(project);
										setRenameValue(project.name);
									},
									children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Pen, { className: "w-4 h-4 mr-2" }), " Rename Project"]
								}),
								/* @__PURE__ */ (0, import_jsx_runtime.jsxs)(ContextMenuItem, {
									className: "font-bold cursor-pointer rounded-lg px-3 py-2 text-terracotta hover:bg-terracotta/10 hover:text-terracotta focus:bg-terracotta/10 focus:text-terracotta",
									onClick: () => setProjectToDelete(project),
									children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Trash2, { className: "w-4 h-4 mr-2" }), " Delete Project"]
								})
							]
						})] }, project.id))
					}),
					total > size && /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
						className: "flex items-center justify-between mt-8",
						children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("p", {
							className: "text-sm font-medium text-slate/70",
							children: [
								"Showing ",
								Math.min((page - 1) * size + 1, total),
								" to",
								" ",
								Math.min(page * size, total),
								" of ",
								total,
								" projects"
							]
						}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
							className: "flex items-center gap-2",
							children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)(Button, {
								variant: "outline",
								size: "sm",
								onClick: () => setPage((p) => Math.max(1, p - 1)),
								disabled: page === 1,
								className: "border-2 border-slate",
								children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(ChevronLeft, { className: "w-4 h-4 mr-1" }), "Previous"]
							}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(Button, {
								variant: "outline",
								size: "sm",
								onClick: () => setPage((p) => p + 1),
								disabled: page * size >= total,
								className: "border-2 border-slate",
								children: ["Next", /* @__PURE__ */ (0, import_jsx_runtime.jsx)(ChevronRight, { className: "w-4 h-4 ml-1" })]
							})]
						})]
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Dialog$1, {
						open: !!projectToRename,
						onOpenChange: (open) => !open && setProjectToRename(null),
						children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(DialogContent, {
							className: "sm:max-w-md",
							children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("form", {
								onSubmit: handleRenameProject,
								children: [
									/* @__PURE__ */ (0, import_jsx_runtime.jsxs)(DialogHeader, { children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(DialogTitle, { children: "Rename Project" }), /* @__PURE__ */ (0, import_jsx_runtime.jsx)(DialogDescription, { children: "Enter a new name for your project." })] }),
									/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
										className: "py-6",
										children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Label, {
											htmlFor: "rename",
											children: "Project Name"
										}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Input, {
											id: "rename",
											value: renameValue,
											onChange: (e) => setRenameValue(e.target.value),
											autoFocus: true,
											className: "mt-2"
										})]
									}),
									/* @__PURE__ */ (0, import_jsx_runtime.jsxs)(DialogFooter, { children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Button, {
										type: "button",
										variant: "outline",
										onClick: () => setProjectToRename(null),
										children: "Cancel"
									}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Button, {
										type: "submit",
										disabled: isRenaming || !renameValue.trim() || renameValue.trim() === projectToRename?.name,
										children: isRenaming ? "Renaming..." : "Save Changes"
									})] })
								]
							})
						})
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Dialog$1, {
						open: !!projectToDelete,
						onOpenChange: (open) => !open && setProjectToDelete(null),
						children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(DialogContent, {
							className: "sm:max-w-md border-terracotta",
							children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)(DialogHeader, { children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)(DialogTitle, {
								className: "text-terracotta flex items-center gap-2",
								children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(TriangleAlert, { className: "w-5 h-5" }), "Delete Project"]
							}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(DialogDescription, {
								className: "mt-2",
								children: [
									"Are you absolutely sure you want to delete",
									" ",
									/* @__PURE__ */ (0, import_jsx_runtime.jsx)("strong", {
										className: "text-slate font-bold",
										children: projectToDelete?.name
									}),
									"? This action cannot be undone and will permanently destroy the project and all its users."
								]
							})] }), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(DialogFooter, {
								className: "mt-6 gap-2 sm:justify-between",
								children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Button, {
									type: "button",
									variant: "outline",
									onClick: () => setProjectToDelete(null),
									children: "Cancel"
								}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Button, {
									type: "button",
									variant: "primary",
									className: "bg-terracotta hover:bg-terracotta/90 text-white",
									disabled: isDeleting,
									onClick: handleDeleteProject,
									children: isDeleting ? "Deleting..." : "Yes, delete project"
								})]
							})]
						})
					})
				]
			})
		})
	}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(ContextMenuContent, {
		className: "w-64 bg-vanilla border-2 border-slate rounded-xl shadow-[4px_4px_0px_rgba(96,114,116,1)] p-1 z-60",
		children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)(ContextMenuItem, {
			className: "font-bold cursor-pointer rounded-lg px-3 py-2 hover:bg-sand focus:bg-sand",
			onClick: () => setIsDialogOpen(true),
			children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Plus, { className: "w-4 h-4 mr-2" }), " Create New Project"]
		}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(ContextMenuItem, {
			className: "font-bold cursor-pointer rounded-lg px-3 py-2 hover:bg-sand focus:bg-sand",
			onClick: () => fetchProjects(),
			children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(RefreshCcw, { className: "w-4 h-4 mr-2" }), " Refresh Projects List"]
		})]
	})] });
}
function FolderKanban$1(props) {
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("svg", {
		...props,
		xmlns: "http://www.w3.org/2000/svg",
		width: "24",
		height: "24",
		viewBox: "0 0 24 24",
		fill: "none",
		stroke: "currentColor",
		strokeWidth: "2",
		strokeLinecap: "round",
		strokeLinejoin: "round",
		children: [
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)("path", { d: "M4 20h16a2 2 0 0 0 2-2V8a2 2 0 0 0-2-2h-7.93a2 2 0 0 1-1.66-.9l-.82-1.2A2 2 0 0 0 7.93 3H4a2 2 0 0 0-2 2v13c0 1.1.9 2 2 2Z" }),
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)("path", { d: "M9 10v4" }),
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)("path", { d: "M12 10v2" }),
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)("path", { d: "M15 10v6" })
		]
	});
}
//#endregion
export { ProjectsIndexPage as component };
