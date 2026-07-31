import { o as __toESM } from "../_runtime.mjs";
import { u as require_react } from "../_libs/@floating-ui/react-dom+[...].mjs";
import { t as cn } from "./utils-DgjCne0W.mjs";
import { n as require_jsx_runtime } from "../_libs/@marsidev/react-turnstile+[...].mjs";
//#region node_modules/.nitro/vite/services/ssr/assets/label-CFPE1x7g.js
var import_react = /* @__PURE__ */ __toESM(require_react());
var import_jsx_runtime = require_jsx_runtime();
var Label = import_react.forwardRef(({ className, ...props }, ref) => /* @__PURE__ */ (0, import_jsx_runtime.jsx)("label", {
	ref,
	className: cn("text-sm font-bold leading-none text-slate peer-disabled:cursor-not-allowed peer-disabled:opacity-70", className),
	...props
}));
Label.displayName = "Label";
//#endregion
export { Label as t };
