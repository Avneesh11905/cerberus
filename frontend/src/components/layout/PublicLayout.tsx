import { useNavigate } from '@tanstack/react-router'
import { ShieldCheck } from 'lucide-react'
import { Button } from '../ui/button'
import { useAuthStore } from '../../store/auth'

export function PublicLayout({ children }: { children: React.ReactNode }) {
  const accessToken = useAuthStore((state) => state.accessToken)
  const navigate = useNavigate()

  return (
    <div className="min-h-screen bg-vanilla flex flex-col font-sans selection:bg-slate selection:text-vanilla">
      {/* Navigation */}
      <nav className="w-full h-16 border-b-2 border-taupe/30 bg-vanilla sticky top-0 z-50">
        <div className="w-full max-w-7xl mx-auto h-full px-4 sm:px-6 flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <div className="w-8 h-8 rounded bg-slate text-vanilla flex items-center justify-center flat-shadow-taupe shrink-0">
              <ShieldCheck size={20} />
            </div>
            <span className="text-xl font-display font-bold text-slate tracking-tight hidden sm:block">
              Cerberus
            </span>
          </div>

          <div className="flex items-center space-x-2 sm:space-x-4 min-w-35 justify-end">
            {accessToken ? (
              <Button
                variant="outline"
                onClick={() => navigate({ to: '/dashboard' })}
                className="text-xs sm:text-sm whitespace-nowrap bg-sand"
              >
                Go to Dashboard
              </Button>
            ) : (
              <>
                <Button
                  variant="ghost"
                  onClick={() => navigate({ to: '/login' })}
                  className="text-xs sm:text-sm whitespace-nowrap"
                >
                  Log in
                </Button>
                <Button
                  variant="primary"
                  onClick={() => navigate({ to: '/register' })}
                  className="text-xs sm:text-sm whitespace-nowrap"
                >
                  Sign up
                </Button>
              </>
            )}
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="grow">{children}</main>

      {/* Footer */}
      <footer className="w-full px-6 py-6 border-t-2 border-taupe/30 bg-sand flex flex-col items-center justify-center">
        <div className="flex items-center space-x-2 mb-2">
          <ShieldCheck size={20} className="text-slate" />
          <span className="text-xl font-display font-bold text-slate tracking-tight">
            Cerberus
          </span>
        </div>
        <p className="text-slate/70 font-medium text-xs text-center">
          © {new Date().getFullYear()} Cerberus Platform. All rights reserved.
        </p>
      </footer>
    </div>
  )
}
