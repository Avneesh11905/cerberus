import { o as __toESM } from "./_runtime.mjs";
import { u as require_react } from "./_libs/@floating-ui/react-dom+[...].mjs";
import { i as extractErrorMessage } from "./_ssr/api-client-DJkUESpZ.mjs";
import { n as require_jsx_runtime } from "./_libs/@marsidev/react-turnstile+[...].mjs";
import { A as LoaderCircle, f as ShieldOff, tt as ArrowLeft, v as Search, z as Ellipsis } from "./_libs/lucide-react.mjs";
import { n as AvatarFallback, t as Avatar } from "./_ssr/avatar-DnS6IaKa.mjs";
import { i as DropdownMenuLabel, n as DropdownMenuContent, o as DropdownMenuTrigger, r as DropdownMenuItem, t as DropdownMenu } from "./_ssr/dropdown-menu-BwIF-xpi.mjs";
import { y as useRouter } from "./_libs/@tanstack/react-router+[...].mjs";
import { t as Button } from "./_ssr/button-C-O_Pb_u.mjs";
import { t as Input } from "./_ssr/input-DFi7Mh72.mjs";
import { c as getTenantUsers, y as updateTenantUserStatus } from "./_ssr/projects-B5Nezf2L.mjs";
import { n as toast } from "./_libs/sonner.mjs";
import { t as Checkbox } from "./_ssr/checkbox-BY8mRrC-.mjs";
import { a as TableHeader, i as TableHead, n as TableBody, o as TableRow, r as TableCell, t as Table } from "./_ssr/table-BDzCw5fj.mjs";
//#region node_modules/.nitro/vite/services/ssr/assets/_protected.users.index-5W8nYHYT.js
var import_react = /* @__PURE__ */ __toESM(require_react());
var import_jsx_runtime = require_jsx_runtime();
function GlobalUsersDashboard() {
	const router = useRouter();
	const [users, setUsers] = (0, import_react.useState)([]);
	const [total, setTotal] = (0, import_react.useState)(0);
	const [loading, setLoading] = (0, import_react.useState)(true);
	const [page, setPage] = (0, import_react.useState)(1);
	const [search, setSearch] = (0, import_react.useState)("");
	const size = 50;
	(0, import_react.useEffect)(() => {
		const handler = setTimeout(() => {
			fetchUsers();
		}, 500);
		return () => clearTimeout(handler);
	}, [page, search]);
	const fetchUsers = async () => {
		try {
			setLoading(true);
			const data = await getTenantUsers(page, size, search);
			setUsers(data.items);
			setTotal(data.total);
		} catch (err) {
			toast.error(extractErrorMessage(err, "Failed to fetch global users"));
		} finally {
			setLoading(false);
		}
	};
	const handleToggleStatus = async (email, currentStatus) => {
		try {
			await updateTenantUserStatus(email, !currentStatus);
			toast.success(`User ${!currentStatus ? "activated" : "deactivated"} across all projects`);
			fetchUsers();
		} catch (err) {
			toast.error(extractErrorMessage(err, "Failed to update user status"));
		}
	};
	const totalPages = Math.ceil(total / size);
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
		className: "max-w-7xl mx-auto flex flex-col gap-8 w-full",
		children: [
			/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
				className: "flex items-center gap-4 mb-2",
				children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Button, {
					variant: "outline",
					size: "icon",
					className: "border-2 border-slate w-10 h-10 rounded-xl",
					onClick: () => router.navigate({ to: "/dashboard" }),
					children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(ArrowLeft, { className: "w-5 h-5 text-slate" })
				}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", { children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("h1", {
					className: "text-3xl font-display font-black tracking-tight text-slate",
					children: "Global Users"
				}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
					className: "text-slate/70 font-semibold mt-1",
					children: "Manage users across all your projects."
				})] })]
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
				className: "flex items-center space-x-2",
				children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
					className: "relative flex-1 max-w-md",
					children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Search, { className: "absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate/50" }), /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Input, {
						placeholder: "Search by name or email...",
						className: "pl-9 bg-vanilla/50",
						value: search,
						onChange: (e) => {
							setSearch(e.target.value);
							setPage(1);
						}
					})]
				})
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
				className: "bg-vanilla rounded-xl border-2 border-slate shadow-[4px_4px_0px_rgba(30,41,59,1)] overflow-hidden",
				children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)(Table, { children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(TableHeader, {
					className: "bg-sand border-b-2 border-slate",
					children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(TableRow, {
						className: "hover:bg-transparent",
						children: [
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)(TableHead, {
								className: "font-black text-slate uppercase tracking-wider py-4",
								children: "User"
							}),
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)(TableHead, {
								className: "font-black text-slate uppercase tracking-wider py-4",
								children: "Active"
							}),
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)(TableHead, {
								className: "font-black text-slate uppercase tracking-wider py-4 text-right",
								children: "Actions"
							})
						]
					})
				}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)(TableBody, { children: loading ? /* @__PURE__ */ (0, import_jsx_runtime.jsx)(TableRow, { children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(TableCell, {
					colSpan: 4,
					className: "h-32 text-center",
					children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(LoaderCircle, { className: "w-8 h-8 animate-spin mx-auto text-slate" })
				}) }) : users.length === 0 ? /* @__PURE__ */ (0, import_jsx_runtime.jsx)(TableRow, { children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(TableCell, {
					colSpan: 4,
					className: "h-32 text-center text-slate/60 font-medium",
					children: "No users found."
				}) }) : users.map((user) => /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(TableRow, {
					className: "border-b-2 border-slate/10 hover:bg-vanilla/50 transition-colors",
					children: [
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)(TableCell, { children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
							className: "flex items-center gap-3",
							children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Avatar, {
								className: "w-10 h-10 border-2 border-slate",
								children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(AvatarFallback, {
									className: "bg-sand font-bold text-slate",
									children: (user.name?.[0] || user.email[0]).toUpperCase()
								})
							}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", { children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
								className: "font-bold text-slate",
								children: user.name || "Unknown User"
							}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
								className: "text-sm font-medium text-slate/60",
								children: user.email
							})] })]
						}) }),
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)(TableCell, { children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Checkbox, {
							checked: user.is_active,
							onCheckedChange: () => handleToggleStatus(user.email, user.is_active),
							className: "border-2 border-slate data-[state=checked]:bg-slate data-[state=checked]:text-white"
						}) }),
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)(TableCell, {
							className: "text-right",
							children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(DropdownMenu, { children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(DropdownMenuTrigger, {
								asChild: true,
								children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(Button, {
									variant: "ghost",
									className: "h-8 w-8 p-0 text-slate hover:bg-slate/10 hover:text-slate",
									children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
										className: "sr-only",
										children: "Open menu"
									}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Ellipsis, { className: "h-4 w-4" })]
								})
							}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(DropdownMenuContent, {
								align: "end",
								className: "w-48 bg-vanilla border-2 border-slate shadow-[4px_4px_0px_rgba(30,41,59,1)] rounded-xl p-1",
								children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(DropdownMenuLabel, {
									className: "font-bold text-slate px-2 py-1.5",
									children: "Actions"
								}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(DropdownMenuItem, {
									onClick: () => handleToggleStatus(user.email, user.is_active),
									className: "font-medium cursor-pointer rounded-lg px-2 py-1.5",
									children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(ShieldOff, { className: "mr-2 h-4 w-4" }), user.is_active ? "Deactivate Everywhere" : "Activate Everywhere"]
								})]
							})] })
						})
					]
				}, `${user.id}-${user.email}`)) })] }), !loading && totalPages > 1 && /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
					className: "p-4 border-t-2 border-slate flex items-center justify-between bg-sand",
					children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
						className: "text-sm font-bold text-slate",
						children: [
							"Showing ",
							(page - 1) * size + 1,
							" to ",
							Math.min(page * size, total),
							" ",
							"of ",
							total,
							" users"
						]
					}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
						className: "flex gap-2",
						children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Button, {
							variant: "outline",
							size: "sm",
							onClick: () => setPage((p) => Math.max(1, p - 1)),
							disabled: page === 1,
							className: "font-bold border-2",
							children: "Previous"
						}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Button, {
							variant: "outline",
							size: "sm",
							onClick: () => setPage((p) => Math.min(totalPages, p + 1)),
							disabled: page === totalPages,
							className: "font-bold border-2",
							children: "Next"
						})]
					})]
				})]
			})
		]
	});
}
//#endregion
export { GlobalUsersDashboard as component };
