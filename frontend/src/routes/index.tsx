import { createFileRoute, Link } from '@tanstack/react-router'
import { useState, useCallback } from 'react'
import { Shield, Zap, ChevronRight, Key, Layers, Code2 } from 'lucide-react'
import { useAuth } from '#/lib/auth'
import { UserNav } from '#/components/UserNav'
import { ThemeToggle } from '#/components/ThemeToggle'
import { CodeBlock } from '#/components/CodeBlock'

export const Route = createFileRoute('/')({
  component: LandingPage,
})

function LandingPage() {
  const { user, isLoading } = useAuth()
  const [isScrolled, setIsScrolled] = useState(false)

  const showcaseCode = `import { CerberusClient } from '@cerberus/sdk'

// 1. Initialize the Frontend SDK
export const cerberus = new CerberusClient({
  apiKey: 'cerb_XXXXXXXXXX'
})

// 2. Authenticate seamlessly
await cerberus.auth.login({
  email: 'founder@startup.com',
  password: 'SecurePass123!'
})

// 3. Fetch the current user profile
const user = await cerberus.users.getMe()
console.log(\`Welcome back, \${user.email}\`)`

  const handleScroll = useCallback((e: React.UIEvent<HTMLDivElement>) => {
    setIsScrolled(e.currentTarget.scrollTop > 900)
  }, [])

  return (
    <div
      className="h-screen w-full overflow-y-auto custom-scrollbar"
      onScroll={handleScroll}
    >
      <div className="relative min-h-screen bg-slate-50 dark:bg-background text-slate-900 dark:text-slate-50 overflow-x-hidden selection:bg-primary/30 select-none">
        {/* Background Effects */}
        <div
          className="fixed inset-0 bg-[linear-gradient(to_right,#cbd5e1_1px,transparent_1px),linear-gradient(to_bottom,#cbd5e1_1px,transparent_1px)] dark:bg-[linear-gradient(to_right,#ffffff0a_1px,transparent_1px),linear-gradient(to_bottom,#ffffff0a_1px,transparent_1px)] bg-size-[32px_32px] pointer-events-none mask-image-gradient"
          style={{
            WebkitMaskImage:
              'radial-gradient(ellipse 80% 50% at 50% 0%, #000 70%, transparent 100%)',
          }}
        />
        <div className="fixed top-0 left-1/2 -translate-x-1/2 w-250 h-125 bg-primary/30 dark:bg-primary/20 blur-[120px] rounded-full pointer-events-none opacity-60" />

        {/* Navigation */}
        <nav
          className={`fixed top-0 left-0 right-0 z-50 flex items-center justify-between px-6 lg:px-12 py-4 w-full transition-all duration-300 bg-transparent border-b border-transparent ${isScrolled ? '-translate-y-full opacity-0 pointer-events-none' : 'translate-y-0 opacity-100'}`}
        >
          <div className="flex items-center gap-3 select-none cursor-default">
            <img
              src="/logo.webp"
              alt="Cerberus"
              className="w-10 h-10 md:w-12 md:h-12 select-none"
              draggable={false}
            />
            <span
              className="text-xl md:text-2xl tracking-tight text-slate-900 dark:text-white"
              style={{ fontFamily: 'Audiowide, sans-serif' }}
            >
              Cerberus
            </span>
          </div>

          <div className="flex items-center gap-4 sm:gap-6">
            <ThemeToggle />
            {isLoading ? (
              <div className="w-8 h-8 rounded-full bg-slate-200 dark:bg-slate-800 animate-pulse" />
            ) : user ? (
              <UserNav />
            ) : (
              <div className="flex items-center gap-3">
                <Link
                  to="/auth/login"
                  className="text-sm font-medium text-slate-700 dark:text-slate-300 hover:text-slate-900 dark:hover:text-white transition-colors"
                >
                  Sign In
                </Link>
                <Link
                  to="/auth/register"
                  className="hidden sm:inline-flex items-center justify-center px-4 py-2 text-sm font-medium text-white bg-primary hover:bg-primary/90 rounded-full transition-all hover:scale-105 active:scale-95 shadow-lg shadow-primary/25"
                >
                  Get Started
                </Link>
              </div>
            )}
          </div>
        </nav>

        <main className="relative z-10 flex flex-col items-center">
          {/* Hero Section */}
          <section className="w-full px-6 pt-32 pb-20 md:pt-40 md:pb-32 mx-auto max-w-7xl text-center">
            <h1
              className="text-5xl md:text-7xl lg:text-8xl font-extrabold tracking-tight text-slate-900 dark:text-white mb-8 opacity-0-init animate-fade-in-up animate-delay-100 leading-[1.1]"
              style={{ fontFamily: 'Audiowide, sans-serif' }}
            >
              Manage Your <br className="hidden md:block" />
              <span className="text-transparent bg-clip-text bg-linear-to-r from-indigo-600 to-violet-600 dark:from-indigo-400 dark:to-violet-400">
                Identity Infrastructure.
              </span>
            </h1>

            <p className="text-lg md:text-xl text-slate-600 dark:text-slate-400 max-w-2xl mx-auto mb-10 leading-relaxed opacity-0-init animate-fade-in-up animate-delay-200">
              A comprehensive multi-project platform to oversee your
              authentication. Effortlessly create projects, configure identity
              providers, manage access keys, and monitor user sessions.
            </p>

            <div className="flex flex-col sm:flex-row items-center justify-center gap-4 w-full sm:w-auto opacity-0-init animate-fade-in-up animate-delay-300 select-auto">
              {isLoading ? (
                <div className="w-48 h-14 rounded-full bg-slate-200 dark:bg-slate-800 animate-pulse" />
              ) : user ? (
                <Link
                  to="/dashboard"
                  className="group relative flex items-center justify-center gap-2 w-full sm:w-auto px-8 py-3.5 text-base font-semibold text-white bg-indigo-600 rounded-full overflow-hidden transition-all hover:bg-indigo-700 active:scale-95 shadow-lg shadow-indigo-500/25"
                >
                  <span>Go to Dashboard</span>
                  <ChevronRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
                </Link>
              ) : (
                <Link
                  to="/auth/register"
                  className="group relative flex items-center justify-center gap-2 w-full sm:w-auto px-8 py-3.5 text-base font-semibold text-white bg-indigo-600 rounded-full overflow-hidden transition-all hover:bg-indigo-700 active:scale-95 shadow-lg shadow-indigo-500/25"
                >
                  <span>Start building for free</span>
                  <ChevronRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
                </Link>
              )}
              <Link
                to="/docs"
                className="flex items-center justify-center gap-2 w-full sm:w-auto px-8 py-3.5 text-base font-medium text-slate-700 dark:text-slate-200 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-full hover:bg-slate-50 dark:hover:bg-slate-700 transition-all shadow-sm"
              >
                <Code2 className="w-5 h-5" />
                SDK Docs
              </Link>
            </div>
          </section>

          {/* Code Showcase Section */}
          <section className="w-full px-6 pb-24 mx-auto max-w-6xl opacity-0-init animate-fade-in-up animate-delay-400 mt-12">
            <div className="grid lg:grid-cols-2 gap-8 md:gap-16 items-center">
              <div className="text-left space-y-6">
                <h2 className="text-3xl md:text-4xl font-bold tracking-tight text-slate-900 dark:text-white leading-tight">
                  Authentication that stays out of your way.
                </h2>
                <p className="text-lg text-slate-600 dark:text-slate-400 leading-relaxed">
                  Cerberus SDK handles the heavy lifting. Token rotation, secure
                  cookies, and API retries happen silently in the background,
                  leaving your codebase clean and focused on your product.
                </p>
                <div className="flex gap-8 pt-4">
                  <div className="flex flex-col gap-1">
                    <span className="text-4xl font-bold text-indigo-500 tracking-tighter">
                      3x
                    </span>
                    <span className="text-xs font-semibold text-slate-500 uppercase tracking-widest">
                      Faster Setup
                    </span>
                  </div>
                  <div className="w-px h-14 bg-slate-200 dark:bg-slate-800 self-center" />
                  <div className="flex flex-col gap-1">
                    <span className="text-4xl font-bold text-indigo-500 tracking-tighter">
                      0
                    </span>
                    <span className="text-xs font-semibold text-slate-500 uppercase tracking-widest">
                      Security Leaks
                    </span>
                  </div>
                </div>
              </div>

              <div className="relative group">
                <div className="absolute -inset-4 bg-linear-to-tr from-indigo-500/20 to-purple-500/20 blur-2xl opacity-0 group-hover:opacity-100 transition-opacity duration-500 pointer-events-none rounded-3xl" />
                <CodeBlock
                  code={showcaseCode}
                  language="typescript"
                  title="auth.ts"
                  className="my-0 relative z-10"
                  hideCopy
                  unselectable
                />
              </div>
            </div>
          </section>

          {/* Bento Box Features Section */}
          <section
            id="features"
            className="w-full py-24 border-t border-slate-200 dark:border-white/5 relative"
          >
            <div className="absolute top-0 left-1/2 -translate-x-1/2 w-200 h-100 bg-indigo-500/10 blur-[100px] rounded-full pointer-events-none" />

            <div className="max-w-6xl mx-auto px-6 relative z-10">
              <div className="text-center mb-16 md:mb-24">
                <h2 className="text-3xl md:text-5xl font-bold tracking-tight text-slate-900 dark:text-white mb-6">
                  Engineered for speed and security.
                </h2>
                <p className="text-lg text-slate-600 dark:text-slate-400 max-w-2xl mx-auto">
                  Cerberus provides everything you need to ship a robust,
                  advanced authentication system in minutes, not months.
                </p>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-6 auto-rows-[250px] md:auto-rows-[300px]">
                {/* Feature 1 (Spans 2 columns) */}
                <div className="md:col-span-2 group relative p-8 md:p-10 rounded-[2.5rem] border border-slate-200 dark:border-slate-800 bg-white dark:bg-[#0f0f0f] hover:bg-slate-50 dark:hover:bg-[#151515] hover:shadow-xl hover:-translate-y-1 transition-all duration-300 overflow-hidden">
                  <div className="absolute top-0 right-0 p-8 opacity-5">
                    <Layers className="w-48 h-48 md:w-64 md:h-64 group-hover:scale-110 transition-transform duration-700" />
                  </div>
                  <div className="relative z-10 h-full flex flex-col justify-between">
                    <div className="w-14 h-14 rounded-2xl bg-indigo-100 dark:bg-indigo-900/30 text-indigo-600 dark:text-indigo-400 flex items-center justify-center ring-4 ring-indigo-50 dark:ring-indigo-900/10 mb-6">
                      <Layers className="w-7 h-7" />
                    </div>
                    <div>
                      <h3 className="text-2xl font-bold text-slate-900 dark:text-white mb-3">
                        Multi-Project Architecture
                      </h3>
                      <p className="text-slate-600 dark:text-slate-400 leading-relaxed text-base max-w-lg">
                        Build B2B SaaS platforms effortlessly. Cerberus allows
                        you to isolate user pools into completely independent
                        Projects, each with their own isolated security policies
                        and origin controls.
                      </p>
                    </div>
                  </div>
                </div>

                {/* Feature 2 */}
                <div className="group relative p-8 md:p-10 rounded-[2.5rem] border border-slate-200 dark:border-slate-800 bg-white dark:bg-[#0f0f0f] hover:bg-slate-50 dark:hover:bg-[#151515] hover:shadow-xl hover:-translate-y-1 transition-all duration-300 overflow-hidden">
                  <div className="relative z-10 h-full flex flex-col justify-between">
                    <div className="w-14 h-14 rounded-2xl bg-rose-100 dark:bg-rose-900/30 text-rose-600 dark:text-rose-400 flex items-center justify-center ring-4 ring-rose-50 dark:ring-rose-900/10 mb-6">
                      <Zap className="w-7 h-7" />
                    </div>
                    <div>
                      <h3 className="text-xl font-bold text-slate-900 dark:text-white mb-3">
                        Edge-Optimized
                      </h3>
                      <p className="text-slate-600 dark:text-slate-400 leading-relaxed text-sm">
                        Tokens are signed with secure public/private key
                        cryptography, allowing instant verification at the edge
                        without database latency.
                      </p>
                    </div>
                  </div>
                </div>

                {/* Feature 3 */}
                <div className="group relative p-8 md:p-10 rounded-[2.5rem] border border-slate-200 dark:border-slate-800 bg-white dark:bg-[#0f0f0f] hover:bg-slate-50 dark:hover:bg-[#151515] hover:shadow-xl hover:-translate-y-1 transition-all duration-300 overflow-hidden">
                  <div className="relative z-10 h-full flex flex-col justify-between">
                    <div className="w-14 h-14 rounded-2xl bg-emerald-100 dark:bg-emerald-900/30 text-emerald-600 dark:text-emerald-400 flex items-center justify-center ring-4 ring-emerald-50 dark:ring-emerald-900/10 mb-6">
                      <Key className="w-7 h-7" />
                    </div>
                    <div>
                      <h3 className="text-xl font-bold text-slate-900 dark:text-white mb-3">
                        Native OAuth flows
                      </h3>
                      <p className="text-slate-600 dark:text-slate-400 leading-relaxed text-sm">
                        Easily add Google, GitHub, or Apple sign-ins. We handle
                        the OAuth handshakes, callbacks, and automatic account
                        merging for you.
                      </p>
                    </div>
                  </div>
                </div>

                {/* Feature 4 (Spans 2 columns) */}
                <div className="md:col-span-2 group relative p-8 md:p-10 rounded-[2.5rem] border border-slate-200 dark:border-slate-800 bg-white dark:bg-[#0f0f0f] hover:bg-slate-50 dark:hover:bg-[#151515] hover:shadow-xl hover:-translate-y-1 transition-all duration-300 overflow-hidden">
                  <div className="absolute top-0 right-0 p-8 opacity-5">
                    <Shield className="w-48 h-48 md:w-64 md:h-64 group-hover:scale-110 transition-transform duration-700" />
                  </div>
                  <div className="relative z-10 h-full flex flex-col justify-between">
                    <div className="w-14 h-14 rounded-2xl bg-blue-100 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400 flex items-center justify-center ring-4 ring-blue-50 dark:ring-blue-900/10 mb-6">
                      <Shield className="w-7 h-7" />
                    </div>
                    <div>
                      <h3 className="text-2xl font-bold text-slate-900 dark:text-white mb-3">
                        Ironclad Token Security
                      </h3>
                      <p className="text-slate-600 dark:text-slate-400 leading-relaxed text-base max-w-lg">
                        We natively enforce HttpOnly and secure cookies. Our
                        background rotators handle refresh tokens silently,
                        completely eliminating race conditions and token theft
                        risks.
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </section>

          {/* Footer CTA */}
          <section className="w-full relative pt-24 pb-32 border-t border-slate-200 dark:border-white/5 bg-slate-50 dark:bg-[#0a0a0a]">
            <div className="max-w-4xl mx-auto px-6 text-center relative z-10">
              <h2 className="text-4xl md:text-5xl lg:text-6xl font-extrabold tracking-tight text-slate-900 dark:text-white mb-8 leading-tight">
                Ready to{' '}
                <span className="text-transparent bg-clip-text bg-linear-to-r from-indigo-600 to-purple-600">
                  secure
                </span>{' '}
                your next big idea?
              </h2>
              <p className="text-xl text-slate-600 dark:text-slate-400 mb-12 max-w-2xl mx-auto">
                Join developers building the next generation of web applications
                with Cerberus Authentication.
              </p>
              <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
                {isLoading ? (
                  <div className="w-64 h-16 rounded-full bg-slate-200 dark:bg-slate-800 animate-pulse" />
                ) : user ? (
                  <Link
                    to="/dashboard"
                    className="group relative inline-flex items-center justify-center gap-2 px-10 py-4 text-lg font-semibold text-white bg-indigo-600 rounded-full hover:bg-indigo-700 transition-all shadow-lg active:scale-95"
                  >
                    <span>Go to Dashboard</span>
                    <ChevronRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
                  </Link>
                ) : (
                  <Link
                    to="/auth/register"
                    className="group relative inline-flex items-center justify-center gap-2 px-10 py-4 text-lg font-semibold text-white bg-indigo-600 rounded-full hover:bg-indigo-700 transition-all shadow-lg active:scale-95"
                  >
                    <span>Create your free account</span>
                    <ChevronRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
                  </Link>
                )}
              </div>
            </div>
          </section>
        </main>

        <footer className="w-full py-8 border-t border-slate-200 dark:border-slate-800 bg-white dark:bg-[#050505]">
          <div className="max-w-6xl mx-auto px-6 flex flex-col md:flex-row items-center justify-between gap-4">
            <div className="flex items-center gap-2">
              <img
                src="/logo.webp"
                alt="Cerberus"
                className="w-6 h-6 select-none opacity-80"
                draggable={false}
              />
              <span className="text-sm font-semibold text-slate-700 dark:text-slate-300">
                Cerberus
              </span>
            </div>
            <div className="text-sm text-slate-500 dark:text-slate-400 text-center md:text-right">
              &copy; {new Date().getFullYear()} Avneesh Mahajan. Proprietary
              Software. All rights reserved.
            </div>
          </div>
        </footer>
      </div>
    </div>
  )
}
