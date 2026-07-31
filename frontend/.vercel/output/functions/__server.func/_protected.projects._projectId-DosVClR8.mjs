import { o as __toESM } from "./_runtime.mjs";
import { u as require_react } from "./_libs/@floating-ui/react-dom+[...].mjs";
import { i as extractErrorMessage } from "./_ssr/api-client-DJkUESpZ.mjs";
import { n as require_jsx_runtime } from "./_libs/@marsidev/react-turnstile+[...].mjs";
import { N as Key, S as RefreshCcw, V as Copy, Y as Check, d as Shield, g as Settings2, i as User, j as List, n as Webhook, nt as Activity, tt as ArrowLeft, w as Pencil, x as RefreshCw } from "./_libs/lucide-react.mjs";
import { a as ContextMenuTrigger, i as ContextMenuSeparator, n as ContextMenuContent, r as ContextMenuItem, t as ContextMenu$1 } from "./_ssr/context-menu-Dw6tfCxT.mjs";
import { f as Outlet, l as useLocation, y as useRouter } from "./_libs/@tanstack/react-router+[...].mjs";
import { t as Button } from "./_ssr/button-C-O_Pb_u.mjs";
import { t as Route } from "./_protected.projects._projectId-BPJOfHyM.mjs";
import { t as Input } from "./_ssr/input-DFi7Mh72.mjs";
import { t as ProjectContext } from "./_ssr/ProjectContext-Dh_Z2-MY.mjs";
import { i as getProjectSecrets, m as updateProjectName, r as getProject } from "./_ssr/projects-B5Nezf2L.mjs";
import { n as toast } from "./_libs/sonner.mjs";
//#region node_modules/.nitro/vite/services/ssr/assets/_protected.projects._projectId-DosVClR8.js
var import_react = /* @__PURE__ */ __toESM(require_react());
var import_jsx_runtime = require_jsx_runtime();
function ProjectLayout() {
	const { projectId } = Route.useParams();
	const router = useRouter();
	const location = useLocation();
	const [project, setProject] = (0, import_react.useState)(null);
	const [publicKey, setPublicKey] = (0, import_react.useState)("");
	const [loading, setLoading] = (0, import_react.useState)(true);
	const [isEditingName, setIsEditingName] = (0, import_react.useState)(false);
	const [name, setName] = (0, import_react.useState)("");
	const [savingName, setSavingName] = (0, import_react.useState)(false);
	const fetchProjectData = async (showLoader = false) => {
		try {
			if (showLoader) setLoading(true);
			const data = await getProject(projectId);
			const secrets = await getProjectSecrets(projectId);
			setProject(data);
			setPublicKey(secrets.public_key);
			setName(data.name);
		} catch (err) {
			toast.error(extractErrorMessage(err, "Failed to fetch project details"));
			router.navigate({ to: "/projects" });
		} finally {
			if (showLoader) setLoading(false);
		}
	};
	(0, import_react.useEffect)(() => {
		fetchProjectData(true);
	}, [projectId]);
	const handleUpdateName = async () => {
		if (!name.trim() || name === project?.name) {
			setIsEditingName(false);
			setName(project?.name || "");
			return;
		}
		setSavingName(true);
		try {
			await updateProjectName(projectId, name);
			toast.success("Project name updated");
			await fetchProjectData();
			setIsEditingName(false);
		} catch (error) {
			toast.error(extractErrorMessage(error, "Failed to update project name"));
		} finally {
			setSavingName(false);
		}
	};
	if (loading || !project) return /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
		className: "max-w-7xl mx-auto flex flex-col gap-8 w-full",
		children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
			className: "flex flex-col gap-6 max-w-4xl mx-auto w-full animate-pulse",
			children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", { className: "h-12 w-64 bg-slate/10 rounded-xl" }), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", { className: "h-96 w-full bg-slate/10 rounded-xl" })]
		})
	});
	const currentTab = location.pathname.split("/").pop() || "analytics";
	const tabs = [
		{
			id: "analytics",
			label: "Analytics",
			icon: Activity,
			to: `/projects/${projectId}/analytics`
		},
		{
			id: "general",
			label: "General",
			icon: Settings2,
			to: `/projects/${projectId}/general`
		},
		{
			id: "auth",
			label: "Authentication",
			icon: Shield,
			to: `/projects/${projectId}/auth`
		},
		{
			id: "users",
			label: "Users",
			icon: User,
			to: `/projects/${projectId}/users`
		},
		{
			id: "security",
			label: "Security",
			icon: Key,
			to: `/projects/${projectId}/security`
		},
		{
			id: "claims",
			label: "Custom Default Claims",
			icon: Webhook,
			to: `/projects/${projectId}/claims`
		}
	];
	return /* @__PURE__ */ (0, import_jsx_runtime.jsx)(ProjectContext.Provider, {
		value: {
			project,
			publicKey,
			fetchProject: fetchProjectData
		},
		children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(ContextMenu$1, { children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(ContextMenuTrigger, {
			asChild: true,
			children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
				className: "w-full min-h-[calc(100vh-100px)] flex flex-col px-4 sm:px-6 lg:px-8",
				children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
					className: "max-w-7xl mx-auto flex flex-col w-full relative",
					children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
						className: "pb-4 mb-4",
						children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
							className: "w-full flex-wrap flex items-center justify-start rounded-xl bg-slate/5 p-1 text-slate/70 flat-shadow-slate border-2 border-slate mb-8",
							children: tabs.map((tab) => {
								return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("button", {
									onClick: () => router.navigate({ to: tab.to }),
									className: `inline-flex flex-1 items-center justify-center whitespace-nowrap rounded-lg px-3 py-1.5 text-sm font-bold ring-offset-background transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 gap-2 ${currentTab === tab.id || currentTab === projectId && tab.id === "analytics" ? "bg-vanilla text-slate shadow-sm border-2 border-slate" : "border-2 border-transparent hover:text-slate hover:bg-slate/5"}`,
									children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(tab.icon, { className: "w-4 h-4" }), tab.label]
								}, tab.id);
							})
						}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
							className: "flex items-center gap-4",
							children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Button, {
								variant: "outline",
								size: "icon",
								className: "h-10 w-10 shrink-0",
								onClick: () => router.navigate({ to: `/projects` }),
								children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(ArrowLeft, { className: "h-5 w-5" })
							}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
								className: "flex flex-col flex-1 min-w-0",
								children: [isEditingName ? /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
									className: "flex items-center gap-2 h-9",
									children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Input, {
										value: name,
										onChange: (e) => setName(e.target.value),
										className: "text-3xl font-display font-black tracking-tight text-slate h-full py-0 px-2 -ml-2 bg-taupe/10 border-slate/20 max-w-75",
										autoFocus: true,
										onKeyDown: (e) => {
											if (e.key === "Enter") handleUpdateName();
											if (e.key === "Escape") {
												setName(project.name);
												setIsEditingName(false);
											}
										}
									}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Button, {
										variant: "ghost",
										size: "icon",
										onClick: handleUpdateName,
										disabled: savingName,
										className: "h-8 w-8 shrink-0",
										children: savingName ? /* @__PURE__ */ (0, import_jsx_runtime.jsx)(RefreshCw, { className: "w-4 h-4 animate-spin" }) : /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Check, { className: "w-5 h-5 text-sage" })
									})]
								}) : /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
									className: "flex items-center gap-3 group h-9",
									children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("h1", {
										className: "text-3xl font-display font-black tracking-tight text-slate truncate",
										children: project.name
									}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("button", {
										onClick: () => setIsEditingName(true),
										className: "opacity-0 group-hover:opacity-100 transition-opacity text-slate/40 hover:text-slate shrink-0",
										children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Pencil, { className: "w-4 h-4" })
									})]
								}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("p", {
									className: "text-slate/70 font-semibold mt-1 font-mono text-sm truncate",
									children: ["ID: ", project.id]
								})]
							})]
						})]
					}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
						className: "mt-2",
						children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Outlet, {})
					})]
				})
			})
		}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(ContextMenuContent, {
			className: "w-56 bg-vanilla border-2 border-slate rounded-xl shadow-[4px_4px_0px_rgba(96,114,116,1)] p-1 z-60",
			children: [
				/* @__PURE__ */ (0, import_jsx_runtime.jsxs)(ContextMenuItem, {
					className: "font-bold cursor-pointer rounded-lg px-3 py-2 hover:bg-sand focus:bg-sand",
					onClick: () => {
						navigator.clipboard.writeText(project.id);
						toast.success("Project ID copied to clipboard");
					},
					children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Copy, { className: "w-4 h-4 mr-2" }), " Copy Project ID"]
				}),
				/* @__PURE__ */ (0, import_jsx_runtime.jsxs)(ContextMenuItem, {
					className: "font-bold cursor-pointer rounded-lg px-3 py-2 hover:bg-sand focus:bg-sand",
					onClick: () => fetchProjectData(),
					children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(RefreshCcw, { className: "w-4 h-4 mr-2" }), " Refresh Data"]
				}),
				/* @__PURE__ */ (0, import_jsx_runtime.jsx)(ContextMenuSeparator, { className: "bg-slate/10 my-1" }),
				/* @__PURE__ */ (0, import_jsx_runtime.jsxs)(ContextMenuItem, {
					className: "font-bold cursor-pointer rounded-lg px-3 py-2 hover:bg-sand focus:bg-sand",
					onClick: () => router.navigate({ to: "/dashboard" }),
					children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(List, { className: "w-4 h-4 mr-2" }), " Back to Projects List"]
				})
			]
		})] })
	});
}
//#endregion
export { ProjectLayout as component };
