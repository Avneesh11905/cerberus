import { o as __toESM } from "../_runtime.mjs";
import { u as require_react } from "../_libs/@floating-ui/react-dom+[...].mjs";
import { t as cn } from "./utils-DgjCne0W.mjs";
import { n as require_jsx_runtime } from "../_libs/@marsidev/react-turnstile+[...].mjs";
import { L as Eye, R as EyeOff } from "../_libs/lucide-react.mjs";
import { t as Input } from "./input-DFi7Mh72.mjs";
//#region node_modules/.nitro/vite/services/ssr/assets/password-input-wO7IT-9k.js
var import_react = /* @__PURE__ */ __toESM(require_react());
var import_jsx_runtime = require_jsx_runtime();
var PasswordInput = import_react.forwardRef(({ className, ...props }, ref) => {
	const [showPassword, setShowPassword] = import_react.useState(false);
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
		className: "relative",
		children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Input, {
			type: showPassword ? "text" : "password",
			className: cn("pr-10", className),
			ref,
			...props
		}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("button", {
			type: "button",
			onClick: () => setShowPassword(!showPassword),
			className: "absolute right-3 top-1/2 -translate-y-1/2 text-slate/50 hover:text-slate transition-colors cursor-pointer",
			"aria-label": showPassword ? "Hide password" : "Show password",
			children: showPassword ? /* @__PURE__ */ (0, import_jsx_runtime.jsx)(EyeOff, { size: 16 }) : /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Eye, { size: 16 })
		})]
	});
});
PasswordInput.displayName = "PasswordInput";
//#endregion
export { PasswordInput as t };
