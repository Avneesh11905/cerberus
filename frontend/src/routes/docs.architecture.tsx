import { createFileRoute } from '@tanstack/react-router'
import { Shield, Lock, Layers, RefreshCcw } from 'lucide-react'
import { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '#/components/ui/card'

export const Route = createFileRoute('/docs/architecture')({
  component: ArchitectureDocs,
})

function ArchitectureDocs() {
  const [activeSection, setActiveSection] = useState('dual-token')

  useEffect(() => {
    const scrollContainer = document.querySelector('.flex-1.overflow-y-auto')
    if (scrollContainer) {
      scrollContainer.scrollTop = 0
    }
  }, [])

  const sections = [
    { id: 'dual-token', title: 'Dual-Token Strategy' },
    { id: 'silent-refresh', title: 'Silent Refresh & CSRF' },
    { id: 'isolation', title: 'Multi-Project Isolation' },
  ]

  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            setActiveSection(entry.target.id)
          }
        })
      },
      { rootMargin: '-15% 0px -60% 0px' },
    )

    sections.forEach((section) => {
      const el = document.getElementById(section.id)
      if (el) observer.observe(el)
    })

    return () => observer.disconnect()
  }, [])

  const scrollToSection = (id: string) => {
    setActiveSection(id)
    document
      .getElementById(id)
      ?.scrollIntoView({ behavior: 'smooth', block: 'start' })
  }

  return (
    <div className="flex gap-12 relative min-h-max w-full">
      <main className="flex-1 min-w-0 max-w-4xl pt-4 pb-20">
        {/* Header */}
        <div className="mb-12">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-100 dark:bg-indigo-900/30 text-indigo-700 dark:text-indigo-300 text-sm font-medium mb-4">
            <Shield className="w-4 h-4" />
            <span>Architecture & Security</span>
          </div>
          <h1 className="text-4xl sm:text-5xl font-bold tracking-tight text-slate-900 dark:text-white mb-6">
            Security by Design
          </h1>
          <p className="text-xl text-slate-600 dark:text-slate-400 max-w-2xl">
            Learn how Cerberus implements robust security models, dual-token
            strategies, and strict multi-project isolation to keep your users
            secure.
          </p>
        </div>

        <div className="prose prose-slate dark:prose-invert max-w-none prose-headings:scroll-mt-24 prose-h2:text-3xl prose-h3:text-2xl">
          {/* Dual-Token Strategy */}
          <section id="dual-token" className="scroll-mt-8 mb-16">
            <h2 className="text-3xl font-bold tracking-tight mb-4 flex items-center gap-2 border-b border-slate-200 dark:border-slate-800 pb-2">
              <Lock className="w-8 h-8 text-blue-500" />
              Dual-Token Strategy
            </h2>
            <p className="text-slate-600 dark:text-slate-400 text-lg mb-6">
              Cerberus secures sessions using a dual-token architecture designed
              to eliminate XSS token theft vulnerability while maintaining high
              API performance.
            </p>

            <div className="grid sm:grid-cols-2 gap-6 my-8">
              <Card>
                <CardHeader>
                  <CardTitle>Access Tokens (JWT)</CardTitle>
                </CardHeader>
                <CardContent>
                  <ul className="space-y-2 text-slate-600 dark:text-slate-400">
                    <li className="flex gap-2">
                      <div className="w-1.5 h-1.5 rounded-full bg-blue-500 mt-2 shrink-0" />{' '}
                      Short-lived (15 minutes).
                    </li>
                    <li className="flex gap-2">
                      <div className="w-1.5 h-1.5 rounded-full bg-blue-500 mt-2 shrink-0" />{' '}
                      Stateless and cryptographically signed.
                    </li>
                    <li className="flex gap-2">
                      <div className="w-1.5 h-1.5 rounded-full bg-blue-500 mt-2 shrink-0" />{' '}
                      Returned in the JSON body.
                    </li>
                    <li className="flex gap-2">
                      <div className="w-1.5 h-1.5 rounded-full bg-blue-500 mt-2 shrink-0" />{' '}
                      Stored <strong>strictly in memory</strong> by the SDK,
                      never in localStorage.
                    </li>
                  </ul>
                </CardContent>
              </Card>
              <Card>
                <CardHeader>
                  <CardTitle>Refresh Tokens</CardTitle>
                </CardHeader>
                <CardContent>
                  <ul className="space-y-2 text-slate-600 dark:text-slate-400">
                    <li className="flex gap-2">
                      <div className="w-1.5 h-1.5 rounded-full bg-emerald-500 mt-2 shrink-0" />{' '}
                      Long-lived (7 days by default).
                    </li>
                    <li className="flex gap-2">
                      <div className="w-1.5 h-1.5 rounded-full bg-emerald-500 mt-2 shrink-0" />{' '}
                      Stateful and revocable in the database.
                    </li>
                    <li className="flex gap-2">
                      <div className="w-1.5 h-1.5 rounded-full bg-emerald-500 mt-2 shrink-0" />{' '}
                      Stored in an <code>HttpOnly, Secure, SameSite=Lax</code>{' '}
                      cookie.
                    </li>
                    <li className="flex gap-2">
                      <div className="w-1.5 h-1.5 rounded-full bg-emerald-500 mt-2 shrink-0" />{' '}
                      Cannot be accessed or stolen via JavaScript (XSS immune).
                    </li>
                  </ul>
                </CardContent>
              </Card>
            </div>
          </section>

          {/* Silent Refresh & CSRF */}
          <section id="silent-refresh" className="scroll-mt-8 mb-16">
            <h2 className="text-3xl font-bold tracking-tight mb-4 flex items-center gap-2 border-b border-slate-200 dark:border-slate-800 pb-2">
              <RefreshCcw className="w-8 h-8 text-emerald-500" />
              Silent Refresh & CSRF
            </h2>

            <Card className="mb-8">
              <CardHeader>
                <CardTitle>The Refresh Pipeline</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-slate-600 dark:text-slate-400 mb-4">
                  When an Access Token expires, API requests will return a{' '}
                  <code>401 Unauthorized</code> error. The{' '}
                  <code>@cerberus/sdk</code> handles this entirely behind the
                  scenes:
                </p>
                <ol className="list-decimal list-inside space-y-2 text-slate-600 dark:text-slate-400 ml-4">
                  <li>
                    The SDK intercepts the <code>401</code> response before your
                    app sees it.
                  </li>
                  <li>
                    It places all concurrent API requests into a holding queue.
                  </li>
                  <li>
                    It calls <code>POST /auth/refresh</code>, which
                    automatically attaches the <code>HttpOnly</code> refresh
                    cookie.
                  </li>
                  <li>
                    The backend validates the cookie and issues a new Access
                    Token.
                  </li>
                  <li>
                    The SDK stores the new Access Token in memory and
                    transparently retries the queued requests.
                  </li>
                </ol>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>CSRF Protection</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-slate-600 dark:text-slate-400 mb-4">
                  Because Refresh Tokens are sent automatically via cookies,
                  Cerberus implements strict Cross-Site Request Forgery (CSRF)
                  protection.
                </p>
                <p className="text-slate-600 dark:text-slate-400 mb-4">
                  When the SDK hits the refresh endpoint, the backend rotates a
                  unique, cryptographic CSRF token and passes it back in the
                  JSON body. The SDK caches this token and attaches it as an{' '}
                  <code>X-CSRF</code> header to all subsequent state-changing
                  requests (POST, PUT, PATCH, DELETE).
                </p>
                <p className="text-slate-600 dark:text-slate-400">
                  This guarantees that even if a malicious site tricks the
                  user's browser into sending a request with the{' '}
                  <code>HttpOnly</code> cookie, it will be rejected because the
                  malicious site cannot read the <code>X-CSRF</code> token to
                  include it in the header.
                </p>
              </CardContent>
            </Card>
          </section>

          {/* Multi-Project Isolation */}
          <section id="isolation" className="scroll-mt-8 mb-16">
            <h2 className="text-3xl font-bold tracking-tight mb-4 flex items-center gap-2 border-b border-slate-200 dark:border-slate-800 pb-2">
              <Layers className="w-8 h-8 text-indigo-500" />
              Multi-Project Isolation
            </h2>
            <p className="text-slate-600 dark:text-slate-400 text-lg mb-6">
              Cerberus is built from the ground up for strict multi-project
              isolation. Every user, session, configuration, and OAuth provider
              is bound strictly to a Project namespace.
            </p>

            <div className="grid md:grid-cols-2 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle>Project API Keys</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-slate-600 dark:text-slate-400">
                    Your frontend simply sets the{' '}
                    <code>X-Cerberus-API-Key</code> header (handled
                    automatically by the SDK). The backend dynamically binds the
                    database session to that specific project namespace for the
                    duration of the request.
                  </p>
                </CardContent>
              </Card>
              <Card>
                <CardHeader>
                  <CardTitle>CORS & Allowed Origins</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-slate-600 dark:text-slate-400">
                    Because Cerberus issues cross-origin cookies, it enforces a
                    strict CORS policy per-project. Your frontend URL must be
                    explicitly whitelisted in the dashboard, or the browser will
                    reject the authentication cookies.
                  </p>
                </CardContent>
              </Card>
            </div>
          </section>
        </div>
      </main>

      {/* Right Sidebar (Indexes) */}
      <aside className="hidden xl:block w-56 shrink-0 self-start sticky top-12 pl-6 border-l border-slate-200 dark:border-slate-800/50 max-h-[calc(100vh-6rem)] overflow-y-auto pb-8 scrollbar-none [-ms-overflow-style:none] [&::-webkit-scrollbar]:hidden">
        <div className="mb-8">
          <h4 className="text-xs font-semibold text-slate-900 dark:text-white uppercase tracking-wider mb-4">
            On this page
          </h4>
          <div className="flex flex-col gap-2">
            {sections.map((section) => (
              <div key={section.id} className="flex flex-col gap-1 w-full">
                <button
                  onClick={() => scrollToSection(section.id)}
                  className={`text-left text-sm transition-colors ${
                    activeSection === section.id
                      ? 'text-blue-600 dark:text-blue-400 font-medium'
                      : 'text-slate-600 dark:text-slate-300 hover:text-slate-900 dark:hover:text-white'
                  }`}
                >
                  {section.title}
                </button>
              </div>
            ))}
          </div>
        </div>
      </aside>
    </div>
  )
}
