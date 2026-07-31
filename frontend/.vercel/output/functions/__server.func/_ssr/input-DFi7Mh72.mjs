import { o as __toESM } from "../_runtime.mjs";
import { u as require_react } from "../_libs/@floating-ui/react-dom+[...].mjs";
import { t as cn } from "./utils-DgjCne0W.mjs";
import { n as require_jsx_runtime } from "../_libs/@marsidev/react-turnstile+[...].mjs";
//#region node_modules/.nitro/vite/services/ssr/assets/input-DFi7Mh72.js
var import_react = /* @__PURE__ */ __toESM(require_react());
var import_jsx_runtime = require_jsx_runtime();
var Input = import_react.forwardRef(({ className, type, ...props }, ref) => {
	return /* @__PURE__ */ (0, import_jsx_runtime.jsx)("input", {
		type,
		className: cn("flex h-10 w-full rounded-xl border-2 border-taupe bg-vanilla px-3 py-2 text-sm text-slate font-medium ring-offset-vanilla file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-taupe focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-slate focus-visible:border-slate disabled:cursor-not-allowed disabled:opacity-50 transition-colors", className),
		ref,
		...props
	});
});
Input.displayName = "Input";
//#endregion
export { Input as t };
