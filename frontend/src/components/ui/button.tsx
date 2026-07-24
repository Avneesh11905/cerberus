import * as React from "react"
import { cva, type VariantProps } from "class-variance-authority"
import { cn } from "../../lib/utils"

const buttonVariants = cva(
  "inline-flex items-center justify-center whitespace-nowrap rounded-xl text-sm font-bold ring-offset-vanilla transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-slate focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50",
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
