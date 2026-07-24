import { createFileRoute, Link } from '@tanstack/react-router'
import { PublicLayout } from '../components/layout/PublicLayout'
import { Server, Users, Key, ShieldCheck, ArrowRight } from 'lucide-react'
import { useAuthStore } from '../store/auth'
import { motion, type Variants } from 'framer-motion'
import { useEffect, useRef } from 'react'
import gsap from 'gsap'
import { ScrollTrigger } from 'gsap/ScrollTrigger'
import { Observer } from 'gsap/Observer'
import { ScrollToPlugin } from 'gsap/ScrollToPlugin'
import { buttonVariants } from '../components/ui/button'
import { cn } from '../lib/utils'

gsap.registerPlugin(ScrollTrigger, Observer, ScrollToPlugin)

export const Route = createFileRoute('/')({
  component: LandingPage,
})

function LandingPage() {
  const accessToken = useAuthStore(state => state.accessToken)
  const isCheckingSession = useAuthStore(state => state.isCheckingSession)

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.2
      }
    }
  }

  const itemVariants: Variants = {
    hidden: { opacity: 0, y: 20 },
    visible: { opacity: 1, y: 0, transition: { type: 'spring', stiffness: 100 } }
  }

  const pageRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (!pageRef.current) return
    
    let mm = gsap.matchMedia(pageRef);
    
    mm.add("(min-width: 768px)", () => {
        // --- 1. Pinned Hero Section ---
        const heroTl = gsap.timeline({
          scrollTrigger: {
            trigger: '.hero-section',
            start: 'top 64px', // Right under navbar
            end: '+=1500', // Scroll 1500px to unlock
            pin: true,
            scrub: 1, // 1 second smoothing
          }
        })
        // Fade out text while scaling up 3D graphic and pulling cards to center of screen
        heroTl.to('.hero-text-content', { opacity: 0, y: -50, duration: 1 }, 0)
              .to('.hero-3d-graphic', { 
                scale: 1.5, 
                rotateY: 0, // Face the user directly when centered
                x: () => {
                  const el = document.querySelector('.hero-3d-graphic');
                  if (!el) return 0;
                  const rect = el.getBoundingClientRect();
                  return (window.innerWidth / 2) - (rect.left + rect.width / 2);
                },
                duration: 2 
              }, 0)
              .to('.hero-float-1', { x: 0, y: 0, rotation: 0, duration: 2 }, 0)
              .to('.hero-float-2', { x: 0, y: 0, rotation: 0, duration: 2 }, 0)
              .to('.hero-float-3', { x: 0, y: 0, rotation: 0, duration: 2 }, 0)
              .to('.hero-3d-graphic', { opacity: 0, duration: 0.5 }, 1.5)

        // --- 2. Pinned Features Section ---
        const featuresTl = gsap.timeline({
          scrollTrigger: {
            trigger: '#features',
            start: 'top 64px',
            end: '+=2000',
            pin: true,
            scrub: 1,
          }
        })
        featuresTl.from('.feature-header', { y: 30, opacity: 0, duration: 0.5 })
                  .from('.feature-card-wrapper', { 
                    y: 100, 
                    opacity: 0, 
                    rotateX: -15, 
                    stagger: 0.3, 
                    duration: 1,
                    transformPerspective: 1000
                  }, "-=0.2")

        // --- 3. Pinned Code Snippet Section ---
        const codeTl = gsap.timeline({
          scrollTrigger: {
            trigger: '.code-snippet-section',
            start: 'top 64px',
            end: '+=1500',
            pin: true,
            scrub: 1
          }
        });
        codeTl.from('.code-snippet-section .code-window', {
          x: 80, y: 20, opacity: 0, rotateY: -20, rotateX: 10, scale: 0.9, duration: 1, transformPerspective: 1500
        })
        .from('.code-snippet-section .code-dot', { scale: 0, opacity: 0, stagger: 0.1, duration: 0.3 }, "-=0.2");

        // --- 4. Pinned Integration Section ---
        const intTl = gsap.timeline({
          scrollTrigger: {
            trigger: '.integration-section',
            start: 'top 64px',
            end: '+=1500', // Scroll for 1500px to match other sections
            pin: true,
            scrub: 1
          }
        });
        
        // Use exact screen width to guarantee a massive, visible scroll
        intTl.to('.integration-section .marquee-top', { x: () => -window.innerWidth, duration: 1 }, 0)
             .to('.integration-section .marquee-bottom', { x: () => window.innerWidth, duration: 1 }, 0)

        // --- 5. Pinned CTA Section ---
        const ctaTl = gsap.timeline({
          scrollTrigger: {
            trigger: '.bottom-cta-section',
            start: 'top 64px',
            end: '+=1000',
            pin: true,
            scrub: 1,
          }
        })
        ctaTl.from('.bottom-cta-wrapper', {
          scale: 0.8,
          opacity: 0,
          y: 50,
          duration: 1
        })
    });

    // Mobile Fallback Animations (Non-pinned)
    mm.add("(max-width: 767px)", () => {
      gsap.from('.feature-card-wrapper', {
        scrollTrigger: {
          trigger: '.features-grid',
          start: 'top 80%',
          toggleActions: 'play none none reverse',
        },
        y: 30, opacity: 0, stagger: 0.1, duration: 0.8
      })

      gsap.from('.code-snippet-section .code-window', {
        scrollTrigger: { trigger: '.code-snippet-section', start: 'top 70%', toggleActions: 'play none none reverse' },
        y: 30, opacity: 0, duration: 1
      })
    });

    return () => mm.revert();
  }, [])

  return (
    <div ref={pageRef}>
      <PublicLayout>
        {/* Hero Section */}
      <section className="hero-section w-full max-w-7xl mx-auto px-4 sm:px-6 md:min-h-[calc(100vh-64px)] flex flex-col justify-center py-12 sm:py-20 md:py-0 overflow-hidden">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 lg:gap-16 xl:gap-8 items-center w-full">
          <div className="hero-text-content z-10 w-full">
            <motion.div 
              initial="hidden"
              animate="visible"
              variants={containerVariants}
              className="flex flex-col items-center lg:items-start text-center lg:text-left"
            >
              <motion.h1 variants={itemVariants} className="text-4xl sm:text-5xl lg:text-6xl xl:text-7xl font-display font-bold text-slate tracking-tight mb-6 max-w-2xl leading-[1.1]">
                Let Cerberus Guard the Gates.
              </motion.h1>
              
              <motion.p variants={itemVariants} className="text-base sm:text-lg xl:text-xl text-slate/80 font-medium max-w-xl mb-10 leading-relaxed">
                Stop rebuilding the same auth and analytics infrastructure for every project. Cerberus provides drop-in multi-tenant management, invisible bot protection, and real-time streaming analytics in one beautiful, unbreakable platform.
              </motion.p>
              
              <motion.div variants={itemVariants} className="flex flex-col sm:flex-row items-center gap-4 w-full sm:w-auto min-h-15">
                {accessToken ? (
                  <Link 
                    to="/dashboard" 
                    className={cn(buttonVariants({ variant: "primary", size: "xl" }), "w-full sm:w-auto group")}
                  >
                    Go to Dashboard
                    <ArrowRight className="ml-2 w-5 h-5 group-hover:translate-x-1 transition-transform" />
                  </Link>
                ) : isCheckingSession ? (
                  <div className="w-full sm:w-56 h-14 bg-taupe/10 animate-pulse rounded-xl" />
                ) : (
                  <Link 
                    to="/register" 
                    className={cn(buttonVariants({ variant: "primary", size: "xl" }), "w-full sm:w-auto group")}
                  >
                    Start Building Free
                    <ArrowRight className="ml-2 w-5 h-5 group-hover:translate-x-1 transition-transform" />
                  </Link>
                )}
                <a 
                  href="#features" 
                  className={cn(buttonVariants({ variant: "outline", size: "xl" }), "w-full sm:w-auto bg-sand")}
                >
                  Explore Features
                </a>
              </motion.div>
            </motion.div>
          </div>

          <div className="hero-3d-graphic w-full mt-8 lg:mt-0 z-10">
            <motion.div 
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 0.4, duration: 0.8, type: 'spring' }}
              className="flex justify-center items-center h-87.5 sm:h-112.5 lg:h-full lg:min-h-125 w-full"
            >
              <div className="w-full h-full transform scale-75 sm:scale-90 lg:scale-100 xl:scale-125 flex items-center justify-center transition-transform duration-500">
                <Hero3DGraphic />
              </div>
            </motion.div>
          </div>
        </div>
      </section>

      {/* Features Grid */}
      <section id="features" className="w-full bg-sand border-y-2 border-taupe/30 md:min-h-[calc(100vh-64px)] flex flex-col justify-center">
        <div className="w-full max-w-7xl mx-auto px-4 sm:px-6 py-16 sm:py-20 md:py-0">
          <div className="feature-header text-center mb-16">
            <h2 className="text-3xl sm:text-4xl font-display font-bold text-slate tracking-tight mb-4">
              Three Pillars of Control.
            </h2>
            <p className="text-slate/70 font-medium max-w-2xl mx-auto text-lg leading-relaxed">
              A comprehensive toolkit engineered to secure your application and scale your business, wrapped in a developer-first experience.
            </p>
          </div>

          <div className="features-grid grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            <FeatureCard 
              icon={<ShieldCheck className="w-8 h-8 text-vanilla" />}
              title="Ironclad Authentication"
              description="Deploy secure, dual-token JWT authentication in minutes. Features built-in social OAuth, OTP email verification, and invisible Cloudflare Turnstile bot protection."
            />
            <FeatureCard 
              icon={<Users className="w-8 h-8 text-vanilla" />}
              title="Multi-Tenant Architecture"
              description="Isolate your customer data effortlessly. Manage individual workspaces, customize role-based access control (RBAC), and inject custom claims dynamically."
            />
            <div className="md:col-span-2 lg:col-span-1 md:px-16 lg:px-0">
              <FeatureCard 
                icon={<Server className="w-8 h-8 text-vanilla" />}
                title="Real-Time Telemetry"
                description="Never fly blind again. Connect to a high-performance Server-Sent Events (SSE) stream to monitor active sessions, system health, and audit logs instantly."
              />
            </div>
          </div>
        </div>
      </section>

      {/* Code Snippet Section */}
      <CodeSnippetSection />

      {/* Integration Section */}
      <IntegrationSection />

      {/* Bottom CTA */}
      <section className="bottom-cta-section w-full max-w-4xl mx-auto px-4 sm:px-6 py-12 sm:py-16 md:py-0 md:min-h-[calc(100vh-64px-102px)] flex flex-col justify-center text-center overflow-hidden ">
        <div className="bottom-cta-wrapper w-full px-2 sm:px-0">
          <div className="flat-card-dark p-6 sm:p-12 rounded-2xl flex flex-col items-center">
            <Key className="w-10 h-10 sm:w-12 sm:h-12 mb-6 opacity-90 text-sand" />
            <h2 className="text-3xl sm:text-5xl font-display font-bold tracking-tight mb-4 sm:mb-6 leading-tight">
              Let Cerberus Guard the Gates.
            </h2>
            <p className="text-vanilla/80 font-medium max-w-xl mb-8 sm:mb-10 text-base sm:text-lg leading-relaxed">
              Join the next generation of developers building scalable, secure, and beautiful SaaS applications without the infrastructure headache.
            </p>
            <div className="min-h-15 w-full flex flex-col sm:flex-row justify-center items-center gap-4">
              {accessToken ? (
                <Link 
                  to="/dashboard" 
                  className={cn(buttonVariants({ variant: "inverse", size: "xl" }), "w-full sm:w-auto")}
                >
                  Go to Dashboard
                </Link>
              ) : isCheckingSession ? (
                <div className="w-full sm:w-56 h-14 bg-taupe/10 animate-pulse rounded-xl" />
              ) : (
                <Link 
                  to="/register" 
                  className={cn(buttonVariants({ variant: "inverse", size: "xl" }), "w-full sm:w-auto")}
                >
                  Create Your Account
                </Link>
              )}
            </div>
          </div>
        </div>
      </section>
    </PublicLayout>
    </div>
  )
}

