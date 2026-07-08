import { createFileRoute, Link } from '@tanstack/react-router'
import {
  Copy,
  CheckCircle2,
  Shield,
  Layers,
  LayoutTemplate,
  Workflow,
  Globe,
  Key,
  AlertTriangle,
} from 'lucide-react'
import { useState, useEffect } from 'react'
import { Highlight } from 'prism-react-renderer'
import { useTheme } from 'next-themes'
import { Button } from '#/components/ui/button'

const cerberusThemeDark = {
  plain: {
    color: '#e6edf3',
    backgroundColor: 'transparent',
  },
  styles: [
    {
      types: ['keyword', 'operator', 'modifier', 'control-flow'],
      style: { color: '#ff7b72' },
    },
    { types: ['string', 'inserted'], style: { color: '#a5d6ff' } },
    {
      types: ['class-name', 'maybe-class-name', 'builtin', 'type'],
      style: { color: '#d2a8ff' },
    },
    { types: ['function', 'method'], style: { color: '#d2a8ff' } },
    {
      types: ['property', 'variable', 'constant'],
      style: { color: '#79c0ff' },
    },
    {
      types: ['comment'],
      style: { color: '#8b949e', fontStyle: 'italic' as const },
    },
    { types: ['punctuation'], style: { color: '#e6edf3' } },
    { types: ['tag'], style: { color: '#7ee787' } },
    { types: ['attr-name'], style: { color: '#79c0ff' } },
  ],
}

const cerberusThemeLight = {
  plain: {
    color: '#334155',
    backgroundColor: 'transparent',
  },
  styles: [
    {
      types: ['keyword', 'operator', 'modifier', 'control-flow'],
      style: { color: '#9333ea' },
    },
    { types: ['string', 'inserted'], style: { color: '#16a34a' } },
    {
      types: ['class-name', 'maybe-class-name', 'builtin', 'type'],
      style: { color: '#ca8a04' },
    },
    { types: ['function', 'method'], style: { color: '#2563eb' } },
    {
      types: ['property', 'variable', 'constant'],
      style: { color: '#0284c7' },
    },
    {
      types: ['comment'],
      style: { color: '#64748b', fontStyle: 'italic' as const },
    },
    { types: ['punctuation'], style: { color: '#334155' } },
  ],
}

