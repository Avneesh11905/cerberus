import { createFileRoute } from '@tanstack/react-router'
import { Workflow, Code2 } from 'lucide-react'
import { CodeBlock } from '#/components/CodeBlock'
import { ApiRef } from '#/components/ApiRef'
import { useEffect, useState } from 'react'

export const Route = createFileRoute('/docs/sdk/reference')({
  component: DocsSdkReference,
})

function DocsSdkReference() {
  const [activeSection, setActiveSection] = useState('interceptor')

  useEffect(() => {
    const scrollContainer = document.querySelector('.flex-1.overflow-y-auto')
    if (scrollContainer) scrollContainer.scrollTop = 0
  }, [])

  const sections = [
    {
      id: 'interceptor',
      title: 'Token Refresh Pipeline',
      subItems: [
        { id: 'interceptor-axios', title: 'Axios Interceptors' },
        { id: 'interceptor-manual', title: 'Manual Retrieval' },
        { id: 'interceptor-react', title: 'Reacting to Changes' },
      ],
    },
    {
      id: 'schemas',
      title: 'Type Schemas',
      subItems: [
        { id: 'schema-user', title: 'User' },
        { id: 'schema-session', title: 'Session' },
        { id: 'schema-responses', title: 'Message Responses' },
      ],
    },
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
      section.subItems.forEach((subItem) => {
        const subEl = document.getElementById(subItem.id)
        if (subEl) observer.observe(subEl)
      })
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
          <div className="mb-12">
            <h1 className="text-4xl md:text-5xl font-extrabold tracking-tight mb-6 flex items-center gap-4">
              <Workflow className="w-10 h-10 text-blue-500" />
              Advanced Reference
            </h1>
            <p className="text-lg text-slate-600 dark:text-slate-400 leading-relaxed">
              In-depth details on the internal token refresh pipeline, custom
              integrations, and TypeScript schemas.
            </p>
          </div>

          <section id="interceptor" className="scroll-mt-8 mb-16">
            <h2 className="text-3xl font-bold tracking-tight mb-4 flex items-center gap-2 border-b border-slate-200 dark:border-slate-800 pb-2">
              Token Refresh Pipeline
            </h2>
            <p className="text-base text-slate-600 dark:text-slate-400 mb-4">
              Handling short-lived Access Tokens manually can lead to complex
              race conditions. The <code>CerberusClient</code> comes built-in
              with an advanced Axios interceptor queue:
            </p>

            <div className="mt-8 grid grid-cols-1 lg:grid-cols-2 gap-4">
              {[
                {
                  title: 'Initial Request',
                  desc: 'A request is sent using the in-memory Access Token.',
                },
                {
                  title: 'Token Expiry',
                  desc: (
                    <>
                      If it fails with a{' '}
                      <code className="text-xs bg-slate-100 dark:bg-slate-800 px-1 py-0.5 rounded text-red-600 dark:text-red-400">
                        401 Unauthorized
                      </code>{' '}
                      (token expired), the SDK catches the error.
                    </>
                  ),
                },
                {
                  title: 'Queue Requests',
                  desc: (
                    <>
                      It <strong>pauses</strong> all other incoming API requests
                      in a queue to prevent race conditions.
                    </>
                  ),
                },
                {
                  title: 'Silent Refresh',
                  desc: (
                    <>
                      It silently makes a background call to{' '}
                      <code className="text-xs bg-slate-100 dark:bg-slate-800 px-1 py-0.5 rounded">
                        POST /auth/refresh
                      </code>{' '}
                      using the secure <code>HttpOnly</code> cookie.
                    </>
                  ),
                },
                {
                  title: 'Token Injection',
                  desc: 'Upon success, it extracts the newly issued JWT and sets it as the default header for future requests.',
                },
                {
                  title: 'Resume Queue',
                  desc: (
                    <>
                      It safely <strong>replays</strong> all paused requests
                      transparently.
                    </>
                  ),
                },
              ].map((step, i) => (
                <div
                  key={i}
                  className="flex gap-4 items-start p-4 bg-slate-50 dark:bg-[#1c1c1c] border border-slate-200 dark:border-slate-800/80 rounded-xl transition-all hover:border-blue-300 dark:hover:border-blue-800/50 hover:shadow-sm"
                >
                  <div className="shrink-0 w-8 h-8 flex items-center justify-center bg-blue-100 dark:bg-blue-500/20 text-blue-700 dark:text-blue-400 font-bold rounded-full border border-blue-200 dark:border-blue-500/30">
                    {i + 1}
                  </div>
                  <div>
                    <h4 className="font-semibold text-slate-900 dark:text-white text-base">
                      {step.title}
                    </h4>
                    <p className="text-slate-600 dark:text-slate-400 mt-1 leading-relaxed text-sm">
                      {step.desc}
                    </p>
                  </div>
                </div>
              ))}
            </div>

            <h3
              id="interceptor-axios"
              className="text-2xl font-semibold mt-8 mb-3 scroll-mt-8"
            >
              Custom Axios Instance Integration
            </h3>
            <p className="text-base text-slate-600 dark:text-slate-400 mb-4">
              If your frontend application uses its own Axios instance to talk
              to your proprietary backend, you can seamlessly attach Cerberus's
              token rotation logic to it. This automatically injects the{' '}
              <code>Authorization: Bearer &lt;token&gt;</code> header and
              silently rotates the token in the background if your backend
              returns a <code>401</code>.
            </p>

            <ApiRef
              name="cerberus.attachInterceptor(clientInstance)"
              desc="Attaches Cerberus token rotation interceptors to your own Axios instance."
              args={[
                {
                  name: 'clientInstance',
                  type: 'AxiosInstance',
                  desc: 'Your configured Axios instance.',
                },
              ]}
              ret="void"
            />

            <CodeBlock
              language="typescript"
              code={`import axios from 'axios';
import { cerberus } from './cerberus';

// 1. Create your own API client to talk to your proprietary backend
export const myBackendApi = axios.create({
  baseURL: 'https://api.mycoolapp.com',
});

// 2. Attach Cerberus's interceptor logic
cerberus.attachInterceptor(myBackendApi);

// 3. Now use your client freely. If the JWT expires, Cerberus will automatically 
// pause the request, rotate the tokens, and seamlessly retry it!
await myBackendApi.get('/some-protected-route');
`}
            />

            <h3
              id="interceptor-manual"
              className="text-2xl font-semibold mt-8 mb-3 scroll-mt-8"
            >
              Manual Token Retrieval
            </h3>
            <p className="text-base text-slate-600 dark:text-slate-400 mb-4">
              If you are not using Axios and need to manually fetch the access
              token (e.g. for a WebSocket connection or fetch API), use{' '}
              <code>getToken()</code>. This method will automatically decode the
              JWT and trigger a silent background refresh if the token expires
              within the next 30 seconds.
            </p>

            <ApiRef
              name="cerberus.getToken()"
              desc="Retrieves the current access token safely, automatically refreshing it if it expires within 30 seconds."
              args={[]}
              ret="Promise<string | null>"
            />

            <h3
              id="interceptor-react"
              className="text-2xl font-semibold mt-8 mb-3 scroll-mt-8"
            >
              Reacting to Token Changes
            </h3>
            <p className="text-base text-slate-600 dark:text-slate-400 mb-4">
              You can listen for changes to the Access Token using{' '}
              <code>onTokenChange</code>. This is extremely useful for keeping
              your frontend UI framework (like React or Vue) in sync with the
              SDK's internal state. Whenever the token rotates or the user logs
              in/out, the listener will be called.
            </p>

            <ApiRef
              name="cerberus.onTokenChange(listener)"
              desc="Registers a listener that is called whenever the access token is updated or cleared."
              args={[
                {
                  name: 'listener',
                  type: '(token: string | null) => void',
                  desc: 'The callback function to execute.',
                },
              ]}
              ret="() => void (An unsubscribe function)"
            />

            <CodeBlock
              language="typescript"
              code={`import { useEffect, useState } from 'react';
import { cerberus } from './cerberus';

export function useCerberusAuth() {
  const [token, setToken] = useState(cerberus.getAccessToken());

  useEffect(() => {
    // 1. Subscribe to token changes
    const unsubscribe = cerberus.onTokenChange((newToken) => {
      setToken(newToken);
    });

    // 2. Cleanup the listener when the component unmounts
    return () => {
      unsubscribe();
    };
  }, []);

  return { isAuthenticated: !!token };
}
`}
            />
          </section>

          <section id="schemas" className="scroll-mt-8 mb-16">
            <h2 className="text-3xl font-bold tracking-tight mb-4 flex items-center gap-2 border-b border-slate-200 dark:border-slate-800 pb-2">
              <Code2 className="w-8 h-8 text-blue-500" />
              Type Schemas
            </h2>
            <p className="text-base text-slate-600 dark:text-slate-400 mb-4">
              The SDK is fully typed and exports the following interfaces for
              your convenience.
            </p>

            <h3
              id="schema-user"
              className="text-2xl font-semibold mb-3 scroll-mt-8"
            >
              User
            </h3>
            <CodeBlock
              language="typescript"
              code={`export interface User {
  id: string;
  email: string;
  is_active: boolean;
  created_at: string;
  updated_at?: string;
  project_id?: string;
  name?: string;
  picture?: string;
  receive_updates?: boolean;
  login_methods?: string[];
}`}
            />

            <h3
              id="schema-session"
              className="text-2xl font-semibold mt-8 mb-3 scroll-mt-8"
            >
              Session
            </h3>
            <CodeBlock
              language="typescript"
              code={`export interface Session {
  family_id: string;
  ip_address: string | null;
  user_agent: string | null;
  created_at: string;
  last_active: string;
  is_current: boolean;
  auth_provider: string;
}`}
            />

            <h3
              id="schema-responses"
              className="text-2xl font-semibold mt-8 mb-3 scroll-mt-8"
            >
              Message Responses
            </h3>
            <CodeBlock
              language="typescript"
              code={`export interface MessageResponse {
  message: string;
}

export interface LoginResponse {
  message: string;
  csrf_token: string;
}`}
            />
          </section>
        </div>
      </main>

      <aside className="hidden xl:block w-56 shrink-0 self-start sticky top-12 pl-6 ml-6 border-l border-slate-200 dark:border-slate-800/50 max-h-[calc(100vh-6rem)] overflow-y-auto pb-8 scrollbar-none [-ms-overflow-style:none] [&::-webkit-scrollbar]:hidden">
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
                  section.subItems.some((sub) => activeSection === sub.id)
                    ? 'text-blue-600 dark:text-blue-400 font-medium'
                    : 'text-slate-600 dark:text-slate-300 hover:text-slate-900 dark:hover:text-white'
                }`}
              >
                {section.title}
              </button>
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
            </div>
          ))}
        </div>
      </aside>
    </>
  )
}
