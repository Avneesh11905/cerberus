import { createFileRoute } from '@tanstack/react-router'
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

import { format } from 'date-fns'
import { Calendar as CalendarIcon, RefreshCcw, Copy } from 'lucide-react'
import type { DateRange } from 'react-day-picker'
import {
  ContextMenu,
  ContextMenuContent,
  ContextMenuItem,
  ContextMenuTrigger,
} from '../components/ui/context-menu'
import { Popover, PopoverContent, PopoverTrigger } from '../components/ui/popover'
import { Calendar } from '../components/ui/calendar'
import { toast } from 'sonner'

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
  const [page, setPage] = useState(1)
  const [levelFilter, setLevelFilter] = useState<string>('ALL')
  const [dateRange, setDateRange] = useState<DateRange | undefined>(undefined)

  const { data, isLoading } = useQuery({
    queryKey: ['superadmin-logs', page, levelFilter, dateRange?.from, dateRange?.to],
    queryFn: () => {
      let fromStr = undefined
      let toStr = undefined
      
      if (dateRange?.from) {
        fromStr = dateRange.from.toISOString()
        const toDate = dateRange.to ? new Date(dateRange.to) : new Date(dateRange.from)
        toDate.setHours(23, 59, 59, 999)
        toStr = toDate.toISOString()
      }

      return getSystemLogs(
        page, 
        100, 
        levelFilter === 'ALL' ? undefined : levelFilter,
        fromStr,
        toStr
      )
    },
    refetchInterval: 15000, // refresh logs every 15s
  })

  return (
    <ContextMenu>
      <ContextMenuTrigger asChild>
        <div className="space-y-6 pt-4 w-full h-full min-h-[calc(100vh-100px)] px-4 sm:px-6 lg:px-8">
          <div className="max-w-7xl mx-auto w-full">
            <div className="flex flex-col md:flex-row justify-between items-start md:items-end gap-4 mb-6">
              <div>
          <h2 className="text-xl font-bold text-slate">System Logs</h2>
          <p className="text-sm font-semibold text-slate/60 mt-1">
            Real-time audit and error logs for the platform.
          </p>
        </div>

        <div className="flex flex-col sm:flex-row w-full md:w-auto gap-4">
          <Popover>
            <PopoverTrigger asChild>
              <Button
                variant="outline"
                className={`w-full sm:w-65 justify-start text-left bg-vanilla hover:bg-sand focus:ring-ochre ${!dateRange ? 'text-slate/60' : ''}`}
              >
                <CalendarIcon className="mr-2 h-4 w-4" />
                {dateRange?.from ? (
                  dateRange.to ? (
                    <>
                      {format(dateRange.from, 'LLL dd, y')} -{' '}
                      {format(dateRange.to, 'LLL dd, y')}
                    </>
                  ) : (
                    format(dateRange.from, 'LLL dd, y')
                  )
                ) : (
                  <span>Pick a date range</span>
                )}
              </Button>
            </PopoverTrigger>
            <PopoverContent className="w-auto p-0 border-2 border-slate shadow-[8px_8px_0px_var(--slate)] rounded-xl flex flex-col md:flex-row" align="end">
              <div className="flex flex-col gap-2 p-3 border-b-2 md:border-b-0 md:border-r-2 border-slate/10 bg-vanilla/50">
                <Button 
                  variant="ghost" 
                  className="justify-start text-sm"
                  onClick={() => {
                    const to = new Date()
                    const from = new Date()
                    from.setHours(0, 0, 0, 0)
                    setDateRange({ from, to })
                    setPage(1)
                  }}
                >
                  Today
                </Button>
                <Button 
                  variant="ghost" 
                  className="justify-start text-sm"
                  onClick={() => {
                    const to = new Date()
                    const from = new Date()
                    from.setDate(to.getDate() - 7)
                    from.setHours(0, 0, 0, 0)
                    setDateRange({ from, to })
                    setPage(1)
                  }}
                >
                  Last 7 Days
                </Button>
                <Button 
                  variant="ghost" 
                  className="justify-start text-sm"
                  onClick={() => {
                    const to = new Date()
                    const from = new Date()
                    from.setDate(to.getDate() - 30)
                    from.setHours(0, 0, 0, 0)
                    setDateRange({ from, to })
                    setPage(1)
                  }}
                >
                  Last 30 Days
                </Button>
                <Button 
                  variant="ghost" 
                  className="justify-start text-sm text-terracotta hover:text-terracotta hover:bg-terracotta/10 mt-auto"
                  onClick={() => {
                    setDateRange(undefined)
                    setPage(1)
                  }}
                >
                  Clear
                </Button>
              </div>
              {/* @ts-ignore - Shadcn Calendar type inference for range mode */}
              <Calendar
                mode="range"
                defaultMonth={dateRange?.from}
                selected={dateRange}
                onSelect={(range: DateRange | undefined) => {
                  setDateRange(range)
                  setPage(1)
                }}
                numberOfMonths={1}
                showOutsideDays={false}
              />
            </PopoverContent>
          </Popover>

          <div className="w-full sm:w-48">
            <Select
              value={levelFilter}
              onValueChange={(val) => {
                setLevelFilter(val)
                setPage(1)
              }}
            >
              <SelectTrigger className="bg-vanilla text-slate border-2 border-slate rounded-xl shadow-[4px_4px_0px_var(--slate)] transition-all hover:-translate-y-1 hover:shadow-[6px_6px_0px_var(--slate)] active:translate-y-0.5 active:translate-x-0.5 active:shadow-none focus:ring-ochre focus:outline-none">
                <SelectValue placeholder="Filter by level" />
              </SelectTrigger>
              <SelectContent className="border-2 border-slate rounded-xl shadow-[4px_4px_0px_var(--slate)]">
                <SelectItem value="ALL">All Levels</SelectItem>
                <SelectItem value="INFO">INFO</SelectItem>
                <SelectItem value="WARN">WARN</SelectItem>
                <SelectItem value="ERROR">ERROR</SelectItem>
                <SelectItem value="DEBUG">DEBUG</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>
      </div>

      <div className="bg-vanilla border-2 border-taupe/30 rounded-xl overflow-hidden shadow-sm mt-6">
            <Table>
              <TableHeader className="bg-sand/30">
            <TableRow className="border-taupe/30 hover:bg-transparent">
              <TableHead className="font-bold text-slate w-45">
                Timestamp
              </TableHead>
              <TableHead className="font-bold text-slate w-25">
                Level
              </TableHead>
              <TableHead className="font-bold text-slate w-62.5">
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
                <ContextMenu key={log.id}>
                  <ContextMenuTrigger asChild>
                    <TableRow
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
                    className="text-slate/70 text-xs whitespace-pre-wrap wrap-break-word align-top pt-4 py-4"
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
                      </ContextMenuTrigger>
                      <ContextMenuContent className="w-56 bg-vanilla border-2 border-slate rounded-xl shadow-[4px_4px_0px_rgba(96,114,116,1)] p-1 z-60">
                        <ContextMenuItem
                          className="font-bold cursor-pointer rounded-lg px-3 py-2 hover:bg-sand focus:bg-sand"
                          onClick={() => {
                            navigator.clipboard.writeText(log.id)
                            toast.success('Log ID copied to clipboard')
                          }}
                        >
                          <Copy className="w-4 h-4 mr-2" /> Copy Log ID
                        </ContextMenuItem>
                      </ContextMenuContent>
                    </ContextMenu>
                  ))
                )}
              </TableBody>
            </Table>
          </div>

          {data && data.total > data.size && (
            <div className="flex justify-between items-center bg-vanilla border-2 border-taupe/30 p-3 rounded-xl shadow-sm mt-6">
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
        </div>
      </ContextMenuTrigger>
      <ContextMenuContent className="w-56 bg-vanilla border-2 border-slate rounded-xl shadow-[4px_4px_0px_rgba(96,114,116,1)] p-1 z-60">
        <ContextMenuItem
          className="font-bold cursor-pointer rounded-lg px-3 py-2 hover:bg-sand focus:bg-sand"
          onClick={() => setPage(1)}
        >
          <RefreshCcw className="w-4 h-4 mr-2" /> Refresh Logs
        </ContextMenuItem>
      </ContextMenuContent>
    </ContextMenu>
  )
}