function FeatureCard({ icon, title, description }: { icon: React.ReactNode, title: string, description: string }) {
  const cardRef = useRef<HTMLDivElement>(null)

  const handleMouseMove = (e: React.MouseEvent<HTMLDivElement>) => {
    if (!cardRef.current) return
    const rect = cardRef.current.getBoundingClientRect()
    const x = e.clientX - rect.left
    const y = e.clientY - rect.top
    const centerX = rect.width / 2
    const centerY = rect.height / 2
    const rotateX = ((y - centerY) / centerY) * -10
    const rotateY = ((x - centerX) / centerX) * 10

    gsap.to(cardRef.current, {
      rotateX,
      rotateY,
      transformPerspective: 1000,
      ease: "power2.out",
      duration: 0.4
    })
  }

  const handleMouseLeave = () => {
    if (!cardRef.current) return
    gsap.to(cardRef.current, {
      rotateX: 0,
      rotateY: 0,
      ease: "elastic.out(1, 0.3)",
      duration: 1
    })
  }

  return (
    <div className="feature-card-wrapper h-full">
      <div 
        ref={cardRef}
        onMouseMove={handleMouseMove}
        onMouseLeave={handleMouseLeave}
        className="flat-card bg-vanilla p-8 rounded-xl flex flex-col items-start h-full cursor-default"
      >
        <div className="w-14 h-14 rounded-lg bg-slate flex items-center justify-center flat-shadow mb-6">
          {icon}
        </div>
        <h3 className="text-xl font-bold text-slate mb-3">{title}</h3>
        <p className="text-slate/70 font-medium leading-relaxed">
          {description}
        </p>
      </div>
    </div>
  )
}

