import { createFileRoute } from '@tanstack/react-router'
import { Layers } from 'lucide-react'
import { CodeBlock } from '#/components/CodeBlock'
import { ApiRef } from '#/components/ApiRef'
import { useEffect, useState } from 'react'

export const Route = createFileRoute('/docs/sdk/users')({
  component: DocsSdkUsers,
})

function DocsSdkUsers() {
  const [activeSection, setActiveSection] = useState('user-management')

  useEffect(() => {
    const scrollContainer = document.querySelector('.flex-1.overflow-y-auto')
    if (scrollContainer) scrollContainer.scrollTop = 0
  }, [])

  const sections = [
    { id: 'users-cache', title: 'Built-In State Caching' },
    { id: 'users-profile', title: 'Fetching & Updating' },
    { id: 'users-delete', title: 'Account Deletion' }
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
          
          <section id="user-management" className="scroll-mt-8 mb-16">
            <h1 className="text-4xl md:text-5xl font-extrabold tracking-tight mb-6 flex items-center gap-4">
              <Layers className="w-10 h-10 text-blue-500" />
              User Management
            </h1>
            <p className="text-lg text-slate-600 dark:text-slate-400 mb-4 leading-relaxed">
              The <code>cerberus.users</code> module caches user data as the single source of truth and automatically updates it during workflows.
            </p>

            <h3 id="users-cache" className="text-2xl font-semibold mt-8 mb-3 scroll-mt-8">Built-In State Caching</h3>
            <p className="text-slate-600 dark:text-slate-400 text-base mb-4">The SDK automatically caches the user profile. You never need to worry about manually re-fetching the user.</p>
            <CodeBlock 
              language="typescript"
              code={`// Fetch the user (caches internally, deduplicates concurrent requests)
const user = await cerberus.users.getMe();

// Bypass cache and force a fresh fetch from the server
const freshUser = await cerberus.users.getMe(true);`}
            />

            <ApiRef 
              name="cerberus.users.getMe(forceFetch?)"
              desc="Retrieves the current authenticated user profile. Returns from cache if available, unless forced."
              args={[
                { name: "forceFetch", type: "boolean?", defaultValue: "false", desc: "Optional. If true, bypasses the cache and forces a fresh network fetch." }
              ]}
              ret="Promise<User>"
            />

            <h3 id="users-profile" className="text-2xl font-semibold mt-8 mb-3 scroll-mt-8">Fetching & Updating</h3>
            <p className="text-slate-600 dark:text-slate-400 text-base mb-4">You can update the user profile, and the SDK will instantly sync the updated state with the cache.</p>
            <CodeBlock 
              language="typescript"
              code={`// Update profile information (automatically updates the cache)
const updatedUser = await cerberus.users.updateMe({
  name: 'Jane Doe'
});`}
            />

            <ApiRef 
              name="cerberus.users.updateMe(data)"
              desc="Updates the user's profile and immediately synchronizes the internal cache."
              args={[
                { name: "data.name", type: "string?", desc: "Optional new display name for the user." },
                { name: "data.picture", type: "string?", desc: "Optional new avatar URL." },
                { name: "data.receive_updates", type: "boolean?", desc: "Optional preference for marketing/product emails." }
              ]}
              ret="Promise<User>"
            />

            <h3 id="users-delete" className="text-2xl font-semibold mt-8 mb-3 scroll-mt-8">Account Deletion</h3>
            <CodeBlock 
              language="typescript"
              code={`// Permanently soft-delete the user's account and revoke all sessions
await cerberus.users.deleteMe();`}
            />

            <ApiRef 
              name="cerberus.users.deleteMe()"
              desc="Permanently soft-deletes the user's account and revokes all active sessions."
              args={[]}
              ret="Promise<void>"
            />
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
