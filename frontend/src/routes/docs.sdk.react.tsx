import { createFileRoute } from '@tanstack/react-router'
import { Shield } from 'lucide-react'
import { CodeBlock } from '#/components/CodeBlock'
import { useEffect, useState } from 'react'

export const Route = createFileRoute('/docs/sdk/react')({
  component: DocsSdkReact,
})

function DocsSdkReact() {
  const [activeSection, setActiveSection] = useState('protecting-routes')

  useEffect(() => {
    const scrollContainer = document.querySelector('.flex-1.overflow-y-auto')
    if (scrollContainer) scrollContainer.scrollTop = 0
  }, [])

  const sections = [
    { id: 'protecting-check', title: 'Check Auth State' },
    { id: 'protecting-private', title: 'Private Routes' },
    { id: 'protecting-guest', title: 'Guest Routes' },
    { id: 'protecting-public', title: 'Public Routes' }
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
      { rootMargin: '-15% 0px -60% 0px' }
    )

    sections.forEach((section) => {
      const el = document.getElementById(section.id)
      if (el) observer.observe(el)
    })

    return () => observer.disconnect()
  }, [])

  const scrollToSection = (id: string) => {
    setActiveSection(id)
    document.getElementById(id)?.scrollIntoView({ behavior: 'smooth', block: 'start' })
  }

  return (
    <>
      <main className="flex-1 min-w-0 max-w-4xl font-outfit pb-[50vh]">
        <div className="prose prose-slate dark:prose-invert max-w-none">
          
          <section id="protecting-routes" className="scroll-mt-8 mb-16">
            <h1 className="text-4xl md:text-5xl font-extrabold tracking-tight mb-6 flex items-center gap-4">
              <Shield className="w-10 h-10 text-blue-500" />
              Protecting Routes in React
            </h1>
            <p className="text-lg text-slate-600 dark:text-slate-400 mb-8 leading-relaxed">
              Because Cerberus handles token refreshes silently in the background, you can protect frontend routes using a standard Auth Context.
            </p>
            
            <h3 id="protecting-check" className="text-2xl font-semibold mb-3 scroll-mt-8">1. Check Auth State on Load</h3>
            <p className="text-slate-600 dark:text-slate-400 text-base mb-4">When your app mounts, try to fetch the current user profile. If it succeeds, they are logged in. If it throws a 401 error, they aren't.</p>
            <CodeBlock 
              language="typescript"
              code={`import { useState, useEffect, createContext, useContext } from 'react';
import { cerberus } from './cerberus'; // The SDK instance you initialized

export const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    cerberus.users.getMe()
      .then(setUser)
      .catch(() => setUser(null)) // 401 means not logged in
      .finally(() => setIsLoading(false));
  }, []);

  return (
    <AuthContext.Provider value={{ user, isLoading }}>
      {children}
    </AuthContext.Provider>
  );
}

// Custom hook to use the auth state
export const useAuth = () => useContext(AuthContext);`}
            />

            <h3 id="protecting-private" className="text-2xl font-semibold mt-8 mb-3 scroll-mt-8">2. Wrap Private Routes (Protected)</h3>
            <p className="text-slate-600 dark:text-slate-400 text-base mb-4">Use the context to block unauthorized access to private routes like a Dashboard. If the user isn't logged in, they are redirected to the login page.</p>
            <CodeBlock 
              language="typescript"
              code={`import { Navigate } from 'react-router-dom';
import { useAuth } from './AuthProvider'; // The hook we created above
import { LoadingSpinner } from './components/LoadingSpinner';

export function ProtectedRoute({ children }) {
  const { user, isLoading } = useAuth();

  if (isLoading) return <LoadingSpinner />;
  if (!user) return <Navigate to="/login" replace />;

  return children;
}`}
            />

            <h3 id="protecting-guest" className="text-2xl font-semibold mt-8 mb-3 scroll-mt-8">3. Wrap Guest Routes (Logged Out Only)</h3>
            <p className="text-slate-600 dark:text-slate-400 text-base mb-4">For pages like <strong>Login</strong> or <strong>Register</strong>, you don't want logged-in users to access them. Use a Guest Route to redirect them to the dashboard if they are already authenticated.</p>
            <CodeBlock 
              language="typescript"
              code={`import { Navigate } from 'react-router-dom';
import { useAuth } from './AuthProvider';
import { LoadingSpinner } from './components/LoadingSpinner';

export function GuestRoute({ children }) {
  const { user, isLoading } = useAuth();

  if (isLoading) return <LoadingSpinner />;
  if (user) return <Navigate to="/dashboard" replace />; // Already logged in

  return children;
}`}
            />

            <h3 id="protecting-public" className="text-2xl font-semibold mt-8 mb-3 scroll-mt-8">4. Unprotected (Public) Routes</h3>
            <p className="text-slate-600 dark:text-slate-400 text-base mb-4">For public landing pages or documentation, simply don't wrap the route in either component. The user will be able to view the page regardless of their authentication state.</p>

            <div className="mt-8 p-5 bg-slate-50 dark:bg-[#1c1c1c] border border-blue-200 dark:border-blue-800/50 rounded-xl">
              <h4 className="text-sm font-semibold text-blue-800 dark:text-blue-300 mb-2">Troubleshooting: Session constantly drops or getMe() fails?</h4>
              <p className="text-sm text-slate-600 dark:text-slate-400 mb-3">
                If the code above always returns <code>401 Unauthorized</code> even after successfully calling <code>cerberus.auth.login()</code>, the browser is actively blocking the secure <code>HttpOnly</code> cookies.
              </p>
              <ul className="list-disc pl-5 space-y-1 text-sm text-slate-600 dark:text-slate-400">
                <li><strong>Check Dashboard Origins:</strong> Ensure your exact frontend URL (e.g., <code>http://localhost:3000</code>) is added to your project's <strong>Allowed Origins</strong> in the Cerberus Global Dashboard. If the origin doesn't match, cookies will not be set.</li>
                <li><strong>Check Browser Settings:</strong> If you are testing across completely different domains without HTTPS, your browser might block cross-site tracking cookies. Use HTTPS or ensure localhost environments run without strict tracking protection enabled.</li>
              </ul>
            </div>
          </section>

        </div>
      </main>

      <aside className="hidden xl:block w-56 shrink-0 self-start sticky top-12 pl-6 ml-6 border-l border-slate-200 dark:border-slate-800/50">
        <h4 className="text-xs font-semibold text-slate-900 dark:text-white uppercase tracking-wider mb-4 font-outfit">On this page</h4>
        <nav className="flex flex-col gap-2">
          {sections.map((section) => (
            <div key={section.id} className="flex flex-col">
              <button
                onClick={() => scrollToSection(section.id)}
                className={`text-left text-sm transition-colors py-1 ${
                  activeSection === section.id
                    ? 'text-blue-600 dark:text-blue-400 font-medium'
                    : 'text-slate-500 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'
                }`}
              >
                {section.title}
              </button>
            </div>
          ))}
        </nav>
      </aside>
    </>
  )
}