function CodeBlock({
  code,
  language = 'tsx',
  title,
}: {
  code: string
  language?: string
  title?: string
}) {
  const [copied, setCopied] = useState(false)
  const { resolvedTheme } = useTheme()
  const currentTheme =
    resolvedTheme === 'light' ? cerberusThemeLight : cerberusThemeDark

  const copyToClipboard = () => {
    navigator.clipboard.writeText(code)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  return (
    <div className="not-prose relative group rounded-2xl overflow-hidden border border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-[#1c1c1c] shadow-lg my-6">
      <div className="flex items-center justify-between px-4 py-3 bg-slate-100 dark:bg-[#262626] border-b border-slate-200 dark:border-slate-700/50">
        <div className="flex items-center gap-2">
          {title ? (
            <span className="text-xs font-mono font-medium text-slate-500 dark:text-slate-400">
              {title}
            </span>
          ) : (
            <div className="flex gap-2">
              <div className="w-3 h-3 rounded-full bg-red-400 dark:bg-red-500/80" />
              <div className="w-3 h-3 rounded-full bg-yellow-400 dark:bg-yellow-500/80" />
              <div className="w-3 h-3 rounded-full bg-green-400 dark:bg-green-500/80" />
            </div>
          )}
        </div>
        <Button
          onClick={copyToClipboard}
          variant="ghost"
          size="sm"
          className="h-7 px-2 text-xs flex items-center gap-1.5 text-slate-500 hover:text-slate-900 dark:text-slate-400 dark:hover:text-white transition-colors"
        >
          {copied ? (
            <>
              <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600 dark:text-emerald-500" />
              <span className="text-emerald-600 dark:text-emerald-500">
                Copied
              </span>
            </>
          ) : (
            <>
              <Copy className="w-3.5 h-3.5" />
              <span>Copy</span>
            </>
          )}
        </Button>
      </div>
      <div
        className="p-5 overflow-x-auto text-base font-medium leading-relaxed bg-slate-50 dark:bg-[#1c1c1c] text-slate-900 dark:text-slate-50 custom-scrollbar"
        style={{ fontFamily: '"Syne", monospace' }}
      >
        <Highlight theme={currentTheme} code={code.trim()} language={language}>
          {({ className, style, tokens, getLineProps, getTokenProps }) => (
            <pre
              className={className}
              style={{ ...style, backgroundColor: 'transparent' }}
            >
              {tokens.map((line, i) => (
                <div key={i} {...getLineProps({ line })} className="table-row">
                  <span className="table-cell text-right pr-4 text-slate-500 select-none opacity-50 text-xs translate-y-0.5">
                    {i + 1}
                  </span>
                  <span className="table-cell">
                    {line.map((token, key) => (
                      <span key={key} {...getTokenProps({ token })} />
                    ))}
                  </span>
                </div>
              ))}
            </pre>
          )}
        </Highlight>
      </div>
    </div>
  )
}

export const Route = createFileRoute('/docs/setup')({
  component: DocsSetupPage,
})

function DocsSetupPage() {
  const [activeSection, setActiveSection] = useState('getting-started')

  useEffect(() => {
    const scrollContainer = document.querySelector('.flex-1.overflow-y-auto')
    if (scrollContainer) {
      scrollContainer.scrollTop = 0
    }
  }, [])

  type SectionType = {
    id: string
    title: string
    subItems?: { id: string; title: string }[]
  }
  const sections: SectionType[] = [
    { id: 'dashboard-overview', title: 'Dashboard Overview' },
    { id: 'creating-project', title: 'Creating a Project' },
    { id: 'access-keys', title: 'Access Keys' },
    { id: 'origins-cors', title: 'Origins & CORS' },
    { id: 'identity-providers', title: 'Identity Providers' },
    { id: 'environments', title: 'Environments' },
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
      if (section.subItems) {
        section.subItems.forEach((subItem) => {
          const subEl = document.getElementById(subItem.id)
          if (subEl) observer.observe(subEl)
        })
      }
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
    <>
      <main className="flex-1 min-w-0 max-w-4xl font-outfit pb-[50vh]">
        <div className="prose prose-slate dark:prose-invert max-w-none">
          <h1 className="text-4xl md:text-5xl font-extrabold tracking-tight text-slate-900 dark:text-white mb-6 leading-tight">
            Project Setup
          </h1>
          <p className="text-lg text-slate-600 dark:text-slate-400 mb-8 leading-relaxed">
            Before using the Cerberus SDK, you need to configure your project in
            the Dashboard. This guide walks you through the essential steps:
            understanding the dashboard, creating your first project, setting up
            your preferred identity providers, configuring security origins, and
            retrieving the API keys you'll need for your codebase.
          </p>

          <section id="dashboard-overview" className="scroll-mt-8 mb-16">
            <h2 className="text-3xl font-bold tracking-tight mb-4 flex items-center gap-2 border-b border-slate-200 dark:border-slate-800 pb-2">
              <LayoutTemplate className="w-8 h-8 text-blue-500" />
              Dashboard Overview
            </h2>
            <p className="text-base text-slate-600 dark:text-slate-400 mb-6">
              The Cerberus Dashboard is your centralized control panel for
              managing authentication settings, viewing logs, and monitoring
              active sessions across your projects.
            </p>

            <div className="space-y-4 mb-8">
              <h3 className="text-xl font-semibold text-slate-900 dark:text-white">
                Navigating the Dashboard
              </h3>
              <ul className="list-disc pl-6 space-y-3 text-slate-700 dark:text-slate-300">
                <li>
                  <strong>Dashboard:</strong> After logging in, you will land on
                  the dashboard. This lists all the projects (applications) that
                  you manage.
                </li>
                <li>
                  <strong>Project Dashboard:</strong> Clicking on a specific
                  project card opens its dedicated dashboard. Here, you
                  configure all settings specific to that application.
                </li>
                <li>
                  <strong>Sidebar Navigation:</strong> While inside a project,
                  use the left sidebar to navigate between different
                  configuration sections: General Settings, Identity Providers,
                  Origins & CORS, and Access Keys.
                </li>
              </ul>
            </div>

            <div className="bg-slate-50 dark:bg-slate-900/50 border border-slate-200 dark:border-slate-800 rounded-2xl p-6">
              <p className="text-slate-700 dark:text-slate-300">
                To get started, you must first{' '}
                <Link
                  to="/auth/login"
                  className="text-blue-600 dark:text-blue-400 hover:underline font-semibold"
                >
                  Log In
                </Link>{' '}
                or{' '}
                <Link
                  to="/auth/register"
                  className="text-blue-600 dark:text-blue-400 hover:underline font-semibold"
                >
                  Register
                </Link>
                .
              </p>
            </div>
          </section>

          <section id="creating-project" className="scroll-mt-8 mb-16">
            <h2 className="text-3xl font-bold tracking-tight mb-4 flex items-center gap-2 border-b border-slate-200 dark:border-slate-800 pb-2">
              <Layers className="w-8 h-8 text-indigo-500" />
              Creating a Project
            </h2>
            <p className="mb-4 text-slate-600 dark:text-slate-400">
              A <strong>Project</strong> represents your application, startup,
              or organization within Cerberus.
            </p>
            <ol className="list-decimal pl-6 space-y-3 mb-6 text-slate-700 dark:text-slate-300">
              <li>
                Log in and navigate to your{' '}
                <Link
                  to="/dashboard"
                  className="text-blue-600 dark:text-blue-400 hover:underline font-semibold"
                >
                  Dashboard
                </Link>
                .
              </li>
              <li>
                Click the <strong>Create Project</strong> button.
              </li>
              <li>
                Provide a unique, descriptive <strong>Project Name</strong> for
                your application and click create.
              </li>
            </ol>
            <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-xl p-4 flex gap-3">
              <CheckCircle2 className="w-6 h-6 text-blue-600 dark:text-blue-400 shrink-0" />
              <p className="text-sm text-blue-800 dark:text-blue-300 m-0">
                You can manage multiple isolated projects under a single
                Cerberus instance. Each project has its own isolated users,
                sessions, and security configurations!
              </p>
            </div>
          </section>

          <section id="access-keys" className="scroll-mt-8 mb-16">
            <h2 className="text-3xl font-bold tracking-tight mb-4 flex items-center gap-2 border-b border-slate-200 dark:border-slate-800 pb-2">
              <Key className="w-8 h-8 text-amber-500" />
              Access Keys
            </h2>
            <p className="mb-4 text-slate-600 dark:text-slate-400">
              To initialize the Cerberus SDK in your frontend application, you
              need your unique project credentials.
            </p>

            <div className="bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800 rounded-xl p-4 mb-6">
              <p className="text-sm text-amber-800 dark:text-amber-300 m-0 font-medium flex items-start gap-2">
                <AlertTriangle className="w-5 h-5 shrink-0 mt-0.5" />
                <span>
                  <strong>Important:</strong> Your API Key is only displayed{' '}
                  <strong>once</strong> immediately after you create a project.
                  For security reasons, it is never shown again in the
                  dashboard.
                </span>
              </p>
            </div>

            <ol className="list-decimal pl-6 space-y-3 mb-6 text-slate-700 dark:text-slate-300">
              <li>
                When you create a project, the success modal will display your{' '}
                <strong>API Key</strong>. You can securely copy it to your
                clipboard or use the <strong>Download JSON</strong> option to
                save your credentials. This is the only key you need to
                initialize the frontend SDK.
              </li>
              <li>
                If you lose your API key, you can generate a new one by going to
                the <strong>Access Keys & Secrets</strong> tab in your project
                settings and clicking <strong>Roll API Key</strong>.
              </li>
              <li>
                You will also see a <strong>JWT Public Key</strong> in the
                settings. This is NOT needed for the frontend SDK; it is used
                securely by your own project's backend to verify and update the
                JWT tokens issued by Cerberus.
              </li>
            </ol>
            <p className="mb-4 text-slate-600 dark:text-slate-400">
              Copy your API Key into your frontend environment variables (e.g.,{' '}
              <code>.env.local</code>):
            </p>
            <CodeBlock
              language="bash"
              code={'VITE_CERBERUS_API_KEY="your_api_key_here"'}
            />
          </section>

          <section id="origins-cors" className="scroll-mt-8 mb-16">
            <h2 className="text-3xl font-bold tracking-tight mb-4 flex items-center gap-2 border-b border-slate-200 dark:border-slate-800 pb-2">
              <Globe className="w-8 h-8 text-emerald-500" />
              Origins & CORS
            </h2>
            <p className="mb-4 text-slate-600 dark:text-slate-400">
              This section configures how your frontend application communicates
              securely with Cerberus.
            </p>

            <h3 className="text-2xl font-semibold mt-8 mb-3 scroll-mt-8">
              1. Frontend App URL
            </h3>
            <p className="mb-4 text-slate-600 dark:text-slate-400">
              You must set your primary <strong>Frontend App URL</strong> (e.g.,{' '}
              <code>http://localhost:3000</code>). Cerberus uses this exact URL
              to seamlessly redirect your users back to your application after
              they successfully authenticate via OAuth providers (like Google or
              GitHub).
            </p>

            <h3 className="text-2xl font-semibold mt-8 mb-3 scroll-mt-8">
              2. Allowed CORS Origins
            </h3>
            <p className="mb-4 text-slate-600 dark:text-slate-400">
              For security reasons, Cerberus will <strong>only</strong> accept
              authentication requests from explicitly allowed origins (domains).
              This prevents Cross-Site Request Forgery (CSRF).
            </p>
            <ol className="list-decimal pl-6 space-y-3 mb-6 text-slate-700 dark:text-slate-300">
              <li>
                Go to the <strong>Origins & CORS</strong> tab in your Settings.
              </li>
              <li>
                Add the URL of your frontend application to the{' '}
                <strong>Allowed CORS Origins</strong> list (you can add up to 5
                origins).
              </li>
              <li>Ensure you do not include trailing slashes.</li>
            </ol>
            <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-xl p-4">
              <p className="text-sm text-red-800 dark:text-red-300 m-0 font-medium">
                Important: If your origin is not added to this list, all API
                requests from your frontend SDK will be instantly blocked by the
                browser's CORS policy.
              </p>
            </div>
          </section>

          <section id="identity-providers" className="scroll-mt-8 mb-16">
            <h2 className="text-3xl font-bold tracking-tight mb-4 flex items-center gap-2 border-b border-slate-200 dark:border-slate-800 pb-2">
              <Shield className="w-8 h-8 text-purple-500" />
              Identity Providers
            </h2>
            <p className="mb-4 text-slate-600 dark:text-slate-400">
              Cerberus supports multiple authentication methods out of the box.
              You must explicitly enable and configure the providers you wish to
              use for your frontend application.
            </p>
            <ul className="list-disc pl-6 space-y-4 mb-6 text-slate-700 dark:text-slate-300">
              <li>
                <strong>Local Authentication:</strong> Email and password-based
                login. Securely hashes passwords using Argon2id.
              </li>
              <li>
                <strong>OAuth Providers (Google, GitHub):</strong> To enable
                OAuth, you need to provide your OAuth application's Client ID
                and Client Secret in the settings.{' '}
                <em>
                  Note: Currently, only Google and GitHub are supported for
                  OAuth.
                </em>
                <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-xl p-4 mt-3">
                  <p className="text-sm text-blue-800 dark:text-blue-300 m-0 mb-3">
                    <strong>Note:</strong> Ensure you configure the callback URL
                    in your provider (e.g., Google Cloud Console) to point to
                    your Cerberus instance. Replace{' '}
                    <code>&#123;provider&#125;</code> with the name of the
                    identity provider (e.g., <code>google</code> or{' '}
                    <code>github</code>).
                  </p>
                  <div className="-mx-2 -mb-2">
                    <CodeBlock
                      code="https://cerberus-api.aymahajan.in/auth/callback/{provider}"
                      language="text"
                    />
                  </div>

                  <div className="mt-4 pt-4 border-t border-blue-200/50 dark:border-blue-800/50 text-sm text-blue-800 dark:text-blue-300">
                    <p className="mb-2 font-medium">Examples:</p>
                    <ul className="list-disc pl-5 space-y-1">
                      <li>
                        <strong>Google:</strong>{' '}
                        <code>
                          https://cerberus-api.aymahajan.in/auth/callback/google
                        </code>
                      </li>
                      <li>
                        <strong>GitHub:</strong>{' '}
                        <code>
                          https://cerberus-api.aymahajan.in/auth/callback/github
                        </code>
                      </li>
                    </ul>
                  </div>
                </div>
              </li>
            </ul>
            <p className="text-slate-700 dark:text-slate-300">
              Navigate to your specific Project settings or global settings to
              toggle these on and off.
            </p>

            <p className="mt-12 text-base text-slate-700 dark:text-slate-300 font-medium text-center bg-slate-50 dark:bg-slate-900/50 p-6 rounded-2xl border border-slate-200 dark:border-slate-800">
              All set up! You are now ready to proceed to the{' '}
              <Link
                to="/docs/sdk"
                className="text-blue-600 dark:text-blue-400 hover:underline"
              >
                SDK Reference
              </Link>{' '}
              to implement authentication in your code.
            </p>
          </section>

          <section id="environments" className="scroll-mt-8 mb-16">
            <h2 className="text-3xl font-bold tracking-tight mb-4 flex items-center gap-2 border-b border-slate-200 dark:border-slate-800 pb-2">
              <Workflow className="w-8 h-8 text-cyan-500" />
              Environments
            </h2>
            <p className="mb-4 text-slate-600 dark:text-slate-400">
              When you are ready to launch, you can toggle your project between{' '}
              <strong>Development</strong> and <strong>Production</strong>{' '}
              environments in the <strong>General Settings</strong> tab.
            </p>
            <ul className="list-disc pl-6 space-y-3 mb-6 text-slate-700 dark:text-slate-300">
              <li>
                <strong>Development (Default):</strong> Optimized for local
                building. Relaxed security policies and higher tolerance for
                cross-site cookie settings to make localhost testing seamless.
              </li>
              <li>
                <strong>Production:</strong> Enforces strict security policies,
                secure HttpOnly cookie settings, and tighter rate limits to
                protect your live application.
              </li>
            </ul>
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
                    activeSection === section.id ||
                    (section.subItems &&
                      section.subItems.some((sub) => activeSection === sub.id))
                      ? 'text-blue-600 dark:text-blue-400 font-medium'
                      : 'text-slate-600 dark:text-slate-300 hover:text-slate-900 dark:hover:text-white'
                  }`}
                >
                  {section.title}
                </button>
                {section.subItems && (
                  <div className="flex flex-col gap-1 pl-3 border-l-2 border-slate-200 dark:border-slate-800 ml-1">
                    {section.subItems.map((subItem) => (
                      <button
                        key={subItem.id}
                        onClick={() => scrollToSection(subItem.id)}
                        className={`text-left text-xs transition-colors ${
                          activeSection === subItem.id
                            ? 'text-blue-600 dark:text-blue-400 font-medium'
                            : 'text-slate-500 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'
                        }`}
                      >
                        {subItem.title}
                      </button>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      </aside>
    </>
  )
}
