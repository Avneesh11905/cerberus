import { o as __toESM } from "../_runtime.mjs";
import { u as require_react } from "../_libs/@floating-ui/react-dom+[...].mjs";
import { t as useAuthStore } from "./auth-E6d_NOW7.mjs";
import { n as require_jsx_runtime } from "../_libs/@marsidev/react-turnstile+[...].mjs";
import { N as Key, _ as Server, et as ArrowRight, p as ShieldCheck, r as Users } from "../_libs/lucide-react.mjs";
import { _ as useNavigate } from "../_libs/@tanstack/react-router+[...].mjs";
import { t as motion } from "../_libs/framer-motion.mjs";
import { t as Button } from "./button-C-O_Pb_u.mjs";
import { i as gsapWithCSS } from "../_libs/gsap.mjs";
//#region node_modules/.nitro/vite/services/ssr/assets/routes-B07XWKmY.js
var import_react = /* @__PURE__ */ __toESM(require_react());
var import_jsx_runtime = require_jsx_runtime();
function PublicLayout({ children }) {
	const accessToken = useAuthStore((state) => state.accessToken);
	const navigate = useNavigate();
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
		className: "min-h-screen bg-vanilla flex flex-col font-sans selection:bg-slate selection:text-vanilla",
		children: [
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)("nav", {
				className: "w-full h-16 border-b-2 border-taupe/30 bg-vanilla sticky top-0 z-50",
				children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
					className: "w-full max-w-7xl mx-auto h-full px-4 sm:px-6 flex items-center justify-between",
					children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
						className: "flex items-center space-x-2",
						children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
							className: "w-8 h-8 rounded bg-slate text-vanilla flex items-center justify-center flat-shadow-taupe shrink-0",
							children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(ShieldCheck, { size: 20 })
						}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
							className: "text-xl font-display font-bold text-slate tracking-tight hidden sm:block",
							children: "Cerberus"
						})]
					}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
						className: "flex items-center space-x-2 sm:space-x-4 min-w-35 justify-end",
						children: accessToken ? /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Button, {
							variant: "outline",
							onClick: () => navigate({ to: "/dashboard" }),
							className: "text-xs sm:text-sm whitespace-nowrap bg-sand",
							children: "Go to Dashboard"
						}) : /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(import_jsx_runtime.Fragment, { children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Button, {
							variant: "ghost",
							onClick: () => navigate({ to: "/login" }),
							className: "text-xs sm:text-sm whitespace-nowrap",
							children: "Log in"
						}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Button, {
							variant: "primary",
							onClick: () => navigate({ to: "/register" }),
							className: "text-xs sm:text-sm whitespace-nowrap",
							children: "Sign up"
						})] })
					})]
				})
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)("main", {
				className: "grow",
				children
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("footer", {
				className: "w-full px-6 py-6 border-t-2 border-taupe/30 bg-sand flex flex-col items-center justify-center",
				children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
					className: "flex items-center space-x-2 mb-2",
					children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(ShieldCheck, {
						size: 20,
						className: "text-slate"
					}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
						className: "text-xl font-display font-bold text-slate tracking-tight",
						children: "Cerberus"
					})]
				}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("p", {
					className: "text-slate/70 font-medium text-xs text-center",
					children: [
						"© ",
						(/* @__PURE__ */ new Date()).getFullYear(),
						" Cerberus Platform. All rights reserved."
					]
				})]
			})
		]
	});
}
function LandingPage() {
	const accessToken = useAuthStore((state) => state.accessToken);
	const navigate = useNavigate();
	const containerVariants = {
		hidden: { opacity: 0 },
		visible: {
			opacity: 1,
			transition: { staggerChildren: .2 }
		}
	};
	const itemVariants = {
		hidden: {
			opacity: 0,
			y: 20
		},
		visible: {
			opacity: 1,
			y: 0,
			transition: {
				type: "spring",
				stiffness: 100
			}
		}
	};
	const pageRef = (0, import_react.useRef)(null);
	(0, import_react.useEffect)(() => {
		if (!pageRef.current) return;
		const mm = gsapWithCSS.matchMedia(pageRef);
		mm.add("(min-width: 768px)", () => {
			gsapWithCSS.timeline({ scrollTrigger: {
				trigger: ".hero-section",
				start: "top 64px",
				end: "+=1500",
				pin: true,
				scrub: 1
			} }).to(".hero-text-content", {
				opacity: 0,
				y: -50,
				duration: 1
			}, 0).to(".hero-3d-graphic", {
				scale: 1.5,
				rotateY: 0,
				x: () => {
					const el = document.querySelector(".hero-3d-graphic");
					if (!el) return 0;
					const rect = el.getBoundingClientRect();
					return window.innerWidth / 2 - (rect.left + rect.width / 2);
				},
				duration: 2
			}, 0).to(".hero-float-1", {
				x: 0,
				y: 0,
				rotation: 0,
				duration: 2
			}, 0).to(".hero-float-2", {
				x: 0,
				y: 0,
				rotation: 0,
				duration: 2
			}, 0).to(".hero-float-3", {
				x: 0,
				y: 0,
				rotation: 0,
				duration: 2
			}, 0).to(".hero-3d-graphic", {
				opacity: 0,
				duration: .5
			}, 1.5);
			gsapWithCSS.timeline({ scrollTrigger: {
				trigger: "#features",
				start: "top 64px",
				end: "+=2000",
				pin: true,
				scrub: 1
			} }).from(".feature-header", {
				y: 30,
				opacity: 0,
				duration: .5
			}).from(".feature-card-wrapper", {
				y: 100,
				opacity: 0,
				rotateX: -15,
				stagger: .3,
				duration: 1,
				transformPerspective: 1e3
			}, "-=0.2");
			gsapWithCSS.timeline({ scrollTrigger: {
				trigger: ".code-snippet-section",
				start: "top 64px",
				end: "+=1500",
				pin: true,
				scrub: 1
			} }).from(".code-snippet-section .code-window", {
				x: 80,
				y: 20,
				opacity: 0,
				rotateY: -20,
				rotateX: 10,
				scale: .9,
				duration: 1,
				transformPerspective: 1500
			}).from(".code-snippet-section .code-dot", {
				scale: 0,
				opacity: 0,
				stagger: .1,
				duration: .3
			}, "-=0.2");
			gsapWithCSS.timeline({ scrollTrigger: {
				trigger: ".integration-section",
				start: "top 64px",
				end: "+=1500",
				pin: true,
				scrub: 1
			} }).to(".integration-section .marquee-top", {
				x: () => -window.innerWidth,
				duration: 1
			}, 0).to(".integration-section .marquee-bottom", {
				x: () => window.innerWidth,
				duration: 1
			}, 0);
			gsapWithCSS.timeline({ scrollTrigger: {
				trigger: ".bottom-cta-section",
				start: "top 64px",
				end: "+=1000",
				pin: true,
				scrub: 1
			} }).from(".bottom-cta-wrapper", {
				scale: .8,
				opacity: 0,
				y: 50,
				duration: 1
			});
		});
		mm.add("(max-width: 767px)", () => {
			gsapWithCSS.from(".feature-card-wrapper", {
				scrollTrigger: {
					trigger: ".features-grid",
					start: "top 80%",
					toggleActions: "play none none reverse"
				},
				y: 30,
				opacity: 0,
				stagger: .1,
				duration: .8
			});
			gsapWithCSS.from(".code-snippet-section .code-window", {
				scrollTrigger: {
					trigger: ".code-snippet-section",
					start: "top 70%",
					toggleActions: "play none none reverse"
				},
				y: 30,
				opacity: 0,
				duration: 1
			});
		});
		return () => mm.revert();
	}, []);
	return /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
		ref: pageRef,
		children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(PublicLayout, { children: [
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)("section", {
				className: "hero-section w-full max-w-7xl mx-auto px-4 sm:px-6 md:min-h-[calc(100vh-64px)] flex flex-col justify-center py-12 sm:py-20 md:py-0 overflow-hidden",
				children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
					className: "grid grid-cols-1 lg:grid-cols-2 gap-12 lg:gap-16 xl:gap-8 items-center w-full",
					children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
						className: "hero-text-content z-10 w-full",
						children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(motion.div, {
							initial: "hidden",
							animate: "visible",
							variants: containerVariants,
							className: "flex flex-col items-center lg:items-start text-center lg:text-left",
							children: [
								/* @__PURE__ */ (0, import_jsx_runtime.jsx)(motion.h1, {
									variants: itemVariants,
									className: "text-4xl sm:text-5xl lg:text-6xl xl:text-7xl font-display font-bold text-slate tracking-tight mb-6 max-w-2xl leading-[1.1]",
									children: "Let Cerberus Guard the Gates."
								}),
								/* @__PURE__ */ (0, import_jsx_runtime.jsx)(motion.p, {
									variants: itemVariants,
									className: "text-base sm:text-lg xl:text-xl text-slate/80 font-medium max-w-xl mb-10 leading-relaxed",
									children: "Stop rebuilding the same auth and analytics infrastructure for every project. Cerberus provides drop-in multi-tenant management, invisible bot protection, and real-time streaming analytics in one beautiful, unbreakable platform."
								}),
								/* @__PURE__ */ (0, import_jsx_runtime.jsxs)(motion.div, {
									variants: itemVariants,
									className: "flex flex-col sm:flex-row items-center gap-4 w-full sm:w-auto min-h-15",
									children: [accessToken ? /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(Button, {
										variant: "primary",
										size: "xl",
										onClick: () => navigate({ to: "/dashboard" }),
										className: "w-full sm:w-auto group",
										children: ["Go to Dashboard", /* @__PURE__ */ (0, import_jsx_runtime.jsx)(ArrowRight, { className: "ml-2 w-5 h-5 group-hover:translate-x-1 transition-transform" })]
									}) : /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(Button, {
										variant: "primary",
										size: "xl",
										onClick: () => navigate({ to: "/register" }),
										className: "w-full sm:w-auto group",
										children: ["Start Building Free", /* @__PURE__ */ (0, import_jsx_runtime.jsx)(ArrowRight, { className: "ml-2 w-5 h-5 group-hover:translate-x-1 transition-transform" })]
									}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Button, {
										variant: "outline",
										size: "xl",
										onClick: () => document.getElementById("features")?.scrollIntoView({ behavior: "smooth" }),
										className: "w-full sm:w-auto bg-sand",
										children: "Explore Features"
									})]
								})
							]
						})
					}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
						className: "hero-3d-graphic w-full mt-8 lg:mt-0 z-10",
						children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(motion.div, {
							initial: {
								opacity: 0,
								scale: .9
							},
							animate: {
								opacity: 1,
								scale: 1
							},
							transition: {
								delay: .4,
								duration: .8,
								type: "spring"
							},
							className: "flex justify-center items-center h-87.5 sm:h-112.5 lg:h-full lg:min-h-125 w-full",
							children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
								className: "w-full h-full transform scale-75 sm:scale-90 lg:scale-100 xl:scale-125 flex items-center justify-center transition-transform duration-500",
								children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Hero3DGraphic, {})
							})
						})
					})]
				})
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)("section", {
				id: "features",
				className: "w-full bg-sand border-y-2 border-taupe/30 md:min-h-[calc(100vh-64px)] flex flex-col justify-center",
				children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
					className: "w-full max-w-7xl mx-auto px-4 sm:px-6 py-16 sm:py-20 md:py-0",
					children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
						className: "feature-header text-center mb-16",
						children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("h2", {
							className: "text-3xl sm:text-4xl font-display font-bold text-slate tracking-tight mb-4",
							children: "Three Pillars of Control."
						}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
							className: "text-slate/70 font-medium max-w-2xl mx-auto text-lg leading-relaxed",
							children: "A comprehensive toolkit engineered to secure your application and scale your business, wrapped in a developer-first experience."
						})]
					}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
						className: "features-grid grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8",
						children: [
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)(FeatureCard, {
								icon: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(ShieldCheck, { className: "w-8 h-8 text-vanilla" }),
								title: "Ironclad Authentication",
								description: "Deploy secure, dual-token JWT authentication in minutes. Features built-in social OAuth, OTP email verification, and invisible Cloudflare Turnstile bot protection."
							}),
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)(FeatureCard, {
								icon: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Users, { className: "w-8 h-8 text-vanilla" }),
								title: "Multi-Tenant Architecture",
								description: "Isolate your customer data effortlessly. Manage individual workspaces, customize role-based access control (RBAC), and inject custom claims dynamically."
							}),
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
								className: "md:col-span-2 lg:col-span-1 md:px-16 lg:px-0",
								children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(FeatureCard, {
									icon: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Server, { className: "w-8 h-8 text-vanilla" }),
									title: "Real-Time Telemetry",
									description: "Never fly blind again. Connect to a high-performance Server-Sent Events (SSE) stream to monitor active sessions, system health, and audit logs instantly."
								})
							})
						]
					})]
				})
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)(CodeSnippetSection, {}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)(IntegrationSection, {}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)("section", {
				className: "bottom-cta-section w-full max-w-4xl mx-auto px-4 sm:px-6 py-12 sm:py-16 md:py-0 md:min-h-[calc(100vh-64px-102px)] flex flex-col justify-center text-center overflow-hidden ",
				children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
					className: "bottom-cta-wrapper w-full px-2 sm:px-0",
					children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
						className: "flat-card-dark p-6 sm:p-12 rounded-2xl flex flex-col items-center",
						children: [
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Key, { className: "w-10 h-10 sm:w-12 sm:h-12 mb-6 opacity-90 text-sand" }),
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)("h2", {
								className: "text-3xl sm:text-5xl font-display font-bold tracking-tight mb-4 sm:mb-6 leading-tight",
								children: "Let Cerberus Guard the Gates."
							}),
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
								className: "text-vanilla/80 font-medium max-w-xl mb-8 sm:mb-10 text-base sm:text-lg leading-relaxed",
								children: "Join the next generation of developers building scalable, secure, and beautiful SaaS applications without the infrastructure headache."
							}),
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
								className: "min-h-15 w-full flex flex-col sm:flex-row justify-center items-center gap-4",
								children: accessToken ? /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Button, {
									variant: "inverse",
									size: "xl",
									onClick: () => navigate({ to: "/dashboard" }),
									className: "w-full sm:w-auto",
									children: "Go to Dashboard"
								}) : /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Button, {
									variant: "inverse",
									size: "xl",
									onClick: () => navigate({ to: "/register" }),
									className: "w-full sm:w-auto",
									children: "Create Your Account"
								})
							})
						]
					})
				})
			})
		] })
	});
}
function FeatureCard({ icon, title, description }) {
	const cardRef = (0, import_react.useRef)(null);
	const handleMouseMove = (e) => {
		if (!cardRef.current) return;
		const rect = cardRef.current.getBoundingClientRect();
		const x = e.clientX - rect.left;
		const y = e.clientY - rect.top;
		const centerX = rect.width / 2;
		const centerY = rect.height / 2;
		const rotateX = (y - centerY) / centerY * -10;
		const rotateY = (x - centerX) / centerX * 10;
		gsapWithCSS.to(cardRef.current, {
			rotateX,
			rotateY,
			transformPerspective: 1e3,
			ease: "power2.out",
			duration: .4
		});
	};
	const handleMouseLeave = () => {
		if (!cardRef.current) return;
		gsapWithCSS.to(cardRef.current, {
			rotateX: 0,
			rotateY: 0,
			ease: "elastic.out(1, 0.3)",
			duration: 1
		});
	};
	return /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
		className: "feature-card-wrapper h-full",
		children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
			ref: cardRef,
			onMouseMove: handleMouseMove,
			onMouseLeave: handleMouseLeave,
			className: "flat-card bg-vanilla p-8 rounded-xl flex flex-col items-start h-full cursor-default",
			children: [
				/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
					className: "w-14 h-14 rounded-lg bg-slate flex items-center justify-center flat-shadow mb-6",
					children: icon
				}),
				/* @__PURE__ */ (0, import_jsx_runtime.jsx)("h3", {
					className: "text-xl font-bold text-slate mb-3",
					children: title
				}),
				/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
					className: "text-slate/70 font-medium leading-relaxed",
					children: description
				})
			]
		})
	});
}
function Hero3DGraphic() {
	const containerRef = (0, import_react.useRef)(null);
	(0, import_react.useEffect)(() => {
		if (!containerRef.current) return;
		const floatAnim = gsapWithCSS.timeline({
			repeat: -1,
			yoyo: true
		});
		floatAnim.to(".hero-float-1", {
			y: "-=25",
			duration: 3,
			ease: "sine.inOut"
		}, 0);
		floatAnim.to(".hero-float-2", {
			y: "+=20",
			duration: 4,
			ease: "sine.inOut"
		}, 0);
		floatAnim.to(".hero-float-3", {
			y: "-=15",
			duration: 3.5,
			ease: "sine.inOut"
		}, 0);
		let mouseActive = false;
		let timeoutId;
		const handleMouseMove = (e) => {
			mouseActive = true;
			clearTimeout(timeoutId);
			const x = e.clientX / window.innerWidth - .5;
			const y = e.clientY / window.innerHeight - .5;
			gsapWithCSS.to(".hero-parallax-1", {
				x: x * -100,
				y: y * -100,
				rotateX: -y * 20,
				rotateY: x * 30,
				rotateZ: x * 10,
				ease: "power3.out",
				duration: 1.5
			});
			gsapWithCSS.to(".hero-parallax-2", {
				x: x * -150,
				y: y * -150,
				rotateX: -y * 30,
				rotateY: x * 40,
				rotateZ: x * 15,
				ease: "power3.out",
				duration: 2
			});
			gsapWithCSS.to(".hero-parallax-3", {
				x: x * -250,
				y: y * -250,
				rotateX: -y * 45,
				rotateY: x * 60,
				rotateZ: x * -20,
				ease: "power3.out",
				duration: 2.5
			});
			timeoutId = setTimeout(() => {
				if (mouseActive) {
					mouseActive = false;
					gsapWithCSS.to(".hero-parallax-1", {
						x: 0,
						y: 0,
						rotateX: 0,
						rotateY: 0,
						rotateZ: 0,
						duration: 2,
						ease: "power2.inOut"
					});
					gsapWithCSS.to(".hero-parallax-2", {
						x: 0,
						y: 0,
						rotateX: 0,
						rotateY: 0,
						rotateZ: 0,
						duration: 2,
						ease: "power2.inOut"
					});
					gsapWithCSS.to(".hero-parallax-3", {
						x: 0,
						y: 0,
						rotateX: 0,
						rotateY: 0,
						rotateZ: 0,
						duration: 2,
						ease: "power2.inOut"
					});
				}
			}, 500);
		};
		window.addEventListener("mousemove", handleMouseMove);
		return () => {
			window.removeEventListener("mousemove", handleMouseMove);
			floatAnim.kill();
			clearTimeout(timeoutId);
		};
	}, []);
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
		ref: containerRef,
		className: "relative w-full h-full perspective-distant flex items-center justify-center",
		children: [
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
				className: "hero-float-1 absolute transform rotate-12 translate-x-12 -translate-y-12 origin-center z-10",
				children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
					className: "hero-parallax-1 w-56 h-48 bg-sand rounded-xl border-2 border-taupe p-4 flex flex-col shadow-[8px_8px_0px_0px_var(--slate)] overflow-hidden",
					children: [
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
							className: "w-8 h-8 rounded bg-slate mb-4 flex items-center justify-center text-vanilla shrink-0",
							children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Users, { size: 16 })
						}),
						/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
							className: "flex items-center gap-3 mb-3 shrink-0",
							children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", { className: "w-6 h-6 rounded-full bg-taupe/40 shrink-0" }), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", { className: "flex-1 h-2 bg-taupe/40 rounded" })]
						}),
						/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
							className: "flex items-center gap-3 mb-3 shrink-0",
							children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", { className: "w-6 h-6 rounded-full bg-taupe/40 shrink-0" }), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", { className: "flex-1 h-2 bg-taupe/40 rounded" })]
						}),
						/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
							className: "flex items-center gap-3 shrink-0",
							children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", { className: "w-6 h-6 rounded-full bg-taupe/40 shrink-0" }), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", { className: "flex-1 h-2 bg-taupe/40 rounded" })]
						})
					]
				})
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
				className: "hero-float-2 absolute transform -rotate-6 -translate-x-12 -translate-y-4 origin-center z-20",
				children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
					className: "hero-parallax-2 w-56 h-48 bg-vanilla rounded-xl border-2 border-taupe p-4 flex flex-col justify-between overflow-hidden shadow-[8px_8px_0px_0px_var(--slate)]",
					children: [
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
							className: "w-8 h-8 rounded bg-slate mb-4 flex items-center justify-center text-vanilla shrink-0",
							children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Server, { size: 16 })
						}),
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", { className: "w-3/4 h-2 bg-taupe/40 rounded mb-2 shrink-0" }),
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", { className: "w-1/2 h-2 bg-taupe/40 rounded mb-4 shrink-0" }),
						/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
							className: "flex gap-2 items-end mt-auto h-12 shrink-0",
							children: [
								/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", { className: "w-3 h-full bg-slate rounded-sm" }),
								/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", { className: "w-3 h-3/4 bg-sage rounded-sm" }),
								/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", { className: "w-3 h-1/2 bg-terracotta rounded-sm" }),
								/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", { className: "w-3 h-full bg-slate rounded-sm" })
							]
						})
					]
				})
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
				className: "hero-float-3 absolute transform rotate-2 translate-x-2 translate-y-12 origin-center z-30",
				children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
					className: "hero-parallax-3 w-64 h-48 bg-slate text-vanilla rounded-xl border-2 border-slate p-5 flex flex-col shadow-[8px_8px_0px_0px_var(--taupe)] overflow-hidden",
					children: [
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
							className: "w-8 h-8 rounded bg-vanilla text-slate mb-3 flex items-center justify-center shrink-0",
							children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(ShieldCheck, { size: 16 })
						}),
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)("h4", {
							className: "font-bold text-lg mb-2 font-display tracking-tight shrink-0",
							children: "Access Granted"
						}),
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", { className: "w-full h-6 bg-vanilla/20 rounded mb-3 border border-vanilla/30 shrink-0" }),
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
							className: "w-full h-8 bg-vanilla rounded mt-auto flex items-center justify-center text-slate font-bold text-xs shrink-0",
							children: "Authorize"
						})
					]
				})
			})
		]
	});
}
function CodeSnippetSection() {
	return /* @__PURE__ */ (0, import_jsx_runtime.jsx)("section", {
		className: "code-snippet-section w-full bg-slate border-y-2 border-slate text-vanilla py-16 sm:py-24 md:py-0 md:min-h-[calc(100vh-64px)] flex flex-col justify-center ",
		children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
			className: "w-full max-w-7xl mx-auto px-4 sm:px-6 grid grid-cols-1 lg:grid-cols-2 gap-12 lg:gap-16 items-center",
			children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
				className: "code-text flex flex-col items-center lg:items-start text-center lg:text-left",
				children: [
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
						className: "inline-flex items-center rounded-full border-2 border-vanilla/20 bg-vanilla/10 px-3 py-1 text-sm font-bold text-vanilla mb-6",
						children: "Developer Experience"
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("h2", {
						className: "text-3xl sm:text-5xl font-display font-bold tracking-tight mb-6",
						children: [
							"Integration takes minutes. ",
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)("br", { className: "hidden sm:block" }),
							" Not sprints."
						]
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
						className: "text-vanilla/80 text-lg leading-relaxed mb-8 max-w-xl",
						children: "Cerberus handles the heavy lifting of security, session management, and analytics so you can focus on building your actual product. Drop in our React components or hit the REST API directly."
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)("ul", {
						className: "space-y-4 text-left",
						children: [
							"Zero-config Dual-Token JWTs",
							"Invisible Cloudflare Turnstile",
							"SSE Real-time Data Streams",
							"Automated Session Revocation"
						].map((item, i) => /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("li", {
							className: "flex items-center text-vanilla/90 font-medium",
							children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(ShieldCheck, { className: "w-5 h-5 mr-3 text-sand shrink-0" }), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", { children: item })]
						}, i))
					})
				]
			}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
				className: "code-window w-full h-100 bg-vanilla rounded-xl border-4 border-taupe flat-shadow overflow-hidden flex flex-col",
				children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
					className: "w-full h-12 bg-sand border-b-4 border-taupe flex items-center px-4 gap-2 shrink-0",
					children: [
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", { className: "code-dot w-3 h-3 rounded-full bg-terracotta border-2 border-taupe" }),
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", { className: "code-dot w-3 h-3 rounded-full bg-ochre border-2 border-taupe" }),
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", { className: "code-dot w-3 h-3 rounded-full bg-sage border-2 border-taupe" }),
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
							className: "ml-4 text-xs font-bold text-slate/50 font-mono",
							children: "App.tsx"
						})
					]
				}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
					className: "p-4 sm:p-6 font-mono text-xs sm:text-sm md:text-base leading-loose text-slate overflow-auto flex-1 whitespace-nowrap",
					children: [
						/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
							className: "code-line text-sage",
							children: [
								"import ",
								"{ CerberusProvider, useAuth }",
								" from",
								" ",
								/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
									className: "text-terracotta",
									children: "'cerberus-react'"
								})
							]
						}),
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)("br", { className: "code-line" }),
						/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
							className: "code-line text-slate",
							children: [
								"function ",
								/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
									className: "text-ochre",
									children: "App"
								}),
								"() ",
								"{"
							]
						}),
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
							className: "code-line pl-4",
							children: "return ("
						}),
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
							className: "code-line pl-8 text-sage",
							children: "<CerberusProvider "
						}),
						/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
							className: "code-line pl-12 text-slate",
							children: ["clientId=", /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("span", {
								className: "text-terracotta",
								children: [
									"\"",
									"{",
									"import.meta.env.VITE_CERBERUS_ID",
									"}",
									"\""
								]
							})]
						}),
						/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
							className: "code-line pl-12 text-slate",
							children: ["requireTurnstile=", /* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
								className: "text-ochre",
								children: "{true}"
							})]
						}),
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
							className: "code-line pl-8 text-sage",
							children: ">"
						}),
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
							className: "code-line pl-12",
							children: "<YourApp />"
						}),
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
							className: "code-line pl-8 text-sage",
							children: "</CerberusProvider>"
						}),
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
							className: "code-line pl-4",
							children: ")"
						}),
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
							className: "code-line text-slate",
							children: "}"
						})
					]
				})]
			})]
		})
	});
}
function IntegrationSection() {
	const topRow = [
		"React",
		"Next.js",
		"Vue",
		"Nuxt",
		"Svelte",
		"SvelteKit",
		"Angular",
		"SolidJS",
		"Astro"
	];
	const bottomRow = [
		"React Native",
		"Flutter",
		"Swift",
		"Kotlin",
		"Go",
		"Python",
		"Node.js",
		"Rust",
		"Ruby"
	];
	const MarqueeRow = ({ items, reverse = false, className = "" }) => /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
		className: `flex w-max ${reverse ? "animate-marquee-reverse" : "animate-marquee"} hover:paused md:animate-none ${className}`,
		children: [
			1,
			2,
			3
		].map((setIndex) => /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
			className: "flex gap-6 pr-6 shrink-0 py-2",
			children: items.map((tech, i) => /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
				className: "px-8 py-5 bg-vanilla border-2 border-taupe rounded-xl text-slate font-display font-bold text-xl sm:text-2xl flat-shadow-slate flex items-center justify-center shrink-0 min-w-40 sm:min-w-50 hover:-translate-y-1 transition-transform cursor-crosshair",
				children: tech
			}, `${setIndex}-${i}`))
		}, setIndex))
	});
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("section", {
		className: "integration-section w-full bg-sand py-16 sm:py-24 md:py-0 md:min-h-[calc(100vh-64px)] flex flex-col justify-center border-y-2 border-taupe/30 relative overflow-hidden",
		children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
			className: "w-full max-w-7xl mx-auto px-4 sm:px-6 mb-16",
			children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
				className: "flex flex-col items-center text-center z-10 relative",
				children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("h2", {
					className: "text-3xl sm:text-5xl font-display font-bold text-slate tracking-tight mb-6",
					children: "Plays nice with your stack."
				}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
					className: "text-slate/70 font-medium max-w-2xl text-lg sm:text-xl",
					children: "Whether you're building a modern SPA, a server-rendered app, or a native mobile client, Cerberus is completely framework-agnostic."
				})]
			})
		}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
			className: "relative w-full overflow-hidden mask-edges flex flex-col gap-2",
			children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(MarqueeRow, {
				items: topRow,
				className: "marquee-top"
			}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)(MarqueeRow, {
				items: bottomRow,
				reverse: true,
				className: "marquee-bottom"
			})]
		})]
	});
}
//#endregion
export { LandingPage as component };
