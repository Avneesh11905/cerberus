import { createFileRoute } from '@tanstack/react-router'
import { useState, useEffect } from 'react'
import axios from 'axios'
import { motion, AnimatePresence } from 'framer-motion'
import * as z from 'zod'
import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
  CardFooter,
} from '../components/ui/card'
import { Button } from '../components/ui/button'
import { Label } from '../components/ui/label'
import { RefreshCw, Check, Save, AlertTriangle } from 'lucide-react'
import { toast } from 'sonner'
import { extractErrorMessage } from '../lib/api-client'
import { useProject } from '../contexts/ProjectContext'
import { updateProjectClaims } from '../api/projects'
import EditorModule from 'react-simple-code-editor'
const Editor = (EditorModule as any).default || EditorModule
import Prism from 'prismjs'
import 'prismjs/themes/prism.css'

export const Route = createFileRoute(
  '/_protected/projects/$projectId/claims',
)({
  component: ClaimsTab,
})

function ClaimsTab() {
  const { projectId } = Route.useParams()
  const { project, fetchProject } = useProject()

  const [claimsJson, setClaimsJson] = useState('{\n  \n}')
  const [claimsError, setClaimsError] = useState('')
  const [savingClaims, setSavingClaims] = useState(false)
  const [claimsSaved, setClaimsSaved] = useState(false)

  useEffect(() => {
    if (project) {
      setClaimsJson(
        JSON.stringify(project.default_claims || {}, null, 2),
      )
    }
  }, [project])

  const handleFormatJson = () => {
    try {
      if (!claimsJson.trim()) return
      const parsed = JSON.parse(claimsJson)
      setClaimsJson(JSON.stringify(parsed, null, 2))
      setClaimsError('')
    } catch (e) {
      setClaimsError('Invalid JSON: Cannot format')
    }
  }

  const handleEditorKeyDown = (e: any) => {
    const target = e.target as HTMLTextAreaElement
    const { selectionStart, selectionEnd, value } = target

    const pairs: Record<string, string> = {
      '"': '"',
      "'": "'",
      '{': '}',
      '[': ']',
      '(': ')',
    }

    if (pairs[e.key]) {
      e.preventDefault()
      const closing = pairs[e.key]
      const newValue =
        value.substring(0, selectionStart) +
        e.key +
        closing +
        value.substring(selectionEnd)

      setClaimsJson(newValue)

      requestAnimationFrame(() => {
        target.selectionStart = target.selectionEnd = selectionStart + 1
      })
    } else if (
      e.key === 'Backspace' &&
      selectionStart === selectionEnd &&
      selectionStart > 0
    ) {
      const prevChar = value[selectionStart - 1]
      const nextChar = value[selectionStart]
      if (pairs[prevChar] === nextChar) {
        e.preventDefault()
        const newValue =
          value.substring(0, selectionStart - 1) +
          value.substring(selectionEnd + 1)
        setClaimsJson(newValue)
        requestAnimationFrame(() => {
          target.selectionStart = target.selectionEnd = selectionStart - 1
        })
      }
    }
  }

  const handleSaveClaims = async (e: React.FormEvent) => {
    e.preventDefault()
    setSavingClaims(true)
    setClaimsError('')
    try {
      const claimsObj = JSON.parse(claimsJson)

      if (
        typeof claimsObj !== 'object' ||
        Array.isArray(claimsObj) ||
        claimsObj === null
      ) {
        setClaimsError('Claims must be a JSON object')
        setSavingClaims(false)
        return
      }

      const claimsSchema = z
        .record(z.string(), z.any())
        .refine(
          (obj) => Object.keys(obj).length <= 10,
          'Maximum 10 custom claims allowed.',
        )
        .refine((obj) => {
          const reserved = [
            'sub',
            'email',
            'exp',
            'iat',
            'jti',
            'project_id',
            'is_verified',
            'family_id',
          ]
          return !Object.keys(obj).some((k) => reserved.includes(k))
        }, 'Cannot use reserved claims.')

      const result = claimsSchema.safeParse(claimsObj)
      if (!result.success) {
        setClaimsError(result.error.issues[0].message)
        setSavingClaims(false)
        return
      }

      await updateProjectClaims(projectId, claimsObj)
      setClaimsSaved(true)
      setTimeout(() => setClaimsSaved(false), 2000)
      fetchProject(false)
    } catch (error: unknown) {
      if (error instanceof SyntaxError) {
        setClaimsError('Invalid JSON format')
      } else if (
        axios.isAxiosError(error) &&
        error.response?.status === 422 &&
        error.response?.data?.detail?.[0]?.msg
      ) {
        setClaimsError(error.response.data.detail[0].msg)
      } else {
        toast.error(extractErrorMessage(error, 'Failed to update claims'))
      }
    } finally {
      setSavingClaims(false)
    }
  }

  return (
    <div className="flex flex-col gap-6 w-full animate-in fade-in slide-in-from-bottom-2 duration-300">
      <form onSubmit={handleSaveClaims}>
        <Card>
          <CardHeader>
            <CardTitle>Custom Default Claims Mapping</CardTitle>
            <CardDescription>
              Map custom default user metadata into the JWT payloads issued by
              Cerberus.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="bg-terracotta/10 border-2 border-terracotta p-4 rounded-xl">
              <div className="text-sm font-semibold text-terracotta flex items-start gap-2">
                <AlertTriangle className="w-5 h-5 shrink-0" />
                <div>
                  <strong>Reserved Claims:</strong> You cannot map the following
                  reserved claims:
                  <br />
                  <div className="flex flex-wrap gap-1 mt-2">
                    {[
                      'sub',
                      'email',
                      'exp',
                      'iat',
                      'jti',
                      'project_id',
                      'is_verified',
                      'family_id',
                    ].map((claim) => (
                      <code
                        key={claim}
                        className="bg-terracotta/20 px-1.5 py-0.5 rounded text-xs font-mono"
                      >
                        {claim}
                      </code>
                    ))}
                  </div>
                  <span className="text-xs mt-3 block font-bold">
                    Maximum 10 custom claims allowed.
                  </span>
                </div>
              </div>
            </div>
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <Label htmlFor="claimsJson">Claims (JSON)</Label>
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  onClick={handleFormatJson}
                  className="h-8 text-xs"
                >
                  Format JSON
                </Button>
              </div>
              <div
                className={`w-full font-mono text-sm border-2 rounded-xl bg-vanilla focus-within:ring-2 overflow-hidden transition-colors ${claimsError ? 'border-terracotta focus-within:ring-terracotta' : 'border-taupe focus-within:ring-slate'}`}
              >
                <Editor
                  value={claimsJson}
                  onValueChange={(val: string) => {
                    setClaimsJson(val)
                    setClaimsError('')
                  }}
                  onKeyDown={handleEditorKeyDown}
                  highlight={(code: string) =>
                    Prism.highlight(
                      code,
                      Prism.languages.javascript || Prism.languages.js,
                      'javascript',
                    )
                  }
                  padding={16}
                  style={{
                    fontFamily:
                      'ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace',
                    fontSize: 14,
                    minHeight: '200px',
                  }}
                  textareaId="claimsJson"
                  className="w-full focus-visible:outline-none"
                />
              </div>
              {claimsError && (
                <p className="text-sm font-bold text-terracotta">
                  {claimsError}
                </p>
              )}
            </div>
          </CardContent>
          <CardFooter className="flex justify-end border-t-2 border-taupe/20 pt-6">
            <Button
              type="submit"
              disabled={savingClaims || claimsSaved}
              className={`relative overflow-hidden w-35 transition-all duration-300 ${claimsSaved ? 'bg-sage! text-vanilla! border-sage!' : ''}`}
            >
              <AnimatePresence mode="wait">
                {savingClaims ? (
                  <motion.div
                    key="saving"
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -10 }}
                    className="flex items-center justify-center gap-2 absolute inset-0"
                  >
                    <RefreshCw className="w-4 h-4 animate-spin" />
                    Saving...
                  </motion.div>
                ) : claimsSaved ? (
                  <motion.div
                    key="saved"
                    initial={{ opacity: 0, scale: 0.5 }}
                    animate={{ opacity: 1, scale: 1 }}
                    exit={{ opacity: 0, scale: 0.8 }}
                    className="flex items-center justify-center gap-2 absolute inset-0"
                  >
                    <Check className="w-4 h-4" />
                    Saved!
                  </motion.div>
                ) : (
                  <motion.div
                    key="default"
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -10 }}
                    className="flex items-center justify-center gap-2 absolute inset-0"
                  >
                    <Save className="w-4 h-4" />
                    Save Claims
                  </motion.div>
                )}
              </AnimatePresence>
              <div className="invisible flex items-center gap-2">
                <Save className="w-4 h-4" />
                Save Claims
              </div>
              {claimsSaved && (
                <motion.div
                  initial={{ scale: 0, opacity: 0.4 }}
                  animate={{ scale: 3, opacity: 0 }}
                  transition={{ duration: 0.6, ease: 'easeOut' }}
                  className="absolute inset-0 bg-vanilla rounded-full origin-center pointer-events-none"
                />
              )}
            </Button>
          </CardFooter>
        </Card>
      </form>
    </div>
  )
}
