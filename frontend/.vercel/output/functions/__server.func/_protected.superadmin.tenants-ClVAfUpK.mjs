import { o as __toESM } from "./_runtime.mjs";
import { u as require_react } from "./_libs/@floating-ui/react-dom+[...].mjs";
import { i as extractErrorMessage } from "./_ssr/api-client-DJkUESpZ.mjs";
import { n as require_jsx_runtime } from "./_libs/@marsidev/react-turnstile+[...].mjs";
import { S as RefreshCcw, V as Copy, X as ChartNoAxesColumnIncreasing, a as UserX, d as Shield, f as ShieldOff, o as UserCheck, v as Search, z as Ellipsis } from "./_libs/lucide-react.mjs";
import { a as ContextMenuTrigger, i as ContextMenuSeparator, n as ContextMenuContent, r as ContextMenuItem, t as ContextMenu$1 } from "./_ssr/context-menu-Dw6tfCxT.mjs";
import { a as DropdownMenuSeparator, i as DropdownMenuLabel, n as DropdownMenuContent, o as DropdownMenuTrigger, r as DropdownMenuItem, t as DropdownMenu } from "./_ssr/dropdown-menu-BwIF-xpi.mjs";
import { y as useRouter } from "./_libs/@tanstack/react-router+[...].mjs";
import { t as Button } from "./_ssr/button-C-O_Pb_u.mjs";
import { t as Input } from "./_ssr/input-DFi7Mh72.mjs";
import { n as toast } from "./_libs/sonner.mjs";
import { t as Skeleton } from "./_ssr/skeleton-Jd4K_fyE.mjs";
import { o as keepPreviousData } from "./_libs/tanstack__query-core.mjs";
import { i as useQueryClient, n as useQuery, t as useMutation } from "./_libs/tanstack__react-query.mjs";
import { i as updateTenantStatus, n as getTenants, r as updateTenantRole } from "./_ssr/superadmin-BFifgmRl.mjs";
import { a as TableHeader, i as TableHead, n as TableBody, o as TableRow, r as TableCell, t as Table } from "./_ssr/table-BDzCw5fj.mjs";
//#region node_modules/.nitro/vite/services/ssr/assets/_protected.superadmin.tenants-ClVAfUpK.js
var import_react = /* @__PURE__ */ __toESM(require_react());
var import_jsx_runtime = require_jsx_runtime();
function SuperadminTenantsPage() {
	const [page, setPage] = (0, import_react.useState)(1);
	const [search, setSearch] = (0, import_react.useState)("");
	const [searchInput, setSearchInput] = (0, import_react.useState)("");
	const router = useRouter();
	const queryClient = useQueryClient();
	const { data, isLoading } = useQuery({
		queryKey: [
			"superadmin-tenants",
			page,
			search
		],
		queryFn: () => getTenants(page, 50, search || void 0),
		placeholderData: keepPreviousData
	});
	const statusMutation = useMutation({
		mutationFn: ({ id, isActive }) => updateTenantStatus(id, isActive),
		onSuccess: () => {
			queryClient.invalidateQueries({ queryKey: ["superadmin-tenants"] });
			toast.success("Tenant status updated");
		},
		onError: (err) => {
			toast.error("Failed to update status: " + extractErrorMessage(err));
		}
	});
	const roleMutation = useMutation({
		mutationFn: ({ id, role }) => updateTenantRole(id, role),
		onSuccess: () => {
			queryClient.invalidateQueries({ queryKey: ["superadmin-tenants"] });
			toast.success("Tenant role updated");
		},
		onError: (err) => {
			toast.error("Failed to update role: " + extractErrorMessage(err));
		}
	});
	const handleSearch = (e) => {
		e.preventDefault();
		setPage(1);
		setSearch(searchInput);
	};
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(ContextMenu$1, { children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(ContextMenuTrigger, {
		asChild: true,
		children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
			className: "space-y-6 pt-4 w-full h-full min-h-[calc(100vh-100px)] px-4 sm:px-6 lg:px-8",
			children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
				className: "max-w-7xl mx-auto w-full",
				children: [
					/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
						className: "flex flex-col sm:flex-row justify-between items-start sm:items-end gap-4 mb-6",
						children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", { children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("h2", {
							className: "text-xl font-bold text-slate",
							children: "Tenant Management"
						}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
							className: "text-sm font-semibold text-slate/60 mt-1",
							children: "Manage global access and roles for all users."
						})] }), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("form", {
							onSubmit: handleSearch,
							className: "relative w-full sm:w-72",
							children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Search, { className: "absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-taupe" }), /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Input, {
								value: searchInput,
								onChange: (e) => setSearchInput(e.target.value),
								placeholder: "Search email or ID...",
								className: "pl-9 bg-vanilla border-taupe/50 focus-visible:ring-ochre"
							})]
						})]
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
						className: "bg-vanilla border-2 border-taupe/30 rounded-xl overflow-hidden shadow-sm mt-6",
						children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(Table, { children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(TableHeader, {
							className: "bg-sand/30",
							children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(TableRow, {
								className: "border-taupe/30 hover:bg-transparent",
								children: [
									/* @__PURE__ */ (0, import_jsx_runtime.jsx)(TableHead, {
										className: "font-bold text-slate w-62.5",
										children: "Tenant"
									}),
									/* @__PURE__ */ (0, import_jsx_runtime.jsx)(TableHead, {
										className: "font-bold text-slate",
										children: "Role"
									}),
									/* @__PURE__ */ (0, import_jsx_runtime.jsx)(TableHead, {
										className: "font-bold text-slate",
										children: "Status"
									}),
									/* @__PURE__ */ (0, import_jsx_runtime.jsx)(TableHead, {
										className: "font-bold text-slate hidden md:table-cell",
										children: "Joined"
									}),
									/* @__PURE__ */ (0, import_jsx_runtime.jsx)(TableHead, {
										className: "text-right font-bold text-slate w-25",
										children: "Actions"
									})
								]
							})
						}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)(TableBody, { children: isLoading ? Array.from({ length: 5 }).map((_, i) => /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(TableRow, {
							className: "border-taupe/20 hover:bg-transparent",
							children: [
								/* @__PURE__ */ (0, import_jsx_runtime.jsx)(TableCell, { children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Skeleton, { className: "h-5 w-40 bg-taupe/20" }) }),
								/* @__PURE__ */ (0, import_jsx_runtime.jsx)(TableCell, { children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Skeleton, { className: "h-5 w-20 bg-taupe/20" }) }),
								/* @__PURE__ */ (0, import_jsx_runtime.jsx)(TableCell, { children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Skeleton, { className: "h-5 w-16 bg-taupe/20" }) }),
								/* @__PURE__ */ (0, import_jsx_runtime.jsx)(TableCell, {
									className: "hidden md:table-cell",
									children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Skeleton, { className: "h-5 w-24 bg-taupe/20" })
								}),
								/* @__PURE__ */ (0, import_jsx_runtime.jsx)(TableCell, {
									className: "text-right",
									children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Skeleton, { className: "h-8 w-8 ml-auto bg-taupe/20" })
								})
							]
						}, i)) : !data?.items || data.items.length === 0 ? /* @__PURE__ */ (0, import_jsx_runtime.jsx)(TableRow, {
							className: "hover:bg-transparent",
							children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(TableCell, {
								colSpan: 5,
								className: "h-32 text-center text-slate/60 font-semibold",
								children: "No tenants found."
							})
						}) : data.items.map((tenant) => /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(ContextMenu$1, { children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(ContextMenuTrigger, {
							asChild: true,
							children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(TableRow, {
								className: "border-taupe/20 hover:bg-sand/30 transition-colors",
								children: [
									/* @__PURE__ */ (0, import_jsx_runtime.jsxs)(TableCell, { children: [
										/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
											className: "font-semibold text-slate truncate",
											children: tenant.name || "Unnamed User"
										}),
										tenant.email && /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
											className: "text-xs text-slate/70 mt-0.5 truncate font-semibold",
											children: tenant.email
										}),
										/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
											className: "text-xs text-slate/50 font-mono mt-0.5",
											children: tenant.id
										})
									] }),
									/* @__PURE__ */ (0, import_jsx_runtime.jsx)(TableCell, { children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
										className: `inline-flex items-center px-2 py-0.5 rounded text-xs font-bold uppercase ${tenant.role === "SUPERADMIN" ? "bg-ochre/20 text-ochre" : "bg-taupe/20 text-slate/80"}`,
										children: tenant.role
									}) }),
									/* @__PURE__ */ (0, import_jsx_runtime.jsx)(TableCell, { children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
										className: `inline-flex items-center px-2 py-0.5 rounded text-xs font-bold uppercase ${tenant.is_active ? "bg-sage/20 text-sage" : "bg-terracotta/20 text-terracotta"}`,
										children: tenant.is_active ? "Active" : "Disabled"
									}) }),
									/* @__PURE__ */ (0, import_jsx_runtime.jsx)(TableCell, {
										className: "hidden md:table-cell text-sm font-medium text-slate/70",
										children: tenant.created_at ? new Date(tenant.created_at).toLocaleDateString() : "Unknown"
									}),
									/* @__PURE__ */ (0, import_jsx_runtime.jsx)(TableCell, {
										className: "text-right",
										children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(DropdownMenu, { children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(DropdownMenuTrigger, {
											asChild: true,
											children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(Button, {
												variant: "ghost",
												className: "h-8 w-8 p-0 text-slate/70 hover:text-slate hover:bg-taupe/20",
												children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
													className: "sr-only",
													children: "Open menu"
												}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Ellipsis, { className: "h-4 w-4" })]
											})
										}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(DropdownMenuContent, {
											align: "end",
											className: "w-48",
											children: [
												/* @__PURE__ */ (0, import_jsx_runtime.jsx)(DropdownMenuLabel, { children: "Manage Tenant" }),
												/* @__PURE__ */ (0, import_jsx_runtime.jsx)(DropdownMenuSeparator, {}),
												/* @__PURE__ */ (0, import_jsx_runtime.jsxs)(DropdownMenuItem, {
													onClick: () => router.navigate({
														to: "/superadmin/tenants/$tenantId/analytics",
														params: { tenantId: tenant.id }
													}),
													className: "cursor-pointer",
													children: [
														/* @__PURE__ */ (0, import_jsx_runtime.jsx)(ChartNoAxesColumnIncreasing, { className: "mr-2 h-4 w-4 text-slate" }),
														" ",
														"View Analytics"
													]
												}),
												/* @__PURE__ */ (0, import_jsx_runtime.jsx)(DropdownMenuItem, {
													onClick: () => statusMutation.mutate({
														id: tenant.id,
														isActive: !tenant.is_active
													}),
													disabled: statusMutation.isPending,
													children: tenant.is_active ? /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(import_jsx_runtime.Fragment, { children: [
														/* @__PURE__ */ (0, import_jsx_runtime.jsx)(UserX, { className: "mr-2 h-4 w-4 text-terracotta" }),
														" ",
														"Disable Account"
													] }) : /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(import_jsx_runtime.Fragment, { children: [
														/* @__PURE__ */ (0, import_jsx_runtime.jsx)(UserCheck, { className: "mr-2 h-4 w-4 text-sage" }),
														" ",
														"Enable Account"
													] })
												}),
												/* @__PURE__ */ (0, import_jsx_runtime.jsx)(DropdownMenuItem, {
													onClick: () => roleMutation.mutate({
														id: tenant.id,
														role: tenant.role === "SUPERADMIN" ? "TENANT" : "SUPERADMIN"
													}),
													disabled: roleMutation.isPending,
													children: tenant.role === "SUPERADMIN" ? /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(import_jsx_runtime.Fragment, { children: [
														/* @__PURE__ */ (0, import_jsx_runtime.jsx)(ShieldOff, { className: "mr-2 h-4 w-4 text-slate" }),
														" ",
														"Demote to Tenant"
													] }) : /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(import_jsx_runtime.Fragment, { children: [
														/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Shield, { className: "mr-2 h-4 w-4 text-ochre" }),
														" ",
														"Promote to Admin"
													] })
												})
											]
										})] })
									})
								]
							})
						}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(ContextMenuContent, {
							className: "w-56 bg-vanilla border-2 border-slate rounded-xl shadow-[4px_4px_0px_rgba(96,114,116,1)] p-1 z-60",
							children: [
								/* @__PURE__ */ (0, import_jsx_runtime.jsxs)(ContextMenuItem, {
									className: "font-bold cursor-pointer rounded-lg px-3 py-2 hover:bg-sand focus:bg-sand",
									onClick: () => {
										navigator.clipboard.writeText(tenant.id);
										toast.success("Tenant ID copied to clipboard");
									},
									children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Copy, { className: "w-4 h-4 mr-2" }), " Copy Tenant ID"]
								}),
								/* @__PURE__ */ (0, import_jsx_runtime.jsx)(ContextMenuSeparator, { className: "bg-slate/10 my-1" }),
								/* @__PURE__ */ (0, import_jsx_runtime.jsxs)(ContextMenuItem, {
									className: "font-bold cursor-pointer rounded-lg px-3 py-2 hover:bg-sand focus:bg-sand",
									onClick: () => router.navigate({
										to: "/superadmin/tenants/$tenantId/analytics",
										params: { tenantId: tenant.id }
									}),
									children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(ChartNoAxesColumnIncreasing, { className: "w-4 h-4 mr-2" }), " View Analytics"]
								}),
								/* @__PURE__ */ (0, import_jsx_runtime.jsx)(ContextMenuItem, {
									className: "font-bold cursor-pointer rounded-lg px-3 py-2 hover:bg-sand focus:bg-sand",
									onClick: () => statusMutation.mutate({
										id: tenant.id,
										isActive: !tenant.is_active
									}),
									disabled: statusMutation.isPending,
									children: tenant.is_active ? /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(import_jsx_runtime.Fragment, { children: [
										/* @__PURE__ */ (0, import_jsx_runtime.jsx)(UserX, { className: "w-4 h-4 mr-2 text-terracotta" }),
										" ",
										/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
											className: "text-terracotta",
											children: "Disable Tenant"
										})
									] }) : /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(import_jsx_runtime.Fragment, { children: [
										/* @__PURE__ */ (0, import_jsx_runtime.jsx)(UserCheck, { className: "w-4 h-4 mr-2 text-sage" }),
										" ",
										/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
											className: "text-sage",
											children: "Enable Tenant"
										})
									] })
								}),
								/* @__PURE__ */ (0, import_jsx_runtime.jsx)(ContextMenuItem, {
									className: "font-bold cursor-pointer rounded-lg px-3 py-2 hover:bg-sand focus:bg-sand",
									onClick: () => roleMutation.mutate({
										id: tenant.id,
										role: tenant.role === "SUPERADMIN" ? "USER" : "SUPERADMIN"
									}),
									disabled: roleMutation.isPending,
									children: tenant.role === "SUPERADMIN" ? /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(import_jsx_runtime.Fragment, { children: [
										/* @__PURE__ */ (0, import_jsx_runtime.jsx)(ShieldOff, { className: "w-4 h-4 mr-2 text-ochre" }),
										" ",
										"Revoke Superadmin"
									] }) : /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(import_jsx_runtime.Fragment, { children: [
										/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Shield, { className: "w-4 h-4 mr-2 text-ochre" }),
										" ",
										"Promote to Superadmin"
									] })
								})
							]
						})] }, tenant.id)) })] })
					}),
					data && data.total > data.size && /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
						className: "flex justify-between items-center bg-vanilla border-2 border-taupe/30 p-3 rounded-xl shadow-sm",
						children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("p", {
							className: "text-sm font-semibold text-slate/70 ml-2",
							children: [
								"Showing ",
								(page - 1) * data.size + 1,
								" to",
								" ",
								Math.min(page * data.size, data.total),
								" of ",
								data.total
							]
						}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
							className: "flex gap-2",
							children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Button, {
								variant: "outline",
								size: "sm",
								onClick: () => setPage((p) => Math.max(1, p - 1)),
								disabled: page === 1,
								className: "border-taupe/50 bg-vanilla text-slate hover:bg-sand",
								children: "Previous"
							}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Button, {
								variant: "outline",
								size: "sm",
								onClick: () => setPage((p) => p + 1),
								disabled: page * data.size >= data.total,
								className: "border-taupe/50 bg-vanilla text-slate hover:bg-sand",
								children: "Next"
							})]
						})]
					})
				]
			})
		})
	}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)(ContextMenuContent, {
		className: "w-56 bg-vanilla border-2 border-slate rounded-xl shadow-[4px_4px_0px_rgba(96,114,116,1)] p-1 z-60",
		children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(ContextMenuItem, {
			className: "font-bold cursor-pointer rounded-lg px-3 py-2 hover:bg-sand focus:bg-sand",
			onClick: () => queryClient.invalidateQueries({ queryKey: ["superadmin-tenants"] }),
			children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(RefreshCcw, { className: "w-4 h-4 mr-2" }), " Refresh Tenants"]
		})
	})] });
}
//#endregion
export { SuperadminTenantsPage as component };
