import "../_runtime.mjs";
import { u as require_react } from "../_libs/@floating-ui/react-dom+[...].mjs";
import { t as cn } from "./utils-DgjCne0W.mjs";
import { n as require_jsx_runtime } from "../_libs/@marsidev/react-turnstile+[...].mjs";
import { a as ContextMenuSeparator$1, i as ContextMenuPortal, n as ContextMenuContent$1, o as ContextMenuTrigger$1, r as ContextMenuItem$1, t as ContextMenu } from "../_libs/@radix-ui/react-context-menu+[...].mjs";
require_react();
var import_jsx_runtime = require_jsx_runtime();
function ContextMenu$1({ ...props }) {
	return /* @__PURE__ */ (0, import_jsx_runtime.jsx)(ContextMenu, {
		"data-slot": "context-menu",
		...props
	});
}
function ContextMenuTrigger({ ...props }) {
	return /* @__PURE__ */ (0, import_jsx_runtime.jsx)(ContextMenuTrigger$1, {
		"data-slot": "context-menu-trigger",
		...props
	});
}
function ContextMenuContent({ className, ...props }) {
	return /* @__PURE__ */ (0, import_jsx_runtime.jsx)(ContextMenuPortal, { children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(ContextMenuContent$1, {
		"data-slot": "context-menu-content",
		className: cn("z-50 max-h-(--radix-context-menu-content-available-height) min-w-[8rem] origin-(--radix-context-menu-content-transform-origin) overflow-x-hidden overflow-y-auto rounded-md border bg-popover p-1 text-popover-foreground shadow-md data-[side=bottom]:slide-in-from-top-2 data-[side=left]:slide-in-from-right-2 data-[side=right]:slide-in-from-left-2 data-[side=top]:slide-in-from-bottom-2 data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=closed]:zoom-out-95 data-[state=open]:animate-in data-[state=open]:fade-in-0 data-[state=open]:zoom-in-95", className),
		...props
	}) });
}
function ContextMenuItem({ className, inset, variant = "default", ...props }) {
	return /* @__PURE__ */ (0, import_jsx_runtime.jsx)(ContextMenuItem$1, {
		"data-slot": "context-menu-item",
		"data-inset": inset,
		"data-variant": variant,
		className: cn("relative flex cursor-default items-center gap-2 rounded-sm px-2 py-1.5 text-sm outline-hidden select-none focus:bg-accent focus:text-accent-foreground data-[disabled]:pointer-events-none data-[disabled]:opacity-50 data-[inset]:pl-8 data-[variant=destructive]:text-destructive data-[variant=destructive]:focus:bg-destructive/10 data-[variant=destructive]:focus:text-destructive dark:data-[variant=destructive]:focus:bg-destructive/20 [&_svg]:pointer-events-none [&_svg]:shrink-0 [&_svg:not([class*='size-'])]:size-4 [&_svg:not([class*='text-'])]:text-muted-foreground data-[variant=destructive]:*:[svg]:text-destructive!", className),
		...props
	});
}
function ContextMenuSeparator({ className, ...props }) {
	return /* @__PURE__ */ (0, import_jsx_runtime.jsx)(ContextMenuSeparator$1, {
		"data-slot": "context-menu-separator",
		className: cn("-mx-1 my-1 h-px bg-border", className),
		...props
	});
}
//#endregion
export { ContextMenuTrigger as a, ContextMenuSeparator as i, ContextMenuContent as n, ContextMenuItem as r, ContextMenu$1 as t };
