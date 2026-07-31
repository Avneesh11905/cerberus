import { o as __toESM } from "./_runtime.mjs";
import { u as require_react } from "./_libs/@floating-ui/react-dom+[...].mjs";
import { t as axios } from "./_libs/axios+[...].mjs";
import { i as extractErrorMessage } from "./_ssr/api-client-DJkUESpZ.mjs";
import { n as require_jsx_runtime } from "./_libs/@marsidev/react-turnstile+[...].mjs";
import { Y as Check, b as Save, s as TriangleAlert, x as RefreshCw } from "./_libs/lucide-react.mjs";
import { n as AnimatePresence, t as motion } from "./_libs/framer-motion.mjs";
import { t as Button } from "./_ssr/button-C-O_Pb_u.mjs";
import { n as useProject } from "./_ssr/ProjectContext-Dh_Z2-MY.mjs";
import { d as updateProjectClaims } from "./_ssr/projects-B5Nezf2L.mjs";
import { n as toast } from "./_libs/sonner.mjs";
import { a as CardHeader, i as CardFooter, n as CardContent, o as CardTitle, r as CardDescription, t as Card } from "./_ssr/card-D2S-3Lsc.mjs";
import { t as Label } from "./_ssr/label-CFPE1x7g.mjs";
import { t as Route } from "./_protected.projects._projectId.claims-Bd_s5v_j.mjs";
import { a as record, o as string, t as any } from "./_libs/zod.mjs";
import { t as require_lib } from "./_libs/react-simple-code-editor.mjs";
import { t as require_prism } from "./_libs/prismjs.mjs";
//#region node_modules/.nitro/vite/services/ssr/assets/_protected.projects._projectId.claims-BOWtbi76.js
var import_react = /* @__PURE__ */ __toESM(require_react());
var import_jsx_runtime = require_jsx_runtime();
var import_lib = /* @__PURE__ */ __toESM(require_lib());
var import_prism = /* @__PURE__ */ __toESM(require_prism());
var Editor = import_lib.default.default || import_lib.default;
function ClaimsTab() {
	const { projectId } = Route.useParams();
	const { project, fetchProject } = useProject();
	const [claimsJson, setClaimsJson] = (0, import_react.useState)("{\n  \n}");
	const [claimsError, setClaimsError] = (0, import_react.useState)("");
	const [savingClaims, setSavingClaims] = (0, import_react.useState)(false);
	const [claimsSaved, setClaimsSaved] = (0, import_react.useState)(false);
	(0, import_react.useEffect)(() => {
		setClaimsJson(JSON.stringify(project.default_claims, null, 2));
	}, [project]);
	const handleFormatJson = () => {
		try {
			if (!claimsJson.trim()) return;
			const parsed = JSON.parse(claimsJson);
			setClaimsJson(JSON.stringify(parsed, null, 2));
			setClaimsError("");
		} catch (e) {
			setClaimsError("Invalid JSON: Cannot format");
		}
	};
	const handleEditorKeyDown = (e) => {
		const target = e.target;
		const { selectionStart, selectionEnd, value } = target;
		const pairs = {
			"\"": "\"",
			"'": "'",
			"{": "}",
			"[": "]",
			"(": ")"
		};
		if (pairs[e.key]) {
			e.preventDefault();
			const closing = pairs[e.key];
			const newValue = value.substring(0, selectionStart) + e.key + closing + value.substring(selectionEnd);
			setClaimsJson(newValue);
			requestAnimationFrame(() => {
				target.selectionStart = target.selectionEnd = selectionStart + 1;
			});
		} else if (e.key === "Backspace" && selectionStart === selectionEnd && selectionStart > 0) {
			const prevChar = value[selectionStart - 1];
			const nextChar = value[selectionStart];
			if (pairs[prevChar] === nextChar) {
				e.preventDefault();
				const newValue = value.substring(0, selectionStart - 1) + value.substring(selectionEnd + 1);
				setClaimsJson(newValue);
				requestAnimationFrame(() => {
					target.selectionStart = target.selectionEnd = selectionStart - 1;
				});
			}
		}
	};
	const handleSaveClaims = async (e) => {
		e.preventDefault();
		setSavingClaims(true);
		setClaimsError("");
		try {
			const claimsObj = JSON.parse(claimsJson);
			if (typeof claimsObj !== "object" || Array.isArray(claimsObj) || claimsObj === null) {
				setClaimsError("Claims must be a JSON object");
				setSavingClaims(false);
				return;
			}
			const result = record(string(), any()).refine((obj) => Object.keys(obj).length <= 10, "Maximum 10 custom claims allowed.").refine((obj) => {
				const reserved = [
					"sub",
					"email",
					"exp",
					"iat",
					"jti",
					"project_id",
					"is_verified",
					"family_id"
				];
				return !Object.keys(obj).some((k) => reserved.includes(k));
			}, "Cannot use reserved claims.").safeParse(claimsObj);
			if (!result.success) {
				setClaimsError(result.error.issues[0].message);
				setSavingClaims(false);
				return;
			}
			await updateProjectClaims(projectId, claimsObj);
			setClaimsSaved(true);
			setTimeout(() => setClaimsSaved(false), 2e3);
			fetchProject(false);
		} catch (error) {
			if (error instanceof SyntaxError) setClaimsError("Invalid JSON format");
			else if (axios.isAxiosError(error) && error.response?.status === 422 && error.response.data.detail[0]?.msg) setClaimsError(error.response.data.detail[0].msg);
			else toast.error(extractErrorMessage(error, "Failed to update claims"));
		} finally {
			setSavingClaims(false);
		}
	};
	return /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
		className: "flex flex-col gap-6 w-full animate-in fade-in slide-in-from-bottom-2 duration-300",
		children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)("form", {
			onSubmit: handleSaveClaims,
			children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(Card, { children: [
				/* @__PURE__ */ (0, import_jsx_runtime.jsxs)(CardHeader, { children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(CardTitle, { children: "Custom Default Claims Mapping" }), /* @__PURE__ */ (0, import_jsx_runtime.jsx)(CardDescription, { children: "Map custom default user metadata into the JWT payloads issued by Cerberus." })] }),
				/* @__PURE__ */ (0, import_jsx_runtime.jsxs)(CardContent, {
					className: "space-y-4",
					children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
						className: "bg-terracotta/10 border-2 border-terracotta p-4 rounded-xl",
						children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
							className: "text-sm font-semibold text-terracotta flex items-start gap-2",
							children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(TriangleAlert, { className: "w-5 h-5 shrink-0" }), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", { children: [
								/* @__PURE__ */ (0, import_jsx_runtime.jsx)("strong", { children: "Reserved Claims:" }),
								" You cannot map the following reserved claims:",
								/* @__PURE__ */ (0, import_jsx_runtime.jsx)("br", {}),
								/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
									className: "flex flex-wrap gap-1 mt-2",
									children: [
										"sub",
										"email",
										"exp",
										"iat",
										"jti",
										"project_id",
										"is_verified",
										"family_id"
									].map((claim) => /* @__PURE__ */ (0, import_jsx_runtime.jsx)("code", {
										className: "bg-terracotta/20 px-1.5 py-0.5 rounded text-xs font-mono",
										children: claim
									}, claim))
								}),
								/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
									className: "text-xs mt-3 block font-bold",
									children: "Maximum 10 custom claims allowed."
								})
							] })]
						})
					}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
						className: "space-y-2",
						children: [
							/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
								className: "flex items-center justify-between",
								children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Label, {
									htmlFor: "claimsJson",
									children: "Claims (JSON)"
								}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Button, {
									type: "button",
									variant: "outline",
									size: "sm",
									onClick: handleFormatJson,
									className: "h-8 text-xs",
									children: "Format JSON"
								})]
							}),
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
								className: `w-full font-mono text-sm border-2 rounded-xl bg-vanilla focus-within:ring-2 overflow-hidden transition-colors ${claimsError ? "border-terracotta focus-within:ring-terracotta" : "border-taupe focus-within:ring-slate"}`,
								children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Editor, {
									value: claimsJson,
									onValueChange: (val) => {
										setClaimsJson(val);
										setClaimsError("");
									},
									onKeyDown: handleEditorKeyDown,
									highlight: (code) => import_prism.default.highlight(code, import_prism.default.languages.javascript, "javascript"),
									padding: 16,
									style: {
										fontFamily: "ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, \"Liberation Mono\", \"Courier New\", monospace",
										fontSize: 14,
										minHeight: "200px"
									},
									textareaId: "claimsJson",
									className: "w-full focus-visible:outline-none"
								})
							}),
							claimsError && /* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
								className: "text-sm font-bold text-terracotta",
								children: claimsError
							})
						]
					})]
				}),
				/* @__PURE__ */ (0, import_jsx_runtime.jsx)(CardFooter, {
					className: "flex justify-end border-t-2 border-taupe/20 pt-6",
					children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(Button, {
						type: "submit",
						disabled: savingClaims || claimsSaved,
						className: `relative overflow-hidden w-35 transition-all duration-300 ${claimsSaved ? "bg-sage! text-vanilla! border-sage!" : ""}`,
						children: [
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)(AnimatePresence, {
								mode: "wait",
								children: savingClaims ? /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(motion.div, {
									initial: {
										opacity: 0,
										y: 10
									},
									animate: {
										opacity: 1,
										y: 0
									},
									exit: {
										opacity: 0,
										y: -10
									},
									className: "flex items-center justify-center gap-2 absolute inset-0",
									children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(RefreshCw, { className: "w-4 h-4 animate-spin" }), "Saving..."]
								}, "saving") : claimsSaved ? /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(motion.div, {
									initial: {
										opacity: 0,
										scale: .5
									},
									animate: {
										opacity: 1,
										scale: 1
									},
									exit: {
										opacity: 0,
										scale: .8
									},
									className: "flex items-center justify-center gap-2 absolute inset-0",
									children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Check, { className: "w-4 h-4" }), "Saved!"]
								}, "saved") : /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(motion.div, {
									initial: {
										opacity: 0,
										y: 10
									},
									animate: {
										opacity: 1,
										y: 0
									},
									exit: {
										opacity: 0,
										y: -10
									},
									className: "flex items-center justify-center gap-2 absolute inset-0",
									children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Save, { className: "w-4 h-4" }), "Save Claims"]
								}, "default")
							}),
							/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
								className: "invisible flex items-center gap-2",
								children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Save, { className: "w-4 h-4" }), "Save Claims"]
							}),
							claimsSaved && /* @__PURE__ */ (0, import_jsx_runtime.jsx)(motion.div, {
								initial: {
									scale: 0,
									opacity: .4
								},
								animate: {
									scale: 3,
									opacity: 0
								},
								transition: {
									duration: .6,
									ease: "easeOut"
								},
								className: "absolute inset-0 bg-vanilla rounded-full origin-center pointer-events-none"
							})
						]
					})
				})
			] })
		})
	});
}
//#endregion
export { ClaimsTab as component };
