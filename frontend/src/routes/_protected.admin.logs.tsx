import { createFileRoute, redirect, Navigate } from '@tanstack/react-router'
import { useState } from 'react'
import { useAdminLogs } from '#/hooks/useAdmin'
import { DataTable } from '#/components/DataTable'
import { queryClient } from './__root'
import { useAuth, UserRole } from '#/lib/auth'
import type { User } from '#/lib/auth'
import type { ColumnDef } from '@tanstack/react-table'
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from '#/components/ui/tooltip'
import { Button } from '#/components/ui/button'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '#/components/ui/select'
import { Label } from '#/components/ui/label'
import { ChevronLeft, ChevronRight } from 'lucide-react'

export const Route = createFileRoute('/_protected/admin/logs')({
  beforeLoad: () => {
    const user = queryClient.getQueryData<User>(['me'])
    //  Must also redirect when user is undefined (cold cache) — previously a fresh
    // tab would skip this check entirely because `undefined && ...` evaluates to false.
    if (!user || user.role !== UserRole.ADMIN) {
      throw redirect({ to: '/dashboard' })
    }
  },
  component: AdminLogs,
})

const PAGE_SIZE_OPTIONS = [25, 50, 100]
const LOG_LEVELS = [
  '',
  'TRACE',
  'DEBUG',
  'INFO',
  'WARN',
  'ERROR',
  'FATAL',
] as const

