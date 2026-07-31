import { o as __toESM } from "../_runtime.mjs";
import { u as require_react } from "../_libs/@floating-ui/react-dom+[...].mjs";
//#region node_modules/.nitro/vite/services/ssr/assets/ProjectContext-Dh_Z2-MY.js
var import_react = /* @__PURE__ */ __toESM(require_react());
var ProjectContext = (0, import_react.createContext)(void 0);
function useProject() {
	const context = (0, import_react.useContext)(ProjectContext);
	if (!context) throw new Error("useProject must be used within a Project Layout");
	return context;
}
//#endregion
export { useProject as n, ProjectContext as t };
