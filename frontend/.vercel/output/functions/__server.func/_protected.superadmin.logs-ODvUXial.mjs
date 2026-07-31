import { o as __toESM } from "./_runtime.mjs";
import { u as require_react } from "./_libs/@floating-ui/react-dom+[...].mjs";
import { t as cn } from "./_ssr/utils-DgjCne0W.mjs";
import { n as require_jsx_runtime } from "./_libs/@marsidev/react-turnstile+[...].mjs";
import { i as PopoverTrigger$1, n as PopoverContent$1, r as PopoverPortal, t as Popover } from "./_libs/radix-ui__react-popover.mjs";
import { J as ChevronDown, K as ChevronRight, Q as Calendar, S as RefreshCcw, V as Copy, q as ChevronLeft } from "./_libs/lucide-react.mjs";
import { a as ContextMenuTrigger, n as ContextMenuContent, r as ContextMenuItem, t as ContextMenu$1 } from "./_ssr/context-menu-Dw6tfCxT.mjs";
import { i as buttonVariants, t as Button } from "./_ssr/button-C-O_Pb_u.mjs";
import { n as toast } from "./_libs/sonner.mjs";
import { a as SelectValue, i as SelectTrigger, n as SelectContent, r as SelectItem, t as Select$1 } from "./_ssr/select-O4KC7wrJ.mjs";
import { t as Skeleton } from "./_ssr/skeleton-Jd4K_fyE.mjs";
import { n as useQuery } from "./_libs/tanstack__react-query.mjs";
import { t as getSystemLogs } from "./_ssr/superadmin-BFifgmRl.mjs";
import { a as TableHeader, i as TableHead, n as TableBody, o as TableRow, r as TableCell, t as Table } from "./_ssr/table-BDzCw5fj.mjs";
import { l as format } from "./_libs/date-fns.mjs";
import { n as getDefaultClassNames, t as DayPicker } from "./_libs/react-day-picker.mjs";
//#region node_modules/.nitro/vite/services/ssr/assets/_protected.superadmin.logs-ODvUXial.js
var import_react = /* @__PURE__ */ __toESM(require_react());
var import_jsx_runtime = require_jsx_runtime();
function Popover$1({ ...props }) {
	return /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Popover, {
		"data-slot": "popover",
		...props
	});
}
function PopoverTrigger({ ...props }) {
	return /* @__PURE__ */ (0, import_jsx_runtime.jsx)(PopoverTrigger$1, {
		"data-slot": "popover-trigger",
		...props
	});
}
function PopoverContent({ className, align = "center", sideOffset = 4, ...props }) {
	return /* @__PURE__ */ (0, import_jsx_runtime.jsx)(PopoverPortal, { children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(PopoverContent$1, {
		"data-slot": "popover-content",
		align,
		sideOffset,
		className: cn("z-50 w-auto origin-(--radix-popover-content-transform-origin) rounded-xl border-2 border-slate bg-vanilla p-4 text-slate shadow-[4px_4px_0px_rgba(30,41,59,1)] outline-hidden data-[side=bottom]:slide-in-from-top-2 data-[side=left]:slide-in-from-right-2 data-[side=right]:slide-in-from-left-2 data-[side=top]:slide-in-from-bottom-2 data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=closed]:zoom-out-95 data-[state=open]:animate-in data-[state=open]:fade-in-0 data-[state=open]:zoom-in-95", className),
		...props
	}) });
}
function Calendar$1({ className, classNames, showOutsideDays = true, captionLayout = "label", buttonVariant = "ghost", formatters, components, ...props }) {
	const defaultClassNames = getDefaultClassNames();
	return /* @__PURE__ */ (0, import_jsx_runtime.jsx)(DayPicker, {
		showOutsideDays,
		className: cn("group/calendar bg-background p-3 [--cell-size:--spacing(8)] [[data-slot=card-content]_&]:bg-transparent [[data-slot=popover-content]_&]:bg-transparent", String.raw`rtl:**:[.rdp-button\_next>svg]:rotate-180`, String.raw`rtl:**:[.rdp-button\_previous>svg]:rotate-180`, className),
		captionLayout,
		formatters: {
			formatMonthDropdown: (date) => date.toLocaleString("default", { month: "short" }),
			...formatters
		},
		classNames: {
			root: cn("w-fit font-sans", defaultClassNames.root),
			months: cn("relative flex flex-col gap-4 md:flex-row", defaultClassNames.months),
			month: cn("flex w-full flex-col gap-4", defaultClassNames.month),
			nav: cn("absolute inset-x-0 top-0 flex w-full items-center justify-between gap-1", defaultClassNames.nav),
			button_previous: cn(buttonVariants({ variant: buttonVariant }), "size-(--cell-size) p-0 select-none aria-disabled:opacity-50 hover:bg-sand hover:text-slate text-slate border-2 border-transparent hover:border-slate/30", defaultClassNames.button_previous),
			button_next: cn(buttonVariants({ variant: buttonVariant }), "size-(--cell-size) p-0 select-none aria-disabled:opacity-50 hover:bg-sand hover:text-slate text-slate border-2 border-transparent hover:border-slate/30", defaultClassNames.button_next),
			month_caption: cn("flex h-(--cell-size) w-full items-center justify-center px-(--cell-size) font-bold text-slate", defaultClassNames.month_caption),
			dropdowns: cn("flex h-(--cell-size) w-full items-center justify-center gap-1.5 text-sm font-bold", defaultClassNames.dropdowns),
			dropdown_root: cn("relative rounded-md border-2 border-slate shadow-sm has-focus:border-ochre has-focus:ring-[3px] has-focus:ring-ochre/50 bg-vanilla text-slate", defaultClassNames.dropdown_root),
			dropdown: cn("absolute inset-0 bg-popover opacity-0", defaultClassNames.dropdown),
			caption_label: cn("font-bold select-none text-slate", captionLayout === "label" ? "text-sm" : "flex h-8 items-center gap-1 rounded-md pr-1 pl-2 text-sm [&>svg]:size-3.5 [&>svg]:text-slate/60", defaultClassNames.caption_label),
			month_grid: cn("w-full border-collapse", defaultClassNames.month_grid),
			weekdays: cn("flex", defaultClassNames.weekdays),
			weekday: cn("flex-1 rounded-md text-[0.85rem] font-bold text-slate/70 select-none", defaultClassNames.weekday),
			week: cn("mt-2 flex w-full", defaultClassNames.week),
			week_number_header: cn("w-(--cell-size) select-none", defaultClassNames.week_number_header),
			week_number: cn("text-[0.8rem] text-slate/50 select-none", defaultClassNames.week_number),
			day: cn("group/day relative aspect-square h-full w-full p-0 text-center select-none cursor-pointer [&:last-child[data-selected=true]_button]:rounded-r-md", props.showWeekNumber ? "[&:nth-child(2)[data-selected=true]_button]:rounded-l-md" : "[&:first-child[data-selected=true]_button]:rounded-l-md", defaultClassNames.day),
			range_start: cn("rounded-l-md bg-taupe/30", defaultClassNames.range_start),
			range_middle: cn("rounded-none", defaultClassNames.range_middle),
			range_end: cn("rounded-r-md bg-taupe/30", defaultClassNames.range_end),
			today: cn("rounded-md bg-sand font-bold text-slate data-[selected=true]:rounded-none border-2 border-taupe/30", defaultClassNames.today),
			outside: cn("text-slate/40 aria-selected:text-slate/40", defaultClassNames.outside),
			disabled: cn("text-slate/40 opacity-50", defaultClassNames.disabled),
			hidden: cn("invisible", defaultClassNames.hidden),
			...classNames
		},
		components: {
			Root: ({ className: rootClassName, rootRef, ...rootProps }) => {
				return /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
					"data-slot": "calendar",
					ref: rootRef,
					className: cn(rootClassName),
					...rootProps
				});
			},
			Chevron: ({ className: chevronClassName, orientation, ...chevronProps }) => {
				if (orientation === "left") return /* @__PURE__ */ (0, import_jsx_runtime.jsx)(ChevronLeft, {
					className: cn("size-4", chevronClassName),
					...chevronProps
				});
				if (orientation === "right") return /* @__PURE__ */ (0, import_jsx_runtime.jsx)(ChevronRight, {
					className: cn("size-4", chevronClassName),
					...chevronProps
				});
				return /* @__PURE__ */ (0, import_jsx_runtime.jsx)(ChevronDown, {
					className: cn("size-4", chevronClassName),
					...chevronProps
				});
			},
			DayButton: CalendarDayButton,
			WeekNumber: ({ children, ...weekNumberProps }) => {
				return /* @__PURE__ */ (0, import_jsx_runtime.jsx)("td", {
					...weekNumberProps,
					children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
						className: "flex size-(--cell-size) items-center justify-center text-center",
						children
					})
				});
			},
			...components
		},
		...props
	});
}
function CalendarDayButton({ className, day, modifiers, ...props }) {
	const defaultClassNames = getDefaultClassNames();
	const ref = import_react.useRef(null);
	import_react.useEffect(() => {
		if (modifiers.focused) ref.current?.focus();
	}, [modifiers.focused]);
	return /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Button, {
		ref,
		variant: "ghost",
		size: "icon",
		"data-day": day.date.toLocaleDateString(),
		"data-selected-single": modifiers.selected && !modifiers.range_start && !modifiers.range_end && !modifiers.range_middle,
		"data-range-start": modifiers.range_start,
		"data-range-end": modifiers.range_end,
		"data-range-middle": modifiers.range_middle,
		className: cn("flex aspect-square size-auto w-full min-w-(--cell-size) flex-col gap-1 leading-none font-bold group-data-[focused=true]/day:relative group-data-[focused=true]/day:z-10 group-data-[focused=true]/day:border-ochre group-data-[focused=true]/day:ring-[3px] group-data-[focused=true]/day:ring-ochre/50 data-[range-end=true]:rounded-md data-[range-end=true]:rounded-r-md data-[range-end=true]:bg-terracotta data-[range-end=true]:text-vanilla data-[range-middle=true]:rounded-none data-[range-middle=true]:bg-taupe/30 data-[range-middle=true]:text-slate data-[range-start=true]:rounded-md data-[range-start=true]:rounded-l-md data-[range-start=true]:bg-terracotta data-[range-start=true]:text-vanilla data-[selected-single=true]:bg-terracotta data-[selected-single=true]:text-vanilla hover:bg-sand hover:text-slate [&>span]:text-xs [&>span]:opacity-70", defaultClassNames.day, className),
		...props
	});
}
function getLevelBadge(level) {
	switch (level.toUpperCase()) {
		case "ERROR":
		case "FATAL": return "inline-flex items-center px-2 py-0.5 rounded text-xs font-bold uppercase bg-terracotta text-vanilla";
		case "WARNING":
		case "WARN": return "inline-flex items-center px-2 py-0.5 rounded text-xs font-bold uppercase bg-ochre text-slate";
		case "INFO": return "inline-flex items-center px-2 py-0.5 rounded text-xs font-bold uppercase bg-slate text-vanilla";
		default: return "inline-flex items-center px-2 py-0.5 rounded text-xs font-bold uppercase bg-taupe text-slate";
	}
}
function SuperadminLogsPage() {
	const [page, setPage] = (0, import_react.useState)(1);
	const [levelFilter, setLevelFilter] = (0, import_react.useState)("ALL");
	const [dateRange, setDateRange] = (0, import_react.useState)(void 0);
	const { data, isLoading } = useQuery({
		queryKey: [
			"superadmin-logs",
			page,
			levelFilter,
			dateRange?.from,
			dateRange?.to
		],
		queryFn: () => {
			let fromStr = void 0;
			let toStr = void 0;
			if (dateRange?.from) {
				fromStr = dateRange.from.toISOString();
				const toDate = dateRange.to ? new Date(dateRange.to) : new Date(dateRange.from);
				toDate.setHours(23, 59, 59, 999);
				toStr = toDate.toISOString();
			}
			return getSystemLogs(page, 100, levelFilter === "ALL" ? void 0 : levelFilter, fromStr, toStr);
		},
		refetchInterval: 15e3
	});
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(ContextMenu$1, { children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(ContextMenuTrigger, {
		asChild: true,
		children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
			className: "space-y-6 pt-4 w-full h-full min-h-[calc(100vh-100px)] px-4 sm:px-6 lg:px-8",
			children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
				className: "max-w-7xl mx-auto w-full",
				children: [
					/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
						className: "flex flex-col md:flex-row justify-between items-start md:items-end gap-4 mb-6",
						children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", { children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("h2", {
							className: "text-xl font-bold text-slate",
							children: "System Logs"
						}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
							className: "text-sm font-semibold text-slate/60 mt-1",
							children: "Real-time audit and error logs for the platform."
						})] }), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
							className: "flex flex-col sm:flex-row w-full md:w-auto gap-4",
							children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)(Popover$1, { children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(PopoverTrigger, {
								asChild: true,
								children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(Button, {
									variant: "outline",
									className: `w-full sm:w-65 justify-start text-left bg-vanilla hover:bg-sand focus:ring-ochre ${!dateRange ? "text-slate/60" : ""}`,
									children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Calendar, { className: "mr-2 h-4 w-4" }), dateRange?.from ? dateRange.to ? /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(import_jsx_runtime.Fragment, { children: [
										format(dateRange.from, "LLL dd, y"),
										" -",
										" ",
										format(dateRange.to, "LLL dd, y")
									] }) : format(dateRange.from, "LLL dd, y") : /* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", { children: "Pick a date range" })]
								})
							}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(PopoverContent, {
								className: "w-auto p-0 border-2 border-slate shadow-[8px_8px_0px_var(--slate)] rounded-xl flex flex-col md:flex-row",
								align: "end",
								children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
									className: "flex flex-col gap-2 p-3 border-b-2 md:border-b-0 md:border-r-2 border-slate/10 bg-vanilla/50",
									children: [
										/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Button, {
											variant: "ghost",
											className: "justify-start text-sm",
											onClick: () => {
												const to = /* @__PURE__ */ new Date();
												const from = /* @__PURE__ */ new Date();
												from.setHours(0, 0, 0, 0);
												setDateRange({
													from,
													to
												});
												setPage(1);
											},
											children: "Today"
										}),
										/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Button, {
											variant: "ghost",
											className: "justify-start text-sm",
											onClick: () => {
												const to = /* @__PURE__ */ new Date();
												const from = /* @__PURE__ */ new Date();
												from.setDate(to.getDate() - 7);
												from.setHours(0, 0, 0, 0);
												setDateRange({
													from,
													to
												});
												setPage(1);
											},
											children: "Last 7 Days"
										}),
										/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Button, {
											variant: "ghost",
											className: "justify-start text-sm",
											onClick: () => {
												const to = /* @__PURE__ */ new Date();
												const from = /* @__PURE__ */ new Date();
												from.setDate(to.getDate() - 30);
												from.setHours(0, 0, 0, 0);
												setDateRange({
													from,
													to
												});
												setPage(1);
											},
											children: "Last 30 Days"
										}),
										/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Button, {
											variant: "ghost",
											className: "justify-start text-sm text-terracotta hover:text-terracotta hover:bg-terracotta/10 mt-auto",
											onClick: () => {
												setDateRange(void 0);
												setPage(1);
											},
											children: "Clear"
										})
									]
								}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Calendar$1, {
									mode: "range",
									defaultMonth: dateRange?.from,
									selected: dateRange,
									onSelect: (range) => {
										setDateRange(range);
										setPage(1);
									},
									numberOfMonths: 1,
									showOutsideDays: false
								})]
							})] }), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
								className: "w-full sm:w-48",
								children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(Select$1, {
									value: levelFilter,
									onValueChange: (val) => {
										setLevelFilter(val);
										setPage(1);
									},
									children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(SelectTrigger, {
										className: "bg-vanilla text-slate border-2 border-slate rounded-xl shadow-[4px_4px_0px_var(--slate)] transition-all hover:-translate-y-1 hover:shadow-[6px_6px_0px_var(--slate)] active:translate-y-0.5 active:translate-x-0.5 active:shadow-none focus:ring-ochre focus:outline-none",
										children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(SelectValue, { placeholder: "Filter by level" })
									}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(SelectContent, {
										className: "border-2 border-slate rounded-xl shadow-[4px_4px_0px_var(--slate)]",
										children: [
											/* @__PURE__ */ (0, import_jsx_runtime.jsx)(SelectItem, {
												value: "ALL",
												children: "All Levels"
											}),
											/* @__PURE__ */ (0, import_jsx_runtime.jsx)(SelectItem, {
												value: "INFO",
												children: "INFO"
											}),
											/* @__PURE__ */ (0, import_jsx_runtime.jsx)(SelectItem, {
												value: "WARN",
												children: "WARN"
											}),
											/* @__PURE__ */ (0, import_jsx_runtime.jsx)(SelectItem, {
												value: "ERROR",
												children: "ERROR"
											}),
											/* @__PURE__ */ (0, import_jsx_runtime.jsx)(SelectItem, {
												value: "DEBUG",
												children: "DEBUG"
											})
										]
									})]
								})
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
										className: "font-bold text-slate w-45",
										children: "Timestamp"
									}),
									/* @__PURE__ */ (0, import_jsx_runtime.jsx)(TableHead, {
										className: "font-bold text-slate w-25",
										children: "Level"
									}),
									/* @__PURE__ */ (0, import_jsx_runtime.jsx)(TableHead, {
										className: "font-bold text-slate w-62.5",
										children: "Source"
									}),
									/* @__PURE__ */ (0, import_jsx_runtime.jsx)(TableHead, {
										className: "font-bold text-slate",
										children: "Message"
									})
								]
							})
						}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)(TableBody, {
							className: "font-mono text-sm",
							children: isLoading ? Array.from({ length: 15 }).map((_, i) => /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(TableRow, {
								className: "border-taupe/20 hover:bg-transparent",
								children: [
									/* @__PURE__ */ (0, import_jsx_runtime.jsx)(TableCell, { children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Skeleton, { className: "h-4 w-32 bg-taupe/20" }) }),
									/* @__PURE__ */ (0, import_jsx_runtime.jsx)(TableCell, { children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Skeleton, { className: "h-5 w-16 bg-taupe/20 rounded" }) }),
									/* @__PURE__ */ (0, import_jsx_runtime.jsx)(TableCell, { children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Skeleton, { className: "h-4 w-40 bg-taupe/20" }) }),
									/* @__PURE__ */ (0, import_jsx_runtime.jsx)(TableCell, { children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Skeleton, { className: "h-4 w-64 bg-taupe/20" }) })
								]
							}, i)) : data?.items.length === 0 ? /* @__PURE__ */ (0, import_jsx_runtime.jsx)(TableRow, {
								className: "hover:bg-transparent font-sans",
								children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(TableCell, {
									colSpan: 4,
									className: "h-32 text-center text-slate/60 font-semibold",
									children: "No logs found."
								})
							}) : data?.items.map((log) => /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(ContextMenu$1, { children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(ContextMenuTrigger, {
								asChild: true,
								children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(TableRow, {
									className: "border-taupe/20 hover:bg-sand/30 transition-colors",
									children: [
										/* @__PURE__ */ (0, import_jsx_runtime.jsx)(TableCell, {
											className: "text-slate/70 whitespace-nowrap align-top pt-4",
											children: new Date(log.created_at).toLocaleString()
										}),
										/* @__PURE__ */ (0, import_jsx_runtime.jsx)(TableCell, {
											className: "align-top pt-4",
											children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
												className: getLevelBadge(log.level),
												children: log.level
											})
										}),
										/* @__PURE__ */ (0, import_jsx_runtime.jsx)(TableCell, {
											className: "text-slate font-medium align-top pt-4 break-all",
											title: log.source,
											children: log.source
										}),
										/* @__PURE__ */ (0, import_jsx_runtime.jsxs)(TableCell, {
											className: "text-slate/70 text-xs whitespace-pre-wrap wrap-break-word align-top pt-4 py-4",
											title: "Log Message",
											children: [log.file && /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
												className: "font-mono text-slate/50 mb-1.5 flex items-center gap-1.5 bg-taupe/10 w-fit px-2 py-0.5 rounded-md border border-taupe/20",
												children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("svg", {
													xmlns: "http://www.w3.org/2000/svg",
													width: "12",
													height: "12",
													viewBox: "0 0 24 24",
													fill: "none",
													stroke: "currentColor",
													strokeWidth: "2",
													strokeLinecap: "round",
													strokeLinejoin: "round",
													children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("path", { d: "M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z" }), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("polyline", { points: "14 2 14 8 20 8" })]
												}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("span", { children: [
													log.file,
													":",
													log.line || "?"
												] })]
											}), log.message]
										})
									]
								})
							}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)(ContextMenuContent, {
								className: "w-56 bg-vanilla border-2 border-slate rounded-xl shadow-[4px_4px_0px_rgba(96,114,116,1)] p-1 z-60",
								children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(ContextMenuItem, {
									className: "font-bold cursor-pointer rounded-lg px-3 py-2 hover:bg-sand focus:bg-sand",
									onClick: () => {
										navigator.clipboard.writeText(log.id);
										toast.success("Log ID copied to clipboard");
									},
									children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Copy, { className: "w-4 h-4 mr-2" }), " Copy Log ID"]
								})
							})] }, log.id))
						})] })
					}),
					data && data.total > data.size && /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
						className: "flex justify-between items-center bg-vanilla border-2 border-taupe/30 p-3 rounded-xl shadow-sm mt-6",
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
								className: "border-taupe/50 bg-vanilla text-slate hover:bg-sand font-sans",
								children: "Previous"
							}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Button, {
								variant: "outline",
								size: "sm",
								onClick: () => setPage((p) => p + 1),
								disabled: page * data.size >= data.total,
								className: "border-taupe/50 bg-vanilla text-slate hover:bg-sand font-sans",
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
			onClick: () => setPage(1),
			children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(RefreshCcw, { className: "w-4 h-4 mr-2" }), " Refresh Logs"]
		})
	})] });
}
//#endregion
export { SuperadminLogsPage as component };