function Hero3DGraphic() {
  const containerRef = useRef<HTMLDivElement>(null)
  
  useEffect(() => {
    if (!containerRef.current) return
    
    // Continuous infinite floating on the wrappers
    const floatAnim = gsap.timeline({ repeat: -1, yoyo: true })
    floatAnim.to('.hero-float-1', { y: '-=25', duration: 3, ease: 'sine.inOut' }, 0)
    floatAnim.to('.hero-float-2', { y: '+=20', duration: 4, ease: 'sine.inOut' }, 0)
    floatAnim.to('.hero-float-3', { y: '-=15', duration: 3.5, ease: 'sine.inOut' }, 0)

    let mouseActive = false
    let timeoutId: NodeJS.Timeout

    const handleMouseMove = (e: MouseEvent) => {
      mouseActive = true
      clearTimeout(timeoutId)
      
      const x = (e.clientX / window.innerWidth) - 0.5
      const y = (e.clientY / window.innerHeight) - 0.5
      
      // Parallax ONLY on the inner cards
      gsap.to('.hero-parallax-1', {
        x: x * -100,
        y: y * -100,
        rotateX: -y * 20,
        rotateY: x * 30,
        rotateZ: (x * 10),
        ease: "power3.out",
        duration: 1.5
      })
      gsap.to('.hero-parallax-2', {
        x: x * -150,
        y: y * -150,
        rotateX: -y * 30,
        rotateY: x * 40,
        rotateZ: (x * 15),
        ease: "power3.out",
        duration: 2
      })
      gsap.to('.hero-parallax-3', {
        x: x * -250,
        y: y * -250,
        rotateX: -y * 45,
        rotateY: x * 60,
        rotateZ: (x * -20),
        ease: "power3.out",
        duration: 2.5
      })

      // Snap back inner cards when mouse leaves
      timeoutId = setTimeout(() => {
        if (mouseActive) {
          mouseActive = false
          gsap.to('.hero-parallax-1', { x: 0, y: 0, rotateX: 0, rotateY: 0, rotateZ: 0, duration: 2, ease: "power2.inOut" })
          gsap.to('.hero-parallax-2', { x: 0, y: 0, rotateX: 0, rotateY: 0, rotateZ: 0, duration: 2, ease: "power2.inOut" })
          gsap.to('.hero-parallax-3', { x: 0, y: 0, rotateX: 0, rotateY: 0, rotateZ: 0, duration: 2, ease: "power2.inOut" })
        }
      }, 500)
    }
    
    window.addEventListener('mousemove', handleMouseMove)
    return () => {
      window.removeEventListener('mousemove', handleMouseMove)
      floatAnim.kill()
      clearTimeout(timeoutId)
    }
  }, [])
  
  return (
    <div ref={containerRef} className="relative w-full h-full perspective-distant flex items-center justify-center">
      {/* Back Card - Users */}
      <div className="hero-float-1 absolute transform rotate-12 translate-x-12 -translate-y-12 origin-center z-10">
        <div className="hero-parallax-1 w-56 h-48 bg-sand rounded-xl border-2 border-taupe p-4 flex flex-col shadow-[8px_8px_0px_0px_var(--slate)] overflow-hidden">
          <div className="w-8 h-8 rounded bg-slate mb-4 flex items-center justify-center text-vanilla shrink-0"><Users size={16}/></div>
          <div className="flex items-center gap-3 mb-3 shrink-0">
            <div className="w-6 h-6 rounded-full bg-taupe/40 shrink-0" />
            <div className="flex-1 h-2 bg-taupe/40 rounded" />
          </div>
          <div className="flex items-center gap-3 mb-3 shrink-0">
            <div className="w-6 h-6 rounded-full bg-taupe/40 shrink-0" />
            <div className="flex-1 h-2 bg-taupe/40 rounded" />
          </div>
          <div className="flex items-center gap-3 shrink-0">
            <div className="w-6 h-6 rounded-full bg-taupe/40 shrink-0" />
            <div className="flex-1 h-2 bg-taupe/40 rounded" />
          </div>
        </div>
      </div>
      
      {/* Middle Card - Analytics */}
      <div className="hero-float-2 absolute transform -rotate-6 -translate-x-12 -translate-y-4 origin-center z-20">
        <div className="hero-parallax-2 w-56 h-48 bg-vanilla rounded-xl border-2 border-taupe p-4 flex flex-col justify-between overflow-hidden shadow-[8px_8px_0px_0px_var(--slate)]">
          <div className="w-8 h-8 rounded bg-slate mb-4 flex items-center justify-center text-vanilla shrink-0"><Server size={16}/></div>
          <div className="w-3/4 h-2 bg-taupe/40 rounded mb-2 shrink-0" />
          <div className="w-1/2 h-2 bg-taupe/40 rounded mb-4 shrink-0" />
          <div className="flex gap-2 items-end mt-auto h-12 shrink-0">
             <div className="w-3 h-full bg-slate rounded-sm" />
             <div className="w-3 h-3/4 bg-sage rounded-sm" />
             <div className="w-3 h-1/2 bg-terracotta rounded-sm" />
             <div className="w-3 h-full bg-slate rounded-sm" />
          </div>
        </div>
      </div>
      
      {/* Front Card - Auth */}
      <div className="hero-float-3 absolute transform rotate-2 translate-x-2 translate-y-12 origin-center z-30">
        <div className="hero-parallax-3 w-64 h-48 bg-slate text-vanilla rounded-xl border-2 border-slate p-5 flex flex-col shadow-[8px_8px_0px_0px_var(--taupe)] overflow-hidden">
          <div className="w-8 h-8 rounded bg-vanilla text-slate mb-3 flex items-center justify-center shrink-0"><ShieldCheck size={16}/></div>
          <h4 className="font-bold text-lg mb-2 font-display tracking-tight shrink-0">Access Granted</h4>
          <div className="w-full h-6 bg-vanilla/20 rounded mb-3 border border-vanilla/30 shrink-0" />
          <div className="w-full h-8 bg-vanilla rounded mt-auto flex items-center justify-center text-slate font-bold text-xs shrink-0">Authorize</div>
        </div>
      </div>
    </div>
  )
}

