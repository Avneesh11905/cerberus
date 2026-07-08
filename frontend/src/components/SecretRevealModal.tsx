import { useState } from 'react';
import { Copy, CheckCircle2, AlertTriangle, Download, ShieldCheck, Info } from 'lucide-react';
import { Tooltip, TooltipContent, TooltipTrigger, TooltipProvider } from '#/components/ui/tooltip';
import {
  AlertDialog,
  AlertDialogContent,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogAction,
} from '#/components/ui/alert-dialog';
import { Button } from '#/components/ui/button';
import { Label } from '#/components/ui/label';

export type SecretRevealMode = 'project_created' | 'api_key_rotated' | 'jwt_rotated';

interface SecretRevealModalProps {
  isOpen: boolean;
  onClose: () => void;
  secrets: {
    api_key?: string;
    public_key?: string;
  } | null;
  mode: SecretRevealMode;
}

const MODE_CONFIG: Record<SecretRevealMode, { title: string; icon: 'danger' | 'info' }> = {
  project_created: { title: 'Save Your API Key', icon: 'danger' },
  api_key_rotated: { title: 'API Key Rotated', icon: 'danger' },
  jwt_rotated: { title: 'JWT Keys Rotated', icon: 'info' },
};

function SecretField({
  label,
  value,
  keyName,
  recoverable,
  copiedKey,
  onCopy,
}: {
  label: string;
  value: string;
  keyName: string;
  recoverable: boolean;
  copiedKey: string | null;
  onCopy: (text: string, key: string) => void;
}) {
  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between">
        <Label className="text-slate-700 dark:text-slate-300">{label}</Label>
        {recoverable ? (
          <span className="flex items-center gap-1 text-xs text-emerald-600 dark:text-emerald-400">
            <ShieldCheck className="w-3.5 h-3.5" />
            Retrievable anytime from your dashboard
          </span>
        ) : (
          <span className="flex items-center gap-1 text-xs text-red-500 dark:text-red-400">
            <AlertTriangle className="w-3.5 h-3.5" />
            Shown only once — cannot be recovered
          </span>
        )}
      </div>
      <div className="relative">
        <textarea
          readOnly
          value={value || ''}
          rows={value.includes('BEGIN') ? 5 : 1}
          className="w-full bg-white dark:bg-black/50 border border-slate-200 dark:border-slate-800 rounded-lg p-3 text-sm font-mono text-slate-700 dark:text-slate-300 resize-none pr-12 focus:outline-none focus:border-blue-500/50 transition-colors"
        />
        <TooltipProvider delayDuration={0}>
          <Tooltip>
            <TooltipTrigger asChild>
              <Button
                variant="ghost"
                size="icon"
                onClick={() => onCopy(value, keyName)}
                className="absolute right-2 top-[50%] -translate-y-1/2 h-8 w-8 text-slate-400 hover:text-slate-900 dark:hover:text-white hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
                title="Copy to clipboard"
              >
                {copiedKey === keyName ? <CheckCircle2 className="w-4 h-4 text-emerald-500" /> : <Copy className="w-4 h-4" />}
              </Button>
            </TooltipTrigger>
            <TooltipContent side="top" align="center">
              <p>Copy to clipboard</p>
            </TooltipContent>
          </Tooltip>
        </TooltipProvider>
      </div>
    </div>
  );
}

export function SecretRevealModal({ isOpen, onClose, secrets, mode }: SecretRevealModalProps) {
  const [copiedKey, setCopiedKey] = useState<string | null>(null);

  if (!isOpen || !secrets) return null;

  const config = MODE_CONFIG[mode];
  const hasApiKey = !!secrets.api_key;
  const hasPublicKey = !!secrets.public_key;

  const copyToClipboard = async (text: string, keyName: string) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopiedKey(keyName);
      setTimeout(() => setCopiedKey(null), 2000);
    } catch (err) {
      console.error('Failed to copy text: ', err);
    }
  };

  const downloadAsJson = () => {
    const data: Record<string, string> = {};
    if (secrets.api_key) data.api_key = secrets.api_key;
    if (secrets.public_key) data.public_key = secrets.public_key;
    const dataStr = 'data:text/json;charset=utf-8,' + encodeURIComponent(JSON.stringify(data, null, 2));
    const anchor = document.createElement('a');
    anchor.setAttribute('href', dataStr);
    anchor.setAttribute('download', 'cerberus-keys.json');
    document.body.appendChild(anchor);
    anchor.click();
    anchor.remove();
  };

  const isDanger = config.icon === 'danger';

  return (
    <AlertDialog open={isOpen}>
      <AlertDialogContent className="max-w-2xl">
        <AlertDialogHeader className="flex flex-row items-center gap-4 text-left space-y-0">
          <div className={`flex items-center justify-center shrink-0 w-12 h-12 rounded-full border ${
            isDanger
              ? 'bg-red-500/10 border-red-500/20'
              : 'bg-blue-500/10 border-blue-500/20'
          }`}>
            {isDanger
              ? <AlertTriangle className="w-6 h-6 text-red-500" />
              : <Info className="w-6 h-6 text-blue-500" />
            }
          </div>
          <div>
            <AlertDialogTitle className="text-xl font-bold">{config.title}</AlertDialogTitle>
            <AlertDialogDescription className={`mt-1 ${
              isDanger
                ? 'text-red-600/80 dark:text-red-400/80'
                : 'text-slate-500 dark:text-slate-400'
            }`}>
              {hasApiKey
                ? 'Your API key is shown below. Copy it now — it cannot be retrieved again after you close this dialog.'
                : 'Your new JWT public key is shown below. You can always retrieve the public key from your project dashboard.'}
            </AlertDialogDescription>
          </div>
        </AlertDialogHeader>

        <div className="space-y-5 py-4">
          {hasApiKey && (
            <SecretField
              label="API Key"
              value={secrets.api_key!}
              keyName="api"
              recoverable={false}
              copiedKey={copiedKey}
              onCopy={copyToClipboard}
            />
          )}
          {hasPublicKey && (
            <SecretField
              label="JWT Public Key (RSA)"
              value={secrets.public_key!}
              keyName="public"
              recoverable={true}
              copiedKey={copiedKey}
              onCopy={copyToClipboard}
            />
          )}
        </div>

        <AlertDialogFooter className="sm:justify-between w-full border-t border-border pt-4 mt-2">
          <Button variant="outline" onClick={downloadAsJson} className="flex items-center">
            <Download className="w-4 h-4 mr-2" />
            Download JSON
          </Button>
          <AlertDialogAction onClick={onClose}>
            I have saved {hasApiKey ? 'my API key' : 'the keys'} securely
          </AlertDialogAction>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  );
}
