import { o as __toESM } from "../_runtime.mjs";
import { u as require_react } from "../_libs/@floating-ui/react-dom+[...].mjs";
import { t as cva } from "../_libs/class-variance-authority+clsx.mjs";
import { t as cn } from "./utils-DgjCne0W.mjs";
import { n as require_jsx_runtime } from "../_libs/@marsidev/react-turnstile+[...].mjs";
import { B as Download, H as ClipboardCheck, V as Copy, Y as Check } from "../_libs/lucide-react.mjs";
import { n as AnimatePresence, t as motion } from "../_libs/framer-motion.mjs";
//#region node_modules/.nitro/vite/services/ssr/assets/button-C-O_Pb_u.js
var import_react = /* @__PURE__ */ __toESM(require_react());
var import_jsx_runtime = require_jsx_runtime();
var iconVariants = {
	initial: {
		opacity: 0,
		scale: .3,
		y: 5
	},
	animate: {
		opacity: 1,
		scale: 1,
		y: 0
	},
	exit: {
		opacity: 0,
		scale: .3,
		y: -5
	}
};
function AnimatedIconSwap({ isActive, activeIcon: ActiveIcon = Check, inactiveIcon: InactiveIcon, className = "w-4 h-4", activeClassName }) {
	return /* @__PURE__ */ (0, import_jsx_runtime.jsx)(AnimatePresence, {
		mode: "wait",
		children: isActive ? /* @__PURE__ */ (0, import_jsx_runtime.jsx)(motion.div, {
			variants: iconVariants,
			initial: "initial",
			animate: "animate",
			exit: "exit",
			transition: {
				type: "spring",
				stiffness: 500,
				damping: 25,
				mass: .5
			},
			className: "inline-flex items-center justify-center",
			children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(ActiveIcon, { className: activeClassName || className })
		}, "active") : /* @__PURE__ */ (0, import_jsx_runtime.jsx)(motion.div, {
			variants: iconVariants,
			initial: "initial",
			animate: "animate",
			exit: "exit",
			transition: {
				type: "spring",
				stiffness: 500,
				damping: 25,
				mass: .5
			},
			className: "inline-flex items-center justify-center",
			children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(InactiveIcon, { className })
		}, "inactive")
	});
}
var buttonVariants = cva("inline-flex items-center justify-center whitespace-nowrap rounded-xl text-sm font-bold transition-all focus-visible:outline-none disabled:pointer-events-none disabled:opacity-50 cursor-pointer", {
	variants: {
		variant: {
			primary: "bg-slate text-vanilla shadow-[4px_4px_0px_var(--taupe)] hover:-translate-y-0.5 hover:shadow-[6px_6px_0px_var(--taupe)] active:translate-y-0.5 active:translate-x-0.5 active:shadow-[2px_2px_0px_var(--taupe)]",
			secondary: "bg-taupe text-slate border-2 border-slate shadow-[4px_4px_0px_var(--slate)] hover:-translate-y-1 hover:shadow-[6px_6px_0px_var(--slate)] active:translate-y-0.5 active:translate-x-0.5 active:shadow-none",
			destructive: "bg-transparent text-terracotta border-2 border-terracotta shadow-[4px_4px_0px_var(--terracotta)] hover:-translate-y-1 hover:shadow-[6px_6px_0px_var(--terracotta)] active:translate-y-0.5 active:translate-x-0.5 active:shadow-none",
			outline: "bg-transparent text-slate border-2 border-slate shadow-[4px_4px_0px_var(--slate)] hover:-translate-y-1 hover:shadow-[6px_6px_0px_var(--slate)] active:translate-y-0.5 active:translate-x-0.5 active:shadow-none",
			inverse: "bg-vanilla text-slate border-2 border-slate shadow-[4px_4px_0px_var(--taupe)] hover:-translate-y-1 hover:shadow-[6px_6px_0px_var(--taupe)] active:translate-y-0.5 active:translate-x-0.5 active:shadow-none",
			ghost: "hover:bg-taupe/20 text-slate"
		},
		size: {
			default: "h-10 px-4 py-2",
			sm: "h-9 rounded-xl px-3",
			lg: "h-11 rounded-xl px-8",
			xl: "h-14 rounded-xl px-8 text-lg",
			icon: "h-10 w-10"
		}
	},
	defaultVariants: {
		variant: "primary",
		size: "default"
	}
});
var Button = import_react.forwardRef(({ className, variant, size, ...props }, ref) => {
	return /* @__PURE__ */ (0, import_jsx_runtime.jsx)("button", {
		ref,
		className: cn(buttonVariants({
			variant,
			size,
			className
		})),
		...props
	});
});
Button.displayName = "Button";
function CopyButton({ value, copyKey = "copy", className, variant = "outline", size = "icon", ...props }) {
	const [copiedKey, setCopiedKey] = import_react.useState(null);
	const handleCopy = (text, key) => {
		navigator.clipboard.writeText(text);
		setCopiedKey(key);
		setTimeout(() => {
			setCopiedKey(null);
		}, 2e3);
	};
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(Button, {
		variant,
		size,
		onClick: () => handleCopy(value, copyKey),
		className,
		...props,
		children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(AnimatedIconSwap, {
			isActive: copiedKey === copyKey,
			inactiveIcon: Copy,
			activeIcon: ClipboardCheck,
			className: props.children ? "w-3.5 h-3.5 mr-1" : "w-4 h-4",
			activeClassName: props.children ? "w-3.5 h-3.5 mr-1 text-sage" : "w-4 h-4 text-sage"
		}), props.children]
	});
}
function DownloadButton({ onDownload, className, variant = "outline", size = "icon", ...props }) {
	const [isDownloading, setIsDownloading] = import_react.useState(false);
	const handleDownload = () => {
		onDownload();
		setIsDownloading(true);
		setTimeout(() => {
			setIsDownloading(false);
		}, 1e3);
	};
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(Button, {
		variant,
		size,
		onClick: handleDownload,
		className,
		...props,
		children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
			className: "relative overflow-hidden inline-flex items-center justify-center",
			children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(motion.div, {
				animate: isDownloading ? {
					y: [
						0,
						20,
						-20,
						0
					],
					opacity: [
						1,
						0,
						0,
						1
					]
				} : {
					y: 0,
					opacity: 1
				},
				transition: {
					duration: .6,
					times: [
						0,
						.4,
						.6,
						1
					],
					ease: "easeInOut"
				},
				className: "flex items-center justify-center",
				children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Download, { className: props.children ? "w-3.5 h-3.5 mr-1" : "w-4 h-4" })
			})
		}), props.children]
	});
}
//#endregion
export { buttonVariants as i, CopyButton as n, DownloadButton as r, Button as t };
