import { createFileRoute } from '@tanstack/react-router'
import { Terminal, Code2 } from 'lucide-react'
import { CodeBlock } from '#/components/CodeBlock'
import { useEffect, useState } from 'react'

export const Route = createFileRoute('/docs/sdk/')({
  component: DocsSdkIndex,
})

function DocsSdkIndex() {
  const [activeSection, setActiveSection] = useState('getting-started')

  useEffect(() => {
    const scrollContainer = document.querySelector('.flex-1.overflow-y-auto')
    if (scrollContainer) scrollContainer.scrollTop = 0
  }, [])

  const sections = [
    { id: 'getting-started', title: 'Getting Started' },
    { id: 'installation', title: 'Installation' },
    { id: 'initialization', title: 'Initialization' }
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
        
        <section id="getting-started" className="scroll-mt-8 mb-16">
          <h1 className="text-4xl md:text-5xl font-extrabold tracking-tight mb-6">Cerberus SDK Reference</h1>
          <p className="text-lg text-slate-600 dark:text-slate-400 mb-8 leading-relaxed">
            The official JavaScript/TypeScript Frontend SDK for the Cerberus Identity Platform. Seamlessly integrate Cerberus Authentication into any frontend application (React, Vue, Next.js, Svelte, Vanilla JS).
          </p>
          <div className="p-4 bg-slate-50 dark:bg-[#1c1c1c] border border-blue-200 dark:border-blue-800/50 rounded-xl text-sm text-blue-800 dark:text-blue-300">
            <strong>Looking for the backend?</strong> This is the frontend SDK. The core backend Auth-as-a-Service engine and the Global Dashboard can be found in the main repository: <a href="https://github.com/Avneesh11905/cerberus" target="_blank" className="font-semibold underline">Avneesh11905/cerberus</a>.
          </div>
          
          <h3 className="text-2xl font-bold mt-8 mb-4">Key Features</h3>
          <ul className="space-y-2 text-slate-600 dark:text-slate-400 mb-8">
            <li><strong>Silent Token Refresh:</strong> Automatically intercepts <code>401 Unauthorized</code> responses, refreshes the Access Token, and transparently retries requests.</li>
            <li><strong>Cross-Origin Security:</strong> Pre-configured with <code>withCredentials: true</code> for secure cross-origin cookies.</li>
            <li><strong>Tenant Scoping:</strong> Automatically injects your <code>X-Cerberus-API-Key</code> into every request.</li>
            <li><strong>End-to-End Type Safety:</strong> Fully typed requests and responses mirroring backend schemas.</li>
          </ul>
        </section>

        <section id="installation" className="scroll-mt-8 mb-16">
          <h2 className="text-3xl font-bold tracking-tight mb-4 flex items-center gap-2 border-b border-slate-200 dark:border-slate-800 pb-2">
            <Terminal className="w-8 h-8 text-blue-500" />
            Installation
          </h2>
          <p className="text-base text-slate-600 dark:text-slate-400 mb-4">
            You can install this SDK directly from the GitHub repository using npm, yarn, or pnpm.
          </p>
          <CodeBlock 
            language="bash"
            title="Terminal"
            code={`# Using npm\nnpm install github:Avneesh11905/cerberus-sdk#main\n\n# Using pnpm\npnpm add github:Avneesh11905/cerberus-sdk#main`}
          />
          <p className="text-sm text-slate-500 italic mt-4">(The package contains a prepare script that automatically compiles the TypeScript code upon installation).</p>
        </section>

        <section id="initialization" className="scroll-mt-8 mb-16">
          <h2 className="text-3xl font-bold tracking-tight mb-4 flex items-center gap-2 border-b border-slate-200 dark:border-slate-800 pb-2">
            <Code2 className="w-8 h-8 text-blue-500" />
            Initialization
          </h2>
          <p className="text-base text-slate-600 dark:text-slate-400 mb-4">
            Initialize the SDK once in your application and export it. Provide your backend API URL and the Tenant API Key generated from your Cerberus Dashboard.
          </p>
          <CodeBlock 
            language="typescript"
            title="src/lib/cerberus.ts"
            code={`import { CerberusClient } from '@cerberus/sdk';\nexport const cerberus = new CerberusClient({\n  apiKey: 'cerb_XXXXXXXXXX'    // Your Project API Key\n  // baseUrl: 'https://...',        // Optional: Only needed if you are self-hosting the backend\n});`}
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
