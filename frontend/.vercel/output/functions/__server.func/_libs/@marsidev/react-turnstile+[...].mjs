import { o as __toESM, t as __commonJSMin } from "../../_runtime.mjs";
import { u as require_react } from "../@floating-ui/react-dom+[...].mjs";
//#region node_modules/react/cjs/react-jsx-runtime.production.js
/**
* @license React
* react-jsx-runtime.production.js
*
* Copyright (c) Meta Platforms, Inc. and affiliates.
*
* This source code is licensed under the MIT license found in the
* LICENSE file in the root directory of this source tree.
*/
var require_react_jsx_runtime_production = /* @__PURE__ */ __commonJSMin(((exports) => {
	var REACT_ELEMENT_TYPE = Symbol.for("react.transitional.element");
	var REACT_FRAGMENT_TYPE = Symbol.for("react.fragment");
	function jsxProd(type, config, maybeKey) {
		var key = null;
		void 0 !== maybeKey && (key = "" + maybeKey);
		void 0 !== config.key && (key = "" + config.key);
		if ("key" in config) {
			maybeKey = {};
			for (var propName in config) "key" !== propName && (maybeKey[propName] = config[propName]);
		} else maybeKey = config;
		config = maybeKey.ref;
		return {
			$$typeof: REACT_ELEMENT_TYPE,
			type,
			key,
			ref: void 0 !== config ? config : null,
			props: maybeKey
		};
	}
	exports.Fragment = REACT_FRAGMENT_TYPE;
	exports.jsx = jsxProd;
	exports.jsxs = jsxProd;
}));
//#endregion
//#region node_modules/react/jsx-runtime.js
var require_jsx_runtime = /* @__PURE__ */ __commonJSMin(((exports, module) => {
	module.exports = require_react_jsx_runtime_production();
}));
//#endregion
//#region node_modules/@marsidev/react-turnstile/dist/index.js
var import_react = /* @__PURE__ */ __toESM(require_react(), 1);
var import_jsx_runtime = require_jsx_runtime();
var c = (0, import_react.forwardRef)(({ as: e = `div`, ...t }, n) => (0, import_jsx_runtime.jsx)(e, {
	...t,
	ref: n
}));
var l = `https://challenges.cloudflare.com/turnstile/v0/api.js`;
var u = `cf-turnstile-script`;
var f = `onloadTurnstileCallback`;
var p = (e) => !!document.getElementById(e);
var m = ({ render: e = `explicit`, onLoadCallbackName: t = f, scriptOptions: { nonce: n = ``, defer: r = !0, async: i = !0, id: a = ``, appendTo: o, onError: s, crossOrigin: c = `` } = {} }) => {
	let u = a || `cf-turnstile-script`;
	if (p(u)) return;
	let d = document.createElement(`script`);
	d.id = u, d.src = `${l}?onload=${t}&render=${e}`, !document.querySelector(`script[src="${d.src}"]`) && (d.defer = !!r, d.async = !!i, n && d.setAttribute(`nonce`, n), c && (d.crossOrigin = c), s && (d.onerror = s, delete window[t]), (o === `body` ? document.body : document.getElementsByTagName(`head`)[0]).appendChild(d));
};
var h = {
	normal: {
		width: 300,
		height: 65
	},
	compact: {
		width: 150,
		height: 140
	},
	invisible: {
		width: 0,
		height: 0,
		overflow: `hidden`
	},
	flexible: {
		minWidth: 300,
		width: `100%`,
		height: 65
	},
	interactionOnly: {
		width: `fit-content`,
		height: `auto`,
		display: `flex`
	}
};
function g(e) {
	if (e !== `invisible` && e !== `interactionOnly`) return e;
}
function _(e = u) {
	let [t, r] = (0, import_react.useState)(!1);
	return (0, import_react.useEffect)(() => {
		let t = () => {
			p(e) && r(!0);
		}, n = new MutationObserver(t);
		return n.observe(document, {
			childList: !0,
			subtree: !0
		}), t(), () => {
			n.disconnect();
		};
	}, [e]), t;
}
var v = `unloaded`;
var y;
var b = new Promise((e, t) => {
	y = {
		resolve: e,
		reject: t
	}, v === `ready` && e(void 0);
});
var x = (e = f) => (v === `unloaded` && (v = `loading`, window[e] = () => {
	y.resolve(), v = `ready`, delete window[e];
}), b);
var S = (0, import_react.forwardRef)((e, l) => {
	let { scriptOptions: u, options: d = {}, siteKey: f, onWidgetLoad: p, onSuccess: y, onExpire: b, onError: S, onBeforeInteractive: C, onAfterInteractive: w, onUnsupported: T, onTimeout: E, onLoadScript: D, id: O, style: k, as: A = `div`, injectScript: j = !0, rerenderOnCallbackChange: M = !1, ...N } = e, P = d.size, F = (0, import_react.useCallback)(() => P === void 0 ? {} : d.execution === `execute` ? h.invisible : d.appearance === `interaction-only` ? h.interactionOnly : h[P], [
		d.execution,
		P,
		d.appearance
	]), [I, L] = (0, import_react.useState)(F()), R = (0, import_react.useRef)(null), [z, B] = (0, import_react.useState)(!1), V = (0, import_react.useRef)(void 0), H = (0, import_react.useRef)(!1), U = O || `cf-turnstile`, W = (0, import_react.useRef)({
		onSuccess: y,
		onError: S,
		onExpire: b,
		onBeforeInteractive: C,
		onAfterInteractive: w,
		onUnsupported: T,
		onTimeout: E
	});
	(0, import_react.useEffect)(() => {
		M || (W.current = {
			onSuccess: y,
			onError: S,
			onExpire: b,
			onBeforeInteractive: C,
			onAfterInteractive: w,
			onUnsupported: T,
			onTimeout: E
		});
	});
	let G = u?.id || `cf-turnstile-script`, K = _(G), q = u?.onLoadCallbackName || `onloadTurnstileCallback`, J = d.appearance || `always`, Y = (0, import_react.useMemo)(() => ({
		sitekey: f,
		action: d.action,
		cData: d.cData,
		theme: d.theme || `auto`,
		language: d.language || `auto`,
		tabindex: d.tabIndex,
		"response-field": d.responseField,
		"response-field-name": d.responseFieldName,
		size: g(P),
		retry: d.retry || `auto`,
		"retry-interval": d.retryInterval || 8e3,
		"refresh-expired": d.refreshExpired || `auto`,
		"refresh-timeout": d.refreshTimeout || `auto`,
		execution: d.execution || `render`,
		appearance: d.appearance || `always`,
		"feedback-enabled": d.feedbackEnabled ?? !0,
		callback: (e) => {
			H.current = !0, M ? y?.(e) : W.current.onSuccess?.(e);
		},
		"error-callback": M ? S : (...e) => W.current.onError?.(...e),
		"expired-callback": M ? b : (...e) => W.current.onExpire?.(...e),
		"before-interactive-callback": M ? C : (...e) => W.current.onBeforeInteractive?.(...e),
		"after-interactive-callback": M ? w : (...e) => W.current.onAfterInteractive?.(...e),
		"unsupported-callback": M ? T : (...e) => W.current.onUnsupported?.(...e),
		"timeout-callback": M ? E : (...e) => W.current.onTimeout?.(...e)
	}), [
		d.action,
		d.appearance,
		d.cData,
		d.execution,
		d.language,
		d.refreshExpired,
		d.responseField,
		d.responseFieldName,
		d.retry,
		d.retryInterval,
		d.tabIndex,
		d.theme,
		d.feedbackEnabled,
		d.refreshTimeout,
		f,
		P,
		M,
		M ? y : null,
		M ? S : null,
		M ? b : null,
		M ? C : null,
		M ? w : null,
		M ? T : null,
		M ? E : null
	]), X = (0, import_react.useCallback)(() => typeof window < `u` && !!window.turnstile, []);
	return (0, import_react.useEffect)(function() {
		j && !z && (x(q), m({
			onLoadCallbackName: q,
			scriptOptions: {
				...u,
				id: G
			}
		}));
	}, [
		j,
		z,
		u,
		G,
		q
	]), (0, import_react.useEffect)(function() {
		v !== `ready` && x(q).then(() => B(!0)).catch(console.error);
	}, [q]), (0, import_react.useEffect)(function() {
		if (!R.current || !z) return;
		let e = !1;
		return (async () => {
			e || !R.current || (V.current = window.turnstile.render(R.current, Y), V.current && p?.(V.current));
		})(), () => {
			e = !0, V.current && (window.turnstile.remove(V.current), H.current = !1);
		};
	}, [
		U,
		z,
		Y
	]), (0, import_react.useImperativeHandle)(l, () => {
		let { turnstile: e } = window;
		return {
			getResponse() {
				if (!e?.getResponse || !V.current || !X()) {
					console.warn(`Turnstile has not been loaded`);
					return;
				}
				return e.getResponse(V.current);
			},
			async getResponsePromise(e = 3e4, t = 100) {
				return new Promise((n, r) => {
					let i, a = async () => {
						if (H.current && window.turnstile && V.current) try {
							let e = window.turnstile.getResponse(V.current);
							return i && clearTimeout(i), e ? n(e) : r(Error(`No response received`));
						} catch (e) {
							return i && clearTimeout(i), console.warn(`Failed to get response`, e), r(Error(`Failed to get response`));
						}
						i ||= setTimeout(() => {
							i && clearTimeout(i), r(Error(`Timeout`));
						}, e), await new Promise((e) => setTimeout(e, t)), await a();
					};
					a();
				});
			},
			reset() {
				if (!e?.reset || !V.current || !X()) {
					console.warn(`Turnstile has not been loaded`);
					return;
				}
				d.execution === `execute` && L(h.invisible);
				try {
					H.current = !1, e.reset(V.current);
				} catch (e) {
					console.warn(`Failed to reset Turnstile widget ${V.current}`, e);
				}
			},
			remove() {
				if (!e?.remove || !V.current || !X()) {
					console.warn(`Turnstile has not been loaded`);
					return;
				}
				L(h.invisible), H.current = !1, e.remove(V.current), V.current = null;
			},
			render() {
				if (!e?.render || !R.current || !X() || V.current) {
					console.warn(`Turnstile has not been loaded or container not found`);
					return;
				}
				let t = e.render(R.current, Y);
				return V.current = t, V.current && p?.(V.current), d.execution !== `execute` && L(P ? h[P] : {}), t;
			},
			execute() {
				if (d.execution !== `execute`) {
					console.warn(`Execution mode is not set to "execute"`);
					return;
				}
				if (!e?.execute || !R.current || !V.current || !X()) {
					console.warn(`Turnstile has not been loaded or container not found`);
					return;
				}
				e.execute(R.current), L(P ? h[P] : {});
			},
			isExpired() {
				return !e?.isExpired || !V.current || !X() ? (console.warn(`Turnstile has not been loaded`), !1) : e.isExpired(V.current);
			}
		};
	}, [
		V,
		d.execution,
		P,
		Y,
		R,
		X,
		z,
		p
	]), (0, import_react.useEffect)(() => {
		if (z || !K) return;
		if (window.turnstile) {
			B(!0);
			return;
		}
		let e = setInterval(() => {
			window.turnstile && (B(!0), clearInterval(e));
		}, 50);
		return () => {
			clearInterval(e);
		};
	}, [z, K]), (0, import_react.useEffect)(() => {
		L(F());
	}, [
		d.execution,
		P,
		J
	]), (0, import_react.useEffect)(() => {
		!K || typeof D != `function` || D();
	}, [K]), (0, import_jsx_runtime.jsx)(c, {
		ref: R,
		as: A,
		id: U,
		style: {
			...I,
			...k
		},
		...N
	});
});
S.displayName = `Turnstile`;
//#endregion
export { require_jsx_runtime as n, S as t };
