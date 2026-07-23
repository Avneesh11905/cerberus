import React from 'react';
import { motion } from 'framer-motion';
import { ArrowLeft } from 'lucide-react';
import { useRouter } from '@tanstack/react-router';

export function AuthLayout({ children, title, subtitle, showBackButton = true, maxWidth = "max-w-md" }: { children: React.ReactNode, title: string, subtitle?: string, showBackButton?: boolean, maxWidth?: string }) {
  const router = useRouter();

  return (
    <div className="min-h-screen bg-vanilla flex items-center justify-center p-4">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, ease: [0.16, 1, 0.3, 1] }}
        className={`w-full ${maxWidth} perspective-[1000px]`}
      >
        <div 
          className="flat-card p-6 sm:p-8 rounded-xl flex flex-col relative"
        >
          {/* Inner content animates on Z-axis to pop out when tilted */}
          <div>
            {showBackButton && (
              <button 
                type="button"
                onClick={() => router.history.back()}
                className="absolute top-6 left-6 text-slate/50 hover:text-slate transition-colors"
                aria-label="Go back"
              >
                <ArrowLeft size={20} />
              </button>
            )}
            <div className="mb-6 sm:mb-8 text-center">
              <h1 className="text-2xl sm:text-3xl font-display font-bold text-slate mb-2 tracking-tight">{title}</h1>
              {subtitle && <p className="text-slate/70 text-sm font-medium">{subtitle}</p>}
            </div>
            {children}
          </div>
        </div>
      </motion.div>
    </div>
  );
}
