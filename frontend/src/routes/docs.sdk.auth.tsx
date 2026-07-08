import { createFileRoute } from '@tanstack/react-router'
import { Shield } from 'lucide-react'
import { CodeBlock } from '#/components/CodeBlock'
import { ApiRef } from '#/components/ApiRef'
import { useEffect, useState } from 'react'

export const Route = createFileRoute('/docs/sdk/auth')({
  component: DocsSdkAuth,
})

function DocsSdkAuth() {
  const [activeSection, setActiveSection] = useState('auth-methods')

  useEffect(() => {
    const scrollContainer = document.querySelector('.flex-1.overflow-y-auto')
    if (scrollContainer) scrollContainer.scrollTop = 0
  }, [])

  const sections = [
    { id: 'auth-register', title: 'Register & Verification' },
    { id: 'auth-login', title: 'Standard Login' },
    { id: 'auth-oauth', title: 'Dynamic OAuth' },
    { id: 'auth-password', title: 'Password Management' },
    { id: 'auth-sessions', title: 'Session Management' }
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
          
          <section id="auth-methods" className="scroll-mt-8 mb-16">
            <h1 className="text-4xl md:text-5xl font-extrabold tracking-tight mb-6 flex items-center gap-4">
              <Shield className="w-10 h-10 text-blue-500" />
              Authentication
            </h1>
            <p className="text-lg text-slate-600 dark:text-slate-400 mb-8 leading-relaxed">
              The <code>cerberus.auth</code> module handles the entire lifecycle of user sessions.
            </p>
            
            <h3 id="auth-register" className="text-2xl font-semibold mb-3 scroll-mt-8">Register & Email Verification</h3>
            <p className="text-slate-600 dark:text-slate-400 text-base mb-4">Registration is a two-step process to ensure email ownership.</p>
            
            <CodeBlock 
              language="typescript"
              code={`// 1. Create the account (sends a 6-digit OTP to the email)
await cerberus.auth.register({ 
  email: 'test@example.com', 
  password: 'StrongPassword123!',
  name: 'John Doe' // Optional
});

// 2. Verify the account using the OTP
await cerberus.auth.verifyEmail({ 
  email: 'test@example.com', 
  otp: '123456' 
});

// Optional: Resend the OTP if it expired
await cerberus.auth.resendVerification({ email: 'test@example.com' });`}
            />

            <ApiRef 
              name="cerberus.auth.register(data)"
              desc="Creates a new user account and triggers an email verification OTP."
              args={[
                { name: "data.email", type: "string", desc: "The user's email address." },
                { name: "data.password", type: "string", desc: "A strong password (min 8 chars)." },
                { name: "data.name", type: "string?", desc: "Optional full name of the user." }
              ]}
              ret="Promise<MessageResponse>"
            />

            <ApiRef 
              name="cerberus.auth.verifyEmail(data)"
              desc="Verifies the account using the OTP sent to the user's email."
              args={[
                { name: "data.email", type: "string", desc: "The user's email address." },
                { name: "data.otp", type: "string", desc: "The 6-digit OTP received via email." }
              ]}
              ret="Promise<MessageResponse>"
            />

            <ApiRef 
              name="cerberus.auth.resendVerification(data)"
              desc="Resends the verification OTP to the given email if it has expired."
              args={[
                { name: "data.email", type: "string", desc: "The user's email address." }
              ]}
              ret="Promise<MessageResponse>"
            />

            <h3 id="auth-login" className="text-2xl font-semibold mt-8 mb-3 scroll-mt-8">Standard Email/Password Login</h3>
            <p className="text-slate-600 dark:text-slate-400 text-base mb-4">Logging in automatically sets the secure HttpOnly refresh cookie in the user's browser. The SDK intercepts the response and stores the short-lived JWT in memory for subsequent requests.</p>
            
            <CodeBlock 
              language="typescript"
              code={`await cerberus.auth.login({ 
  email: 'test@example.com', 
  password: 'StrongPassword123!' 
});

// You are now fully authenticated!`}
            />

            <ApiRef 
              name="cerberus.auth.login(credentials)"
              desc="Authenticates a user and establishes a secure session via HttpOnly cookies."
              args={[
                { name: "credentials.email", type: "string", desc: "The registered email address." },
                { name: "credentials.password", type: "string", desc: "The user's password." }
              ]}
              ret="Promise<LoginResponse>"
            />

            <h3 id="auth-oauth" className="text-2xl font-semibold mt-8 mb-3 scroll-mt-8">Dynamic OAuth Integrations</h3>
            
            <CodeBlock 
              language="typescript"
              code={`// 1. Bind this directly to your "Login with Google" button onClick handler
await cerberus.auth.initiateOAuthLogin('google');

// 2. Automatically handle the callback when redirected back to your landing page
const result = await cerberus.auth.handleOAuthCallback();

if (result) {
  console.log("OAuth Login Successful! New user:", result.isNewUser);
}`}
            />

            <ApiRef 
              name="cerberus.auth.initiateOAuthLogin(provider)"
              desc="Fetches the preflight URL from the backend and redirects the browser to the OAuth provider (e.g. Google)."
              args={[
                { name: "provider", type: "string", desc: "The OAuth provider name (e.g. 'google', 'github')." }
              ]}
              ret="Promise<void>"
            />

            <ApiRef 
              name="cerberus.auth.handleOAuthCallback()"
              desc="Automatically reads the OAuth code from the URL, exchanges it with the backend, cleans the URL history, and caches the user."
              args={[]}
              ret="Promise<{ user: User, isNewUser: boolean } | null>"
            />

            <h3 id="auth-password" className="text-2xl font-semibold mt-8 mb-3 scroll-mt-8">Password Management</h3>
            
            <CodeBlock 
              language="typescript"
              title="src/lib/auth.ts"
              code={`// Request a password reset email
await cerberus.auth.requestPasswordReset('user@domain.com');

// Execute a password reset using the token from the email
await cerberus.auth.executePasswordReset('reset-token-123', 'new_secure_password123!');

// Change the password for an authenticated user
await cerberus.auth.changePassword({
  current_password: 'old_password',
  new_password: 'new_secure_password123!'
});`}
            />

            <ApiRef 
              name="cerberus.auth.requestPasswordReset(email)"
              desc="Sends a password reset email with a secure, short-lived token to the specified email address."
              args={[
                { name: "email", type: "string", desc: "The email address of the account." }
              ]}
              ret="Promise<MessageResponse>"
            />

            <ApiRef 
              name="cerberus.auth.executePasswordReset(token, new_password)"
              desc="Resets the user's password using the token sent to their email."
              args={[
                { name: "token", type: "string", desc: "The token received in the reset email." },
                { name: "new_password", type: "string", desc: "The new secure password." }
              ]}
              ret="Promise<MessageResponse>"
            />

            <ApiRef 
              name="cerberus.auth.changePassword(data)"
              desc="Changes the password for the currently authenticated user."
              args={[
                { name: "data.current_password", type: "string?", desc: "The user's current password. Optional if they authenticated via OAuth." },
                { name: "data.new_password", type: "string", desc: "The new secure password." }
              ]}
              ret="Promise<MessageResponse>"
            />

            <h3 id="auth-sessions" className="text-2xl font-semibold mt-8 mb-3 scroll-mt-8">Session Management</h3>

            <CodeBlock 
              language="typescript"
              code={`// Log out of the current device
await cerberus.auth.logout();

// Log out of ALL devices instantly (revokes all refresh tokens)
await cerberus.auth.logoutAll();

// Get a list of all active sessions for the user
const sessions = await cerberus.auth.listSessions();

// Revoke a specific unrecognized device
await cerberus.auth.revokeSession('session_family_uuid_here');`}
            />

            <ApiRef 
              name="cerberus.auth.logout()"
              desc="Logs the user out of the current device by revoking the current session cookie."
              args={[]}
              ret="Promise<MessageResponse>"
            />

            <ApiRef 
              name="cerberus.auth.logoutAll()"
              desc="Instantly revokes all active refresh tokens across all devices for the user."
              args={[]}
              ret="Promise<MessageResponse>"
            />

            <ApiRef 
              name="cerberus.auth.listSessions()"
              desc="Retrieves a list of all active sessions (devices) for the current user."
              args={[]}
              ret="Promise<Session[]>"
            />

            <ApiRef 
              name="cerberus.auth.revokeSession(familyId)"
              desc="Revokes a specific session family (device) by its ID."
              args={[
                { name: "familyId", type: "string", desc: "The UUID of the session family to revoke." }
              ]}
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
