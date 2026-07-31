import { n as persist, r as create, t as createJSONStorage } from "../_libs/zustand.mjs";
//#region node_modules/.nitro/vite/services/ssr/assets/auth-E6d_NOW7.js
var safeStorage = {
	getItem: (name) => {
		if (typeof window === "undefined") return null;
		return window.localStorage.getItem(name);
	},
	setItem: (name, value) => {
		if (typeof window === "undefined") return;
		window.localStorage.setItem(name, value);
	},
	removeItem: (name) => {
		if (typeof window === "undefined") return;
		window.localStorage.removeItem(name);
	}
};
var useAuthStore = create()(persist((set) => ({
	accessToken: null,
	csrfToken: null,
	user: null,
	unverifiedEmail: null,
	verifiedEmail: null,
	otpExpiresAt: null,
	resendAvailableAt: null,
	setAuth: (accessToken, csrfToken, user) => set({
		accessToken,
		csrfToken,
		user
	}),
	setAccessToken: (accessToken, csrfToken) => set((state) => ({
		accessToken,
		csrfToken: csrfToken !== void 0 ? csrfToken : state.csrfToken
	})),
	setUser: (user) => set({ user }),
	setUnverifiedEmail: (unverifiedEmail) => set({ unverifiedEmail }),
	setVerifiedEmail: (verifiedEmail) => set({ verifiedEmail }),
	setOtpExpiresAt: (otpExpiresAt) => set({ otpExpiresAt }),
	setResendAvailableAt: (resendAvailableAt) => set({ resendAvailableAt }),
	logout: () => set({
		accessToken: null,
		csrfToken: null,
		user: null,
		unverifiedEmail: null,
		verifiedEmail: null,
		otpExpiresAt: null,
		resendAvailableAt: null
	})
}), {
	name: "cerberus-auth",
	storage: createJSONStorage(() => safeStorage),
	partialize: (state) => ({
		accessToken: state.accessToken,
		csrfToken: state.csrfToken,
		user: state.user,
		unverifiedEmail: state.unverifiedEmail,
		verifiedEmail: state.verifiedEmail,
		otpExpiresAt: state.otpExpiresAt,
		resendAvailableAt: state.resendAvailableAt
	})
}));
//#endregion
export { useAuthStore as t };
