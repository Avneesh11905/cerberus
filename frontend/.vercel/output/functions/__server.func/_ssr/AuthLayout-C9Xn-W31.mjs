import "../_runtime.mjs";
import { u as require_react } from "../_libs/@floating-ui/react-dom+[...].mjs";
import { n as require_jsx_runtime } from "../_libs/@marsidev/react-turnstile+[...].mjs";
import { tt as ArrowLeft } from "../_libs/lucide-react.mjs";
import { y as useRouter } from "../_libs/@tanstack/react-router+[...].mjs";
import { t as motion } from "../_libs/framer-motion.mjs";
require_react();
var import_jsx_runtime = require_jsx_runtime();
function AuthLayout({ children, title, subtitle, showBackButton = true, maxWidth = "max-w-md" }) {
	const router = useRouter();
	return /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
		className: "min-h-screen bg-vanilla flex items-center justify-center p-4",
		children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(motion.div, {
			initial: {
				opacity: 0,
				y: 20
			},
			animate: {
				opacity: 1,
				y: 0
			},
			transition: {
				duration: .6,
				ease: [
					.16,
					1,
					.3,
					1
				]
			},
			className: `w-full ${maxWidth} perspective-[1000px]`,
			children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
				className: "flat-card p-6 sm:p-8 rounded-xl flex flex-col relative",
				children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", { children: [
					showBackButton && /* @__PURE__ */ (0, import_jsx_runtime.jsx)("button", {
						type: "button",
						onClick: () => router.history.back(),
						className: "absolute top-6 left-6 text-slate/50 hover:text-slate transition-colors",
						"aria-label": "Go back",
						children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(ArrowLeft, { size: 20 })
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
						className: "mb-6 sm:mb-8 text-center",
						children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("h1", {
							className: "text-2xl sm:text-3xl font-display font-bold text-slate mb-2 tracking-tight",
							children: title
						}), subtitle && /* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
							className: "text-slate/70 text-sm font-medium",
							children: subtitle
						})]
					}),
					children
				] })
			})
		})
	});
}
//#endregion
export { AuthLayout as t };
