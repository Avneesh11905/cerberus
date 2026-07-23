import { Link } from '@tanstack/react-router'
import { ShieldCheck } from 'lucide-react'
import { useAuthStore } from '../../store/auth'

export function PublicLayout({ children }: { children: React.ReactNode }) {
  const accessToken = useAuthStore(state => state.accessToken)
  const isCheckingSession = useAuthStore(state => state.isCheckingSession)

  return (
    <div className="min-h-screen bg-vanilla flex flex-col font-sans selection:bg-slate selection:text-vanilla">
      {/* Navigation */}
      <nav className="w-full h-16 border-b-2 border-taupe/30 bg-vanilla sticky top-0 z-50">
        <div className="w-full max-w-7xl mx-auto h-full px-4 sm:px-6 flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <div className="w-8 h-8 rounded bg-slate text-vanilla flex items-center justify-center flat-shadow-taupe shrink-0">
              <ShieldCheck size={20} />
            </div>
            <span className="text-xl font-display font-bold text-slate tracking-tight hidden sm:block">Cerberus</span>
          </div>
          
          <div className="flex items-center space-x-2 sm:space-x-4 min-w-35 justify-end">
            {accessToken ? (
              <Link 
                to="/dashboard" 
                className="text-xs sm:text-sm font-bold text-slate bg-sand px-3 sm:px-4 py-2 rounded-md border-2 border-taupe flat-shadow-slate hover:translate-y-0.5 hover:translate-x-0.5 hover:shadow-none transition-all whitespace-nowrap"
              >
                Go to Dashboard
              </Link>
            ) : isCheckingSession ? (
              <div className="w-32 h-9 bg-taupe/10 animate-pulse rounded-md" />
            ) : (
              <>
                <Link to="/login" className="text-xs sm:text-sm font-bold text-slate hover:text-slate/80 transition-colors whitespace-nowrap">
                  Log in
                </Link>
                <Link 
                  to="/register" 
                  className="text-xs sm:text-sm font-bold text-vanilla bg-slate px-3 sm:px-4 py-2 rounded-md border-2 border-slate flat-shadow-taupe hover:translate-y-0.5 hover:translate-x-0.5 hover:shadow-none transition-all whitespace-nowrap"
                >
                  Sign up
                </Link>
              </>
            )}
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="grow">
        {children}
      </main>

      {/* Footer */}
      <footer className="w-full px-6 py-6 border-t-2 border-taupe/30 bg-sand flex flex-col items-center justify-center">
        <div className="flex items-center space-x-2 mb-2">
          <ShieldCheck size={20} className="text-slate" />
          <span className="text-xl font-display font-bold text-slate tracking-tight">Cerberus</span>
        </div>
        <p className="text-slate/70 font-medium text-xs text-center">
          © {new Date().getFullYear()} Cerberus Platform. All rights reserved.
        </p>
      </footer>
    </div>
  )
}