function CodeSnippetSection() {
  return (
    <section className="code-snippet-section w-full bg-slate border-y-2 border-slate text-vanilla py-16 sm:py-24 md:py-0 md:min-h-[calc(100vh-64px)] flex flex-col justify-center ">
      <div className="w-full max-w-7xl mx-auto px-4 sm:px-6 grid grid-cols-1 lg:grid-cols-2 gap-12 lg:gap-16 items-center">
        <div className="code-text flex flex-col items-center lg:items-start text-center lg:text-left">
          <div className="inline-flex items-center rounded-full border-2 border-vanilla/20 bg-vanilla/10 px-3 py-1 text-sm font-bold text-vanilla mb-6">
            Developer Experience
          </div>
          <h2 className="text-3xl sm:text-5xl font-display font-bold tracking-tight mb-6">
            Integration takes minutes. <br className="hidden sm:block"/> Not sprints.
          </h2>
          <p className="text-vanilla/80 text-lg leading-relaxed mb-8 max-w-xl">
            Cerberus handles the heavy lifting of security, session management, and analytics so you can focus on building your actual product. Drop in our React components or hit the REST API directly.
          </p>
          <ul className="space-y-4 text-left">
            {['Zero-config Dual-Token JWTs', 'Invisible Cloudflare Turnstile', 'SSE Real-time Data Streams', 'Automated Session Revocation'].map((item, i) => (
              <li key={i} className="flex items-center text-vanilla/90 font-medium">
                <ShieldCheck className="w-5 h-5 mr-3 text-sand shrink-0" />
                <span>{item}</span>
              </li>
            ))}
          </ul>
        </div>
        
        <div className="code-window w-full h-100 bg-vanilla rounded-xl border-4 border-taupe flat-shadow overflow-hidden flex flex-col">
          {/* Window Header */}
          <div className="w-full h-12 bg-sand border-b-4 border-taupe flex items-center px-4 gap-2 shrink-0">
            <div className="code-dot w-3 h-3 rounded-full bg-terracotta border-2 border-taupe" />
            <div className="code-dot w-3 h-3 rounded-full bg-ochre border-2 border-taupe" />
            <div className="code-dot w-3 h-3 rounded-full bg-sage border-2 border-taupe" />
            <div className="ml-4 text-xs font-bold text-slate/50 font-mono">App.tsx</div>
          </div>
          {/* Code Body */}
          <div className="p-4 sm:p-6 font-mono text-xs sm:text-sm md:text-base leading-loose text-slate overflow-auto flex-1 whitespace-nowrap">
            <div className="code-line text-sage">import {'{ CerberusProvider, useAuth }'} from <span className="text-terracotta">'cerberus-react'</span></div>
            <br className="code-line" />
            <div className="code-line text-slate">function <span className="text-ochre">App</span>() {'{'}</div>
            <div className="code-line pl-4">return (</div>
            <div className="code-line pl-8 text-sage">{'<CerberusProvider '}</div>
            <div className="code-line pl-12 text-slate">clientId=<span className="text-terracotta">"{'{'}import.meta.env.VITE_CERBERUS_ID{'}'}"</span></div>
            <div className="code-line pl-12 text-slate">requireTurnstile=<span className="text-ochre">{'{true}'}</span></div>
            <div className="code-line pl-8 text-sage">{'>'}</div>
            <div className="code-line pl-12">{'<YourApp />'}</div>
            <div className="code-line pl-8 text-sage">{'</CerberusProvider>'}</div>
            <div className="code-line pl-4">)</div>
            <div className="code-line text-slate">{'}'}</div>
          </div>
        </div>
      </div>
    </section>
  )
}

