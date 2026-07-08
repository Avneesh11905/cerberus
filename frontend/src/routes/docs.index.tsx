import { createFileRoute, Link } from '@tanstack/react-router'
import { Terminal, ShieldAlert, ShieldCheck, Zap, Lock, Fingerprint, LayoutDashboard, Code, Sparkles } from 'lucide-react'
import { useEffect } from 'react'
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '#/components/ui/card'

export const Route = createFileRoute('/docs/')({
  component: DocsIndex,
})

function DocsIndex() {
  useEffect(() => {
    const scrollContainer = document.querySelector('.flex-1.overflow-y-auto')
    if (scrollContainer) {
      scrollContainer.scrollTop = 0
    }
  }, [])

  return (
    <main className="flex-1 max-w-4xl min-w-0 font-outfit pb-24">
      <div className="max-w-none">
        
        {/* Header Section */}
        <div className="mb-12">
          <h1 className="text-4xl md:text-5xl font-extrabold tracking-tight text-slate-900 dark:text-white mb-6 leading-tight">
            Stop building auth from <span className="text-transparent bg-clip-text bg-linear-to-r from-blue-600 to-indigo-500">scratch.</span>
          </h1>
          <p className="text-lg text-slate-600 dark:text-slate-400 leading-relaxed max-w-3xl">
            Building authentication involves managing secure cookies, CORS policies, token rotation, database sessions, and OAuth. With Cerberus, our powerful backend handles the complex security, allowing you to authenticate users with just a few lines of code.
          </p>
        </div>

        {/* Feature Grid */}
        <div className="mb-16">
          <h2 className="text-2xl font-bold tracking-tight text-slate-900 dark:text-white mb-6">Why use Cerberus?</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-0 overflow-hidden rounded-3xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-[#0a0a0a] shadow-sm">
            
            {/* The Old Way */}
            <div className="p-8 sm:p-10 bg-slate-50 dark:bg-slate-900/20 border-b md:border-b-0 md:border-r border-slate-200 dark:border-slate-800">
              <h3 className="text-xl font-bold text-slate-900 dark:text-white mb-8 flex items-center gap-3">
                <ShieldAlert className="w-6 h-6 text-red-500" />
                The Old Way
              </h3>
              
              <ul className="space-y-6 text-base text-slate-600 dark:text-slate-400">
                <li className="flex gap-4">
                  <div className="w-1.5 h-1.5 rounded-full bg-red-400 mt-2 shrink-0" />
                  <p>Manually configuring strict CORS, HttpOnly, Secure, and SameSite cookie policies.</p>
                </li>
                <li className="flex gap-4">
                  <div className="w-1.5 h-1.5 rounded-full bg-red-400 mt-2 shrink-0" />
                  <p>Implementing refresh token rotation securely without race conditions.</p>
                </li>
                <li className="flex gap-4">
                  <div className="w-1.5 h-1.5 rounded-full bg-red-400 mt-2 shrink-0" />
                  <p>Building complex database structures to track active sessions, IPs, and devices.</p>
                </li>
                <li className="flex gap-4">
                  <div className="w-1.5 h-1.5 rounded-full bg-red-400 mt-2 shrink-0" />
                  <p>Handling OAuth redirects, exchanging codes, and merging duplicate accounts.</p>
                </li>
              </ul>
            </div>

            {/* The Cerberus Way */}
            <div className="p-8 sm:p-10 bg-blue-50/30 dark:bg-blue-900/10">
              <h3 className="text-xl font-bold text-slate-900 dark:text-white mb-8 flex items-center gap-3">
                <ShieldCheck className="w-6 h-6 text-blue-500" />
                The Cerberus Way
              </h3>
              
              <ul className="space-y-6 text-base text-slate-700 dark:text-slate-300">
                <li className="flex gap-4">
                  <div className="w-1.5 h-1.5 rounded-full bg-blue-500 mt-2 shrink-0" />
                  <p><strong>Natively secure cookies</strong> and strict CORS across all your origins automatically.</p>
                </li>
                <li className="flex gap-4">
                  <div className="w-1.5 h-1.5 rounded-full bg-blue-500 mt-2 shrink-0" />
                  <p><strong>Silent interceptors</strong> that automatically refresh tokens and retry failed requests.</p>
                </li>
                <li className="flex gap-4">
                  <div className="w-1.5 h-1.5 rounded-full bg-blue-500 mt-2 shrink-0" />
                  <p><strong>Real-time session tracking</strong> with instant global revocation capabilities.</p>
                </li>
                <li className="flex gap-4">
                  <div className="w-1.5 h-1.5 rounded-full bg-blue-500 mt-2 shrink-0" />
                  <p><strong>Native OAuth flows</strong> where the SDK handles all redirects and callbacks for you.</p>
                </li>
              </ul>
            </div>
            
          </div>
        </div>

        {/* Features Section */}
        <div className="mt-20 mb-12">
          <div className="text-center mb-10">
            <h2 className="text-2xl font-bold tracking-tight text-slate-900 dark:text-white mb-3">Everything you need to ship fast</h2>
            <p className="text-base text-slate-600 dark:text-slate-400">Powerful features packed into a developer-friendly API.</p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
            <Card className="bg-slate-50 dark:bg-[#111] border-slate-200 dark:border-slate-800 rounded-2xl hover:bg-slate-100 dark:hover:bg-[#151515] transition-colors py-1 gap-2 shadow-none">
              <CardHeader className="px-5 pb-0 items-start">
                <Zap className="w-6 h-6 text-yellow-500 mb-1" />
                <CardTitle className="text-base text-slate-900 dark:text-white">Lightning Fast Setup</CardTitle>
              </CardHeader>
              <CardContent className="px-5 pt-0">
                <CardDescription className="text-slate-600 dark:text-slate-400">Drop in the SDK, configure your Dashboard, and have secure auth running in under 5 minutes.</CardDescription>
              </CardContent>
            </Card>
            
            <Card className="bg-slate-50 dark:bg-[#111] border-slate-200 dark:border-slate-800 rounded-2xl hover:bg-slate-100 dark:hover:bg-[#151515] transition-colors py-1 gap-2 shadow-none">
              <CardHeader className="px-5 pb-0 items-start">
                <Lock className="w-6 h-6 text-emerald-500 mb-1" />
                <CardTitle className="text-base text-slate-900 dark:text-white">Ironclad Security</CardTitle>
              </CardHeader>
              <CardContent className="px-5 pt-0">
                <CardDescription className="text-slate-600 dark:text-slate-400">Strict CORS policies, HttpOnly secure cookies, and automated token rotation keep your users safe.</CardDescription>
              </CardContent>
            </Card>

            <Card className="bg-slate-50 dark:bg-[#111] border-slate-200 dark:border-slate-800 rounded-2xl hover:bg-slate-100 dark:hover:bg-[#151515] transition-colors py-1 gap-2 shadow-none">
              <CardHeader className="px-5 pb-0 items-start">
                <Fingerprint className="w-6 h-6 text-indigo-500 mb-1" />
                <CardTitle className="text-base text-slate-900 dark:text-white">Passwordless / OAuth</CardTitle>
              </CardHeader>
              <CardContent className="px-5 pt-0">
                <CardDescription className="text-slate-600 dark:text-slate-400">Support for traditional Email/Password as well as seamless Google and GitHub OAuth logins.</CardDescription>
              </CardContent>
            </Card>

            <Card className="bg-slate-50 dark:bg-[#111] border-slate-200 dark:border-slate-800 rounded-2xl hover:bg-slate-100 dark:hover:bg-[#151515] transition-colors py-1 gap-2 shadow-none">
              <CardHeader className="px-5 pb-0 items-start">
                <LayoutDashboard className="w-6 h-6 text-blue-500 mb-1" />
                <CardTitle className="text-base text-slate-900 dark:text-white">Powerful Dashboard</CardTitle>
              </CardHeader>
              <CardContent className="px-5 pt-0">
                <CardDescription className="text-slate-600 dark:text-slate-400">A beautiful, centralized control panel to manage all your projects, origins, and identity providers.</CardDescription>
              </CardContent>
            </Card>

            <Card className="bg-slate-50 dark:bg-[#111] border-slate-200 dark:border-slate-800 rounded-2xl hover:bg-slate-100 dark:hover:bg-[#151515] transition-colors py-1 gap-2 shadow-none">
              <CardHeader className="px-5 pb-0 items-start">
                <Code className="w-6 h-6 text-rose-500 mb-1" />
                <CardTitle className="text-base text-slate-900 dark:text-white">Fully Typed SDK</CardTitle>
              </CardHeader>
              <CardContent className="px-5 pt-0">
                <CardDescription className="text-slate-600 dark:text-slate-400">A completely type-safe TypeScript SDK that provides incredible autocomplete and developer experience.</CardDescription>
              </CardContent>
            </Card>

            <Card className="bg-slate-50 dark:bg-[#111] border-slate-200 dark:border-slate-800 rounded-2xl hover:bg-slate-100 dark:hover:bg-[#151515] transition-colors py-1 gap-2 shadow-none">
              <CardHeader className="px-5 pb-0 items-start">
                <Sparkles className="w-6 h-6 text-amber-500 mb-1" />
                <CardTitle className="text-base text-slate-900 dark:text-white">Modern Architecture</CardTitle>
              </CardHeader>
              <CardContent className="px-5 pt-0">
                <CardDescription className="text-slate-600 dark:text-slate-400">Built on a highly scalable, multi-project backend architecture designed to grow with your application.</CardDescription>
              </CardContent>
            </Card>
          </div>
        </div>

        {/* CTA Section */}
        <div className="mt-16 text-center">
          <h2 className="text-3xl font-bold text-slate-900 dark:text-white mb-6">Ready to integrate?</h2>
          <Link 
            to="/docs/sdk"
            className="inline-flex items-center gap-3 px-8 py-4 bg-indigo-600 text-white rounded-2xl font-semibold hover:bg-indigo-700 hover:-translate-y-1 hover:shadow-xl hover:shadow-indigo-500/20 transition-all duration-300 text-lg"
          >
            Explore the SDK Documentation
            <Terminal className="w-5 h-5" />
          </Link>
        </div>
        
      </div>
    </main>
  )
}
