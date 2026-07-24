import * as React from "react"
import { Copy, ClipboardCheck, Download } from "lucide-react"
import { motion } from "framer-motion"
import { cva, type VariantProps } from "class-variance-authority"
import { cn } from "../../lib/utils"

const buttonVariants = cva(
  "inline-flex items-center justify-center whitespace-nowrap rounded-xl text-sm font-bold ring-offset-vanilla transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-slate focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 cursor-pointer",
  {
    variants: {
      variant: {
        primary:
          "bg-slate text-vanilla shadow-[4px_4px_0px_var(--taupe)] hover:-translate-y-0.5 hover:shadow-[6px_6px_0px_var(--taupe)] active:translate-y-0.5 active:translate-x-0.5 active:shadow-[2px_2px_0px_var(--taupe)]",
        secondary:
          "bg-taupe text-slate border-2 border-slate shadow-[4px_4px_0px_var(--slate)] hover:-translate-y-1 hover:shadow-[6px_6px_0px_var(--slate)] active:translate-y-0.5 active:translate-x-0.5 active:shadow-none",
        destructive:
          "bg-transparent text-terracotta border-2 border-terracotta shadow-[4px_4px_0px_var(--terracotta)] hover:-translate-y-1 hover:shadow-[6px_6px_0px_var(--terracotta)] active:translate-y-0.5 active:translate-x-0.5 active:shadow-none",
        outline:
          "bg-transparent text-slate border-2 border-slate shadow-[4px_4px_0px_var(--slate)] hover:-translate-y-1 hover:shadow-[6px_6px_0px_var(--slate)] active:translate-y-0.5 active:translate-x-0.5 active:shadow-none",
        inverse:
          "bg-vanilla text-slate border-2 border-slate shadow-[4px_4px_0px_var(--taupe)] hover:-translate-y-1 hover:shadow-[6px_6px_0px_var(--taupe)] active:translate-y-0.5 active:translate-x-0.5 active:shadow-none",
        ghost: "hover:bg-taupe/20 text-slate",
      },
      size: {
        default: "h-10 px-4 py-2",
        sm: "h-9 rounded-xl px-3",
        lg: "h-11 rounded-xl px-8",
        xl: "h-14 rounded-xl px-8 text-lg",
        icon: "h-10 w-10",
      },
    },
    defaultVariants: {
      variant: "primary",
      size: "default",
    },
  }
)

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, size, ...props }, ref) => {
    return (
      <button
        ref={ref}
        className={cn(buttonVariants({ variant, size, className }))}
        {...props}
      />
    )
  }
)
Button.displayName = "Button"

export { Button, buttonVariants }

import { AnimatedIconSwap } from "./animated-icon-swap"

export interface CopyButtonProps extends Omit<ButtonProps, 'onClick'> {
  value: string
  copyKey?: string
}

export function CopyButton({ value, copyKey = 'copy', className, variant = "outline", size = "icon", ...props }: CopyButtonProps) {
  const [copiedKey, setCopiedKey] = React.useState<string | null>(null)

  const handleCopy = (text: string, key: string) => {
    navigator.clipboard.writeText(text)
    setCopiedKey(key)
    setTimeout(() => {
      setCopiedKey(null)
    }, 2000)
  }

  return (
    <Button 
      variant={variant} 
      size={size} 
      onClick={() => handleCopy(value, copyKey)} 
      className={className}
      {...props}
    >
      <AnimatedIconSwap 
        isActive={copiedKey === copyKey} 
        inactiveIcon={Copy} 
        activeIcon={ClipboardCheck} 
        className={props.children ? "w-3.5 h-3.5 mr-1" : "w-4 h-4"} 
        activeClassName={props.children ? "w-3.5 h-3.5 mr-1 text-sage" : "w-4 h-4 text-sage"} 
      />
      {props.children}
    </Button>
  )
}

export interface DownloadButtonProps extends Omit<ButtonProps, 'onClick'> {
  onDownload: () => void
}

export function DownloadButton({ onDownload, className, variant = "outline", size = "icon", ...props }: DownloadButtonProps) {
  const [isDownloading, setIsDownloading] = React.useState(false)

  const handleDownload = () => {
    onDownload()
    setIsDownloading(true)
    setTimeout(() => {
      setIsDownloading(false)
    }, 1000)
  }

  return (
    <Button 
      variant={variant} 
      size={size} 
      onClick={handleDownload} 
      className={className}
      {...props}
    >
      <div className="relative overflow-hidden inline-flex items-center justify-center">
        <motion.div
          animate={
            isDownloading 
              ? { y: [0, 20, -20, 0], opacity: [1, 0, 0, 1] } 
              : { y: 0, opacity: 1 }
          }
          transition={{ duration: 0.6, times: [0, 0.4, 0.6, 1], ease: "easeInOut" }}
          className="flex items-center justify-center"
        >
          <Download className={props.children ? "w-3.5 h-3.5 mr-1" : "w-4 h-4"} />
        </motion.div>
      </div>
      {props.children}
    </Button>
  )
}
