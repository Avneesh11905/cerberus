import { o as __toESM } from "./_runtime.mjs";
import { u as require_react } from "./_libs/@floating-ui/react-dom+[...].mjs";
import { i as extractErrorMessage } from "./_ssr/api-client-DJkUESpZ.mjs";
import { n as require_jsx_runtime } from "./_libs/@marsidev/react-turnstile+[...].mjs";
import { A as LoaderCircle, a as UserX, d as Shield, v as Search } from "./_libs/lucide-react.mjs";
import { t as Button } from "./_ssr/button-C-O_Pb_u.mjs";
import { t as Input } from "./_ssr/input-DFi7Mh72.mjs";
import { _ as updateProjectUserClaims, a as getProjectUserClaims, o as getProjectUsers, v as updateProjectUserStatus } from "./_ssr/projects-B5Nezf2L.mjs";
import { n as toast } from "./_libs/sonner.mjs";
import { a as CardHeader, n as CardContent, o as CardTitle, r as CardDescription, t as Card } from "./_ssr/card-D2S-3Lsc.mjs";
import { a as DialogFooter, i as DialogDescription, o as DialogHeader, r as DialogContent, s as DialogTitle, t as Dialog$1 } from "./_ssr/dialog-DYmxbvqX.mjs";
import { t as Route } from "./_protected.projects._projectId.users-AA0wXr8R.mjs";
//#region node_modules/.nitro/vite/services/ssr/assets/_protected.projects._projectId.users-Doz0AwOY.js
var import_react = /* @__PURE__ */ __toESM(require_react());
var import_jsx_runtime = require_jsx_runtime();
function ProjectUsers({ projectId }) {
	const [users, setUsers] = (0, import_react.useState)([]);
	const [total, setTotal] = (0, import_react.useState)(0);
	const [page, setPage] = (0, import_react.useState)(1);
	const [search, setSearch] = (0, import_react.useState)("");
	const [loading, setLoading] = (0, import_react.useState)(true);
	const [debouncedSearch, setDebouncedSearch] = (0, import_react.useState)("");
	const [selectedUser, setSelectedUser] = (0, import_react.useState)(null);
	const [claims, setClaims] = (0, import_react.useState)([]);
	const [claimsLoading, setClaimsLoading] = (0, import_react.useState)(false);
	const [savingClaims, setSavingClaims] = (0, import_react.useState)(false);
	const size = 10;
	(0, import_react.useEffect)(() => {
		const handler = setTimeout(() => {
			setDebouncedSearch(search);
			setPage(1);
		}, 500);
		return () => clearTimeout(handler);
	}, [search]);
	const fetchUsers = async () => {
		try {
			setLoading(true);
			const data = await getProjectUsers(projectId, page, size, debouncedSearch);
			setUsers(data.items);
			setTotal(data.total);
		} catch (err) {
			toast.error(extractErrorMessage(err, "Failed to fetch users"));
		} finally {
			setLoading(false);
		}
	};
	(0, import_react.useEffect)(() => {
		fetchUsers();
	}, [
		projectId,
		page,
		size,
		debouncedSearch
	]);
	const toggleStatus = async (user) => {
		try {
			await updateProjectUserStatus(projectId, user.id, !user.is_active);
			toast.success(`User ${!user.is_active ? "activated" : "deactivated"}`);
			fetchUsers();
		} catch (err) {
			toast.error(extractErrorMessage(err, "Failed to update user status"));
		}
	};
	const openClaims = async (user) => {
		setSelectedUser(user);
		setClaimsLoading(true);
		try {
			const overrides = (await getProjectUserClaims(projectId, user.id)).user_overrides;
			setClaims(Object.entries(overrides).map(([k, v]) => ({
				key: k,
				value: String(v)
			})));
		} catch (err) {
			toast.error(extractErrorMessage(err, "Failed to fetch user claims"));
			setSelectedUser(null);
		} finally {
			setClaimsLoading(false);
		}
	};
	const handleSaveClaims = async () => {
		if (!selectedUser) return;
		setSavingClaims(true);
		try {
			const overridesObj = claims.reduce((acc, curr) => {
				if (curr.key) acc[curr.key] = curr.value;
				return acc;
			}, {});
			await updateProjectUserClaims(projectId, selectedUser.id, overridesObj);
			toast.success("User claims updated");
			setSelectedUser(null);
		} catch (err) {
			toast.error(extractErrorMessage(err, "Failed to update user claims"));
		} finally {
			setSavingClaims(false);
		}
	};
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(Card, { children: [
		/* @__PURE__ */ (0, import_jsx_runtime.jsxs)(CardHeader, { children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(CardTitle, { children: "Project Users" }), /* @__PURE__ */ (0, import_jsx_runtime.jsx)(CardDescription, { children: "Manage users who have authenticated with this project." })] }),
		/* @__PURE__ */ (0, import_jsx_runtime.jsxs)(CardContent, {
			className: "space-y-6",
			children: [
				/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
					className: "flex gap-4 items-center",
					children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
						className: "relative flex-1 max-w-sm",
						children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Search, { className: "absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate/50" }), /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Input, {
							placeholder: "Search by email...",
							value: search,
							onChange: (e) => setSearch(e.target.value),
							className: "pl-9"
						})]
					})
				}),
				/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
					className: "border-2 border-slate",
					children: loading ? /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
						className: "p-8 flex justify-center",
						children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(LoaderCircle, { className: "w-6 h-6 animate-spin text-slate" })
					}) : users.length === 0 ? /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
						className: "p-12 flex flex-col items-center justify-center text-center bg-sand",
						children: [
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)(UserX, { className: "w-12 h-12 text-slate/50 mb-4" }),
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)("h3", {
								className: "text-xl font-bold text-slate mb-2",
								children: "No Users Found"
							}),
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
								className: "text-slate/70 font-semibold max-w-sm",
								children: "No users match your criteria or no users have authenticated yet."
							})
						]
					}) : /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
						className: "overflow-x-auto",
						children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("table", {
							className: "w-full text-left text-sm font-semibold",
							children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("thead", {
								className: "bg-taupe/10 border-b-2 border-slate",
								children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("tr", { children: [
									/* @__PURE__ */ (0, import_jsx_runtime.jsx)("th", {
										className: "px-4 py-3 text-slate",
										children: "Email"
									}),
									/* @__PURE__ */ (0, import_jsx_runtime.jsx)("th", {
										className: "px-4 py-3 text-slate",
										children: "Status"
									}),
									/* @__PURE__ */ (0, import_jsx_runtime.jsx)("th", {
										className: "px-4 py-3 text-slate",
										children: "Last Login"
									}),
									/* @__PURE__ */ (0, import_jsx_runtime.jsx)("th", {
										className: "px-4 py-3 text-slate text-right",
										children: "Actions"
									})
								] })
							}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("tbody", {
								className: "divide-y-2 divide-taupe/20",
								children: users.map((user) => /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("tr", {
									className: "hover:bg-sand/30 transition-colors",
									children: [
										/* @__PURE__ */ (0, import_jsx_runtime.jsx)("td", {
											className: "px-4 py-4",
											children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
												className: "flex items-center gap-3",
												children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
													className: "w-8 h-8 bg-slate text-vanilla flex items-center justify-center font-bold",
													children: user.email[0].toUpperCase()
												}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", { children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
													className: "text-slate font-bold",
													children: user.email
												}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
													className: "text-xs text-slate/70",
													children: user.id
												})] })]
											})
										}),
										/* @__PURE__ */ (0, import_jsx_runtime.jsx)("td", {
											className: "px-4 py-4",
											children: user.is_active ? /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("span", {
												className: "inline-flex items-center gap-1.5 px-2.5 py-1 text-xs font-bold bg-sage/20 text-sage border border-sage/30",
												children: [
													/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", { className: "w-1.5 h-1.5 rounded-full bg-sage" }),
													" ",
													"Active"
												]
											}) : /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("span", {
												className: "inline-flex items-center gap-1.5 px-2.5 py-1 text-xs font-bold bg-terracotta/20 text-terracotta border border-terracotta/30",
												children: [
													/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", { className: "w-1.5 h-1.5 rounded-full bg-terracotta" }),
													" ",
													"Inactive"
												]
											})
										}),
										/* @__PURE__ */ (0, import_jsx_runtime.jsx)("td", {
											className: "px-4 py-4 text-slate/70",
											children: user.last_login ? new Date(user.last_login).toLocaleDateString() : "Never"
										}),
										/* @__PURE__ */ (0, import_jsx_runtime.jsx)("td", {
											className: "px-4 py-4 text-right",
											children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
												className: "flex justify-end gap-2",
												children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Button, {
													variant: "outline",
													size: "sm",
													className: "h-8 text-xs font-bold",
													onClick: () => toggleStatus(user),
													children: user.is_active ? "Deactivate" : "Activate"
												}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(Button, {
													variant: "outline",
													size: "sm",
													className: "h-8 text-xs font-bold gap-1",
													onClick: () => openClaims(user),
													children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Shield, { className: "w-3 h-3" }), " Claims"]
												})]
											})
										})
									]
								}, user.id))
							})]
						})
					})
				}),
				/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
					className: "flex items-center justify-between",
					children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("p", {
						className: "text-sm font-semibold text-slate/70",
						children: [
							"Showing ",
							users.length > 0 ? (page - 1) * size + 1 : 0,
							" to",
							" ",
							Math.min(page * size, total),
							" of ",
							total
						]
					}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
						className: "flex gap-2",
						children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Button, {
							variant: "outline",
							disabled: page === 1,
							onClick: () => setPage((p) => p - 1),
							children: "Previous"
						}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Button, {
							variant: "outline",
							disabled: page * size >= total,
							onClick: () => setPage((p) => p + 1),
							children: "Next"
						})]
					})]
				})
			]
		}),
		/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Dialog$1, {
			open: !!selectedUser,
			onOpenChange: (open) => !open && setSelectedUser(null),
			children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(DialogContent, {
				className: "sm:max-w-150 border-2 border-slate bg-vanilla p-0 overflow-hidden shadow-[8px_8px_0px_rgba(30,41,59,1)]",
				children: [
					/* @__PURE__ */ (0, import_jsx_runtime.jsxs)(DialogHeader, {
						className: "p-6 bg-sand border-b-2 border-slate",
						children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(DialogTitle, {
							className: "text-2xl font-black text-slate",
							children: "User Claim Overrides"
						}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(DialogDescription, {
							className: "font-semibold text-slate/70",
							children: [
								"Override default project claims for ",
								selectedUser?.email,
								"."
							]
						})]
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
						className: "p-6",
						children: claimsLoading ? /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
							className: "py-8 flex justify-center",
							children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(LoaderCircle, { className: "w-6 h-6 animate-spin text-slate" })
						}) : /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
							className: "space-y-4",
							children: [claims.map((c, idx) => /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
								className: "flex gap-2 items-center",
								children: [
									/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Input, {
										placeholder: "Key (e.g. role)",
										value: c.key,
										onChange: (e) => {
											const newClaims = [...claims];
											newClaims[idx].key = e.target.value;
											setClaims(newClaims);
										}
									}),
									/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Input, {
										placeholder: "Value (e.g. admin)",
										value: c.value,
										onChange: (e) => {
											const newClaims = [...claims];
											newClaims[idx].value = e.target.value;
											setClaims(newClaims);
										}
									}),
									/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Button, {
										variant: "destructive",
										className: "px-3",
										onClick: () => setClaims(claims.filter((_, i) => i !== idx)),
										children: "X"
									})
								]
							}, idx)), /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Button, {
								type: "button",
								variant: "outline",
								className: "w-full border-dashed",
								onClick: () => setClaims([...claims, {
									key: "",
									value: ""
								}]),
								children: "+ Add Override"
							})]
						})
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsxs)(DialogFooter, {
						className: "p-6 bg-sand border-t-2 border-slate flex justify-end",
						children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Button, {
							variant: "outline",
							onClick: () => setSelectedUser(null),
							children: "Cancel"
						}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(Button, {
							onClick: handleSaveClaims,
							disabled: savingClaims,
							children: [savingClaims ? /* @__PURE__ */ (0, import_jsx_runtime.jsx)(LoaderCircle, { className: "w-4 h-4 mr-2 animate-spin" }) : null, "Save Overrides"]
						})]
					})
				]
			})
		})
	] });
}
function UsersTab() {
	const { projectId } = Route.useParams();
	return /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
		className: "animate-in fade-in slide-in-from-bottom-2 duration-300 w-full",
		children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(ProjectUsers, { projectId })
	});
}
//#endregion
export { UsersTab as component };