function AdminLogs() {
  const { user } = useAuth()
  const [logLevel, setLogLevel] = useState<string>('')
  const [pageSize, setPageSize] = useState<number>(50)
  //  page state drives server-side offset
  const [page, setPage] = useState<number>(1)

  // Reset to page 1 when filters change
  const handleLevelChange = (lvl: string) => {
    setLogLevel(lvl)
    setPage(1)
  }
  const handlePageSizeChange = (size: string) => {
    setPageSize(Number(size))
    setPage(1)
  }

  const {
    data: logs,
    isLoading,
    isFetching,
  } = useAdminLogs(page, pageSize, logLevel, '')
  const hasMore = (logs?.length ?? 0) >= pageSize

  if (user && user.role !== UserRole.ADMIN) {
    return <Navigate to="/dashboard" />
  }

  const logColumns: ColumnDef<any>[] = [
    {
      header: 'Time',
      accessorFn: (row) => new Date(row.created_at).toLocaleString(),
    },
    {
      header: 'Level',
      accessorKey: 'level',
      cell: ({ row }) => {
        const level = row.original.level
        let colorClass = 'bg-primary/10 text-primary'
        if (level === 'FATAL')
          colorClass =
            'bg-red-600/20 text-red-700 dark:text-red-400 font-bold border border-red-500/30'
        else if (level === 'ERROR' || level === 'ERR')
          colorClass =
            'bg-destructive/10 text-destructive border border-destructive/20'
        else if (level === 'WARNING' || level === 'WARN')
          colorClass =
            'bg-amber-500/10 text-amber-600 dark:text-amber-400 border border-amber-500/20'
        else if (level === 'INFO')
          colorClass =
            'bg-blue-500/10 text-blue-600 dark:text-blue-400 border border-blue-500/20'
        else if (level === 'DEBUG')
          colorClass =
            'bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/20'
        else if (level === 'TRACE')
          colorClass =
            'bg-slate-500/10 text-slate-600 dark:text-slate-400 border border-slate-500/20'

        return (
          <span
            className={`px-2 py-1 rounded text-xs font-medium ${colorClass}`}
          >
            {level}
          </span>
        )
      },
    },
    { header: 'Source', accessorKey: 'source' },
    {
      header: 'Message',
      accessorKey: 'message',
      cell: ({ row }) => (
        <Tooltip>
          <TooltipTrigger className="cursor-default text-left max-w-50 sm:max-w-md lg:max-w-2xl truncate block">
            {row.original.message}
          </TooltipTrigger>
          <TooltipContent
            side="bottom"
            align="start"
            className="max-w-75 sm:max-w-md lg:max-w-2xl p-3 bg-slate-900 text-slate-50 dark:bg-slate-100 dark:text-slate-900 border shadow-xl z-50 rounded-lg text-sm wrap-break-word whitespace-pre-wrap"
          >
            <p className="leading-relaxed font-mono">{row.original.message}</p>
          </TooltipContent>
        </Tooltip>
      ),
    },
    {
      header: 'File',
      cell: ({ row }) =>
        row.original.file ? (
          <span className="text-muted-foreground font-mono text-xs">
            {row.original.file}:{row.original.line}
          </span>
        ) : (
          <span className="text-muted-foreground">-</span>
        ),
    },
  ]

  return (
    /* /scroll fix: h-full + overflow-y-auto ensures this container scrolls */
    <div className="w-full h-full overflow-y-auto custom-scrollbar p-4 md:p-6 lg:p-8 max-w-7xl mx-auto space-y-5">
      {/* Filters row */}
      <div className="flex flex-wrap items-center gap-3">
        {/* Level filter pills */}
        <div className="flex flex-wrap gap-2">
          {LOG_LEVELS.map((lvl) => {
            let selectedClass =
              'bg-primary text-primary-foreground hover:bg-primary/90'
            if (logLevel === lvl) {
              if (lvl === 'FATAL')
                selectedClass = 'bg-red-700 text-white hover:bg-red-800'
              else if (lvl === 'ERROR')
                selectedClass = 'bg-red-500 text-white hover:bg-red-600'
              else if (lvl === 'WARN')
                selectedClass = 'bg-amber-500 text-white hover:bg-amber-600'
              else if (lvl === 'INFO')
                selectedClass = 'bg-blue-500 text-white hover:bg-blue-600'
              else if (lvl === 'DEBUG')
                selectedClass = 'bg-emerald-500 text-white hover:bg-emerald-600'
              else if (lvl === 'TRACE')
                selectedClass = 'bg-slate-500 text-white hover:bg-slate-600'
            }

            return (
              <Button
                key={lvl || 'ALL'}
                variant={logLevel === lvl ? 'default' : 'outline'}
                size="sm"
                className={`rounded-full ${logLevel === lvl ? selectedClass : ''}`}
                onClick={() => handleLevelChange(lvl)}
              >
                {lvl || 'ALL'}
              </Button>
            )
          })}
        </div>

        {/* Page size selector */}
        <div className="flex items-center gap-3 ml-auto">
          <Label
            htmlFor="limit-select"
            className="text-sm font-medium text-slate-600 dark:text-slate-400"
          >
            Per page:
          </Label>
          <Select value={String(pageSize)} onValueChange={handlePageSizeChange}>
            <SelectTrigger id="limit-select" className="w-22.5 h-9">
              <SelectValue placeholder="Size" />
            </SelectTrigger>
            <SelectContent>
              {PAGE_SIZE_OPTIONS.map((n) => (
                <SelectItem key={n} value={String(n)}>
                  {n}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
      </div>

      {/* Table */}
      <div className="w-full overflow-x-auto border rounded-md">
        <DataTable
          data={logs || []}
          columns={logColumns}
          isLoading={isLoading}
          pageSize={pageSize}
          emptyMessage="No system logs found matching your filters."
          hidePagination
        />
      </div>

      {/* Server-side pagination controls —  */}
      <div className="flex items-center justify-between pt-1">
        <p className="text-sm text-muted-foreground">
          {isFetching && !isLoading ? (
            <span className="animate-pulse">Loading…</span>
          ) : (
            <>
              Showing{' '}
              {(logs?.length ?? 0) === 0 ? 0 : (page - 1) * pageSize + 1}–
              {(page - 1) * pageSize + (logs?.length ?? 0)} of many
            </>
          )}
        </p>
        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            className="gap-1"
            onClick={() => setPage((p) => Math.max(1, p - 1))}
            disabled={page === 1 || isFetching}
          >
            <ChevronLeft className="w-4 h-4" />
            Previous
          </Button>
          <span className="text-sm font-medium px-2 tabular-nums">
            Page {page}
          </span>
          <Button
            variant="outline"
            size="sm"
            className="gap-1"
            onClick={() => setPage((p) => p + 1)}
            disabled={!hasMore || isFetching}
          >
            Next
            <ChevronRight className="w-4 h-4" />
          </Button>
        </div>
      </div>
    </div>
  )
}