function IntegrationSection() {
  const topRow = ['React', 'Next.js', 'Vue', 'Nuxt', 'Svelte', 'SvelteKit', 'Angular', 'SolidJS', 'Astro']
  const bottomRow = ['React Native', 'Flutter', 'Swift', 'Kotlin', 'Go', 'Python', 'Node.js', 'Rust', 'Ruby']

  const MarqueeRow = ({ items, reverse = false, className = "" }: { items: string[], reverse?: boolean, className?: string }) => (
    <div className={`flex w-max ${reverse ? 'animate-marquee-reverse' : 'animate-marquee'} hover:paused md:animate-none ${className}`}>
      {[1, 2, 3].map((setIndex) => (
        <div key={setIndex} className="flex gap-6 pr-6 shrink-0 py-2">
          {items.map((tech, i) => (
            <div 
              key={`${setIndex}-${i}`} 
              className="px-8 py-5 bg-vanilla border-2 border-taupe rounded-xl text-slate font-display font-bold text-xl sm:text-2xl flat-shadow-slate flex items-center justify-center shrink-0 min-w-40 sm:min-w-50 hover:-translate-y-1 transition-transform cursor-crosshair"
            >
              {tech}
            </div>
          ))}
        </div>
      ))}
    </div>
  )

  return (
    <section className="integration-section w-full bg-sand py-16 sm:py-24 md:py-0 md:min-h-[calc(100vh-64px)] flex flex-col justify-center border-y-2 border-taupe/30 relative overflow-hidden">
      <div className="w-full max-w-7xl mx-auto px-4 sm:px-6 mb-16">
        <div className="flex flex-col items-center text-center z-10 relative">
          <h2 className="text-3xl sm:text-5xl font-display font-bold text-slate tracking-tight mb-6">Plays nice with your stack.</h2>
          <p className="text-slate/70 font-medium max-w-2xl text-lg sm:text-xl">
            Whether you're building a modern SPA, a server-rendered app, or a native mobile client, Cerberus is completely framework-agnostic.
          </p>
        </div>
      </div>
        
      <div className="relative w-full overflow-hidden mask-edges flex flex-col gap-2">
        <MarqueeRow items={topRow} className="marquee-top" />
        <MarqueeRow items={bottomRow} reverse={true} className="marquee-bottom" />
      </div>
    </section>
  )
}
