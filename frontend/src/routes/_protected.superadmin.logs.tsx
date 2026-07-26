import { createFileRoute, useRouter } from '@tanstack/react-router'
import { useState } from 'react'

import { useQuery } from '@tanstack/react-query'
import { getSystemLogs } from '../api/superadmin'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '../components/ui/table'
import { Button } from '../components/ui/button'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '../components/ui/select'
import { Skeleton } from '../components/ui/skeleton'

export const Route = createFileRoute('/_protected/superadmin/logs')({
  component: SuperadminLogsPage,
})

function getLevelBadge(level: string) {
  const base =
    'inline-flex items-center px-2 py-0.5 rounded text-xs font-bold uppercase '
  switch (level.toUpperCase()) {
    case 'ERROR':
    case 'FATAL':
      return base + 'bg-terracotta text-vanilla'
    case 'WARNING':
    case 'WARN':
      return base + 'bg-ochre text-slate'
    case 'INFO':
      return base + 'bg-slate text-vanilla'
    case 'DEBUG':
    default:
      return base + 'bg-taupe text-slate'
  }
}

function SuperadminLogsPage() {
  const router = useRouter()
  const [page, setPage] = useState(1)
  const [levelFilter, setLevelFilter] = useState<string>('ALL')

  const { data, isLoading } = useQuery({
    queryKey: ['superadmin-logs', page, levelFilter],
    queryFn: () =>
      getSystemLogs(page, 100, levelFilter === 'ALL' ? undefined : levelFilter),
    keepPreviousData: true,
    refetchInterval: 15000, // refresh logs every 15s
  })

  return (
    <div className="space-y-6 pt-4">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-end gap-4 mb-6">
        <div>
          <h2 className="text-xl font-bold text-slate">System Logs</h2>
          <p className="text-sm font-semibold text-slate/60 mt-1">
            Real-time audit and error logs for the platform.
          </p>
        </div>

        <div className="w-full sm:w-48">
          <Select
            value={levelFilter}
            onValueChange={(val) => {
              setLevelFilter(val)
              setPage(1)
            }}
          >
            <SelectTrigger className="bg-vanilla border-taupe/50 focus:ring-ochre">
              <SelectValue placeholder="Filter by level" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="ALL">All Levels</SelectItem>
              <SelectItem value="INFO">INFO</SelectItem>
              <SelectItem value="WARN">WARN</SelectItem>
              <SelectItem value="ERROR">ERROR</SelectItem>
              <SelectItem value="DEBUG">DEBUG</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>

      <div className="bg-vanilla border-2 border-taupe/30 rounded-xl overflow-hidden shadow-sm">
        <Table>
          <TableHeader className="bg-sand/30">
            <TableRow className="border-taupe/30 hover:bg-transparent">
              <TableHead className="font-bold text-slate w-[180px]">
                Timestamp
              </TableHead>
              <TableHead className="font-bold text-slate w-[100px]">
                Level
              </TableHead>
              <TableHead className="font-bold text-slate w-[250px]">
                Source
              </TableHead>
              <TableHead className="font-bold text-slate">Message</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody className="font-mono text-sm">
            {isLoading ? (
              Array.from({ length: 15 }).map((_, i) => (
                <TableRow
                  key={i}
                  className="border-taupe/20 hover:bg-transparent"
                >
                  <TableCell>
                    <Skeleton className="h-4 w-32 bg-taupe/20" />
                  </TableCell>
                  <TableCell>
                    <Skeleton className="h-5 w-16 bg-taupe/20 rounded" />
                  </TableCell>
                  <TableCell>
                    <Skeleton className="h-4 w-40 bg-taupe/20" />
                  </TableCell>
                  <TableCell>
                    <Skeleton className="h-4 w-64 bg-taupe/20" />
                  </TableCell>
                </TableRow>
              ))
            ) : data?.items.length === 0 ? (
              <TableRow className="hover:bg-transparent font-sans">
                <TableCell
                  colSpan={4}
                  className="h-32 text-center text-slate/60 font-semibold"
                >
                  No logs found.
                </TableCell>
              </TableRow>
            ) : (
              data?.items.map((log) => (
                <TableRow
                  key={log.id}
                  className="border-taupe/20 hover:bg-sand/30 transition-colors"
                >
                  <TableCell className="text-slate/70 whitespace-nowrap align-top pt-4">
                    {new Date(log.created_at).toLocaleString()}
                  </TableCell>
                  <TableCell className="align-top pt-4">
                    <span className={getLevelBadge(log.level)}>
                      {log.level}
                    </span>
                  </TableCell>
                  <TableCell
                    className="text-slate font-medium align-top pt-4 break-all"
                    title={log.source}
                  >
                    {log.source}
                  </TableCell>
                  <TableCell
                    className="text-slate/70 text-xs whitespace-pre-wrap break-words align-top pt-4 py-4"
                    title="Log Message"
                  >
                    {log.file && (
                      <div className="font-mono text-slate/50 mb-1.5 flex items-center gap-1.5 bg-taupe/10 w-fit px-2 py-0.5 rounded-md border border-taupe/20">
                        <svg
                          xmlns="http://www.w3.org/2000/svg"
                          width="12"
                          height="12"
                          viewBox="0 0 24 24"
                          fill="none"
                          stroke="currentColor"
                          strokeWidth="2"
                          strokeLinecap="round"
                          strokeLinejoin="round"
                        >
                          <path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z" />
                          <polyline points="14 2 14 8 20 8" />
                        </svg>
                        <span>
                          {log.file}:{log.line || '?'}
                        </span>
                      </div>
                    )}
                    {log.message}
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </div>

      {data && data.total > data.size && (
        <div className="flex justify-between items-center bg-vanilla border-2 border-taupe/30 p-3 rounded-xl shadow-sm">
          <p className="text-sm font-semibold text-slate/70 ml-2">
            Showing {(page - 1) * data.size + 1} to{' '}
            {Math.min(page * data.size, data.total)} of {data.total}
          </p>
          <div className="flex gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => setPage((p) => Math.max(1, p - 1))}
              disabled={page === 1}
              className="border-taupe/50 bg-vanilla text-slate hover:bg-sand font-sans"
            >
              Previous
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => setPage((p) => p + 1)}
              disabled={page * data.size >= data.total}
              className="border-taupe/50 bg-vanilla text-slate hover:bg-sand font-sans"
            >
              Next
            </Button>
          </div>
        </div>
      )}
    </div>
  )
}
