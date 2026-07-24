import {
  CircleCheckIcon,
  InfoIcon,
  Loader2Icon,
  OctagonXIcon,
  TriangleAlertIcon,
} from "lucide-react"
import { Toaster as Sonner, type ToasterProps } from "sonner"

const Toaster = ({ ...props }: ToasterProps) => {
  return (
    <Sonner
      className="toaster group"
      toastOptions={{
        classNames: {
          toast: "group toast !bg-sand !text-slate !border-2 !border-slate !shadow-[4px_4px_0px_rgba(96,114,116,1)] !font-bold !rounded-none",
          description: "!text-slate/70 !font-semibold",
          actionButton: "!bg-slate !text-vanilla !border-2 !border-transparent hover:!shadow-[2px_2px_0px_rgba(178,165,155,1)]",
          cancelButton: "!bg-taupe !text-vanilla",
        },
      }}
      icons={{
        success: <CircleCheckIcon className="size-4 text-sage" />,
        info: <InfoIcon className="size-4 text-slate" />,
        warning: <TriangleAlertIcon className="size-4 text-ochre" />,
        error: <OctagonXIcon className="size-4 text-terracotta" />,
        loading: <Loader2Icon className="size-4 animate-spin text-slate" />,
      }}
      style={{
        "--normal-bg": "var(--warm-sand)",
        "--normal-text": "var(--slate)",
        "--normal-border": "var(--slate)",
        "--border-radius": "0px",
        "--toast-svg-margin-start": "0.5rem",
        "--toast-svg-margin-end": "0.75rem",
      } as React.CSSProperties}
      {...props}
    />
  )
}

export { Toaster }
