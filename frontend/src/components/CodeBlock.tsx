import { useState } from 'react'
import { Highlight } from 'prism-react-renderer'
import { useTheme } from 'next-themes'
import { Copy, CheckCircle2 } from 'lucide-react'
import { Button } from '#/components/ui/button'

const cerberusThemeDark = {
  plain: {
    color: "#f8fafc",
    backgroundColor: "transparent",
  },
  styles: [
    { types: ["keyword", "operator", "modifier", "control-flow"], style: { color: "#ec4899" } },
    { types: ["string", "inserted"], style: { color: "#34d399" } },
    { types: ["class-name", "maybe-class-name", "builtin", "type"], style: { color: "#818cf8" } },
    { types: ["function", "method"], style: { color: "#a78bfa" } },
    { types: ["property", "variable", "constant"], style: { color: "#e2e8f0" } },
    { types: ["comment"], style: { color: "#64748b", fontStyle: "italic" as const } },
    { types: ["punctuation"], style: { color: "#94a3b8" } },
    { types: ["tag"], style: { color: "#34d399" } },
    { types: ["attr-name"], style: { color: "#818cf8" } }
  ]
}

const cerberusThemeLight = {
  plain: {
    color: "#334155",
    backgroundColor: "transparent",
  },
  styles: [
    { types: ["keyword", "operator", "modifier", "control-flow"], style: { color: "#9333ea" } },
    { types: ["string", "inserted"], style: { color: "#16a34a" } },
    { types: ["class-name", "maybe-class-name", "builtin", "type"], style: { color: "#ca8a04" } },
    { types: ["function", "method"], style: { color: "#2563eb" } },
    { types: ["property", "variable", "constant"], style: { color: "#0284c7" } },
    { types: ["comment"], style: { color: "#64748b", fontStyle: "italic" as const } },
    { types: ["punctuation"], style: { color: "#334155" } }
  ]
}

export function CodeBlock({ code, language = 'tsx', title, className = "my-6", hideCopy = false, unselectable = false }: { code: string, language?: string, title?: string, className?: string, hideCopy?: boolean, unselectable?: boolean }) {
  const [copied, setCopied] = useState(false)
  const { resolvedTheme } = useTheme()
  const currentTheme = resolvedTheme === 'light' ? cerberusThemeLight : cerberusThemeDark

  const copyToClipboard = () => {
    navigator.clipboard.writeText(code)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  return (
    <div className={`not-prose relative group rounded-2xl overflow-hidden border border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-[#1c1c1c] shadow-lg ${className}`}>
      <div className="relative flex items-center justify-between px-4 py-3 bg-slate-100 dark:bg-[#262626] border-b border-slate-200 dark:border-slate-700/50">
        <div className="flex gap-2 z-10 w-24">
          <div className="w-3 h-3 rounded-full bg-red-400 dark:bg-red-500/80" />
          <div className="w-3 h-3 rounded-full bg-yellow-400 dark:bg-yellow-500/80" />
          <div className="w-3 h-3 rounded-full bg-green-400 dark:bg-green-500/80" />
        </div>
        
        {title && (
          <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
            <span className="text-xs font-mono font-medium text-slate-500 dark:text-slate-400">{title}</span>
          </div>
        )}
        
        {!hideCopy && (
          <Button 
            onClick={copyToClipboard}
            variant="ghost"
            size="sm"
            className="h-7 px-2 text-xs flex items-center gap-1.5 text-slate-500 hover:text-slate-900 dark:text-slate-400 dark:hover:text-white transition-colors z-10"
          >
            {copied ? (
              <>
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600 dark:text-emerald-500" />
                <span className="text-emerald-600 dark:text-emerald-500">Copied</span>
              </>
            ) : (
              <>
                <Copy className="w-3.5 h-3.5" />
                <span>Copy</span>
              </>
            )}
          </Button>
        )}
      </div>
      <div className={`p-5 overflow-x-auto text-sm md:text-base font-medium leading-relaxed bg-slate-50 dark:bg-[#1c1c1c] text-slate-900 dark:text-slate-50 custom-scrollbar ${unselectable ? 'select-none' : ''}`} style={{ fontFamily: '"Syne", monospace' }}>
        <Highlight theme={currentTheme} code={code.trim()} language={language}>
          {({ className: highlightClassName, style, tokens, getLineProps, getTokenProps }) => (
            <pre className={highlightClassName} style={{ ...style, backgroundColor: 'transparent' }}>
              {tokens.map((line, i) => (
                <div key={i} {...getLineProps({ line })} className="table-row">
                  <span className="table-cell text-right pr-4 text-slate-500 select-none opacity-50 text-xs translate-y-0.5">{i + 1}</span>
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
