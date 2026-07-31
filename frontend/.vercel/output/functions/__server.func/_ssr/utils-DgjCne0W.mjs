import { n as clsx } from "../_libs/class-variance-authority+clsx.mjs";
import { t as twMerge } from "../_libs/tailwind-merge.mjs";
//#region node_modules/.nitro/vite/services/ssr/assets/utils-DgjCne0W.js
function cn(...inputs) {
	return twMerge(clsx(inputs));
}
function handleDownloadPem(pemData, filename) {
	const dataStr = "data:application/x-pem-file;charset=utf-8," + encodeURIComponent(pemData);
	const downloadAnchorNode = document.createElement("a");
	downloadAnchorNode.setAttribute("href", dataStr);
	downloadAnchorNode.setAttribute("download", filename);
	document.body.appendChild(downloadAnchorNode);
	downloadAnchorNode.click();
	downloadAnchorNode.remove();
}
//#endregion
export { handleDownloadPem as n, cn as t };
