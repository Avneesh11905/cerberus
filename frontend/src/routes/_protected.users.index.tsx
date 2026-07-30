import { createFileRoute, useRouter } from '@tanstack/react-router'
import { useState, useEffect } from 'react'
import { getTenantUsers, updateTenantUserStatus } from '../api/projects'
import type { ProjectUser } from '../api/projects'
import { extractErrorMessage } from '../lib/api-client'
import { toast } from 'sonner'
import { Button } from '../components/ui/button'
import { Input } from '../components/ui/input'
import { Checkbox } from '../components/ui/checkbox'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '../components/ui/table'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuTrigger,
} from '../components/ui/dropdown-menu'
import { Avatar, AvatarFallback } from '../components/ui/avatar'
import { MoreHorizontal, ShieldOff, Search, Loader2, ArrowLeft } from 'lucide-react'

export const Route = createFileRoute('/_protected/users/')({
  component: GlobalUsersDashboard,
})

function GlobalUsersDashboard() {
  const router = useRouter()
  const [users, setUsers] = useState<ProjectUser[]>([])
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(true)
  const [page, setPage] = useState(1)
  const [search, setSearch] = useState('')

  const size = 50

  useEffect(() => {
    const handler = setTimeout(() => {
      fetchUsers()
    }, 500)
    return () => clearTimeout(handler)
  }, [page, search])

  const fetchUsers = async () => {
    try {
      setLoading(true)
      const data = await getTenantUsers(page, size, search)
      setUsers(data.items)
      setTotal(data.total)
    } catch (err) {
      toast.error(extractErrorMessage(err, 'Failed to fetch global users'))
    } finally {
      setLoading(false)
    }
  }

  const handleToggleStatus = async (email: string, currentStatus: boolean) => {
    try {
      await updateTenantUserStatus(email, !currentStatus)
      toast.success(
        `User ${!currentStatus ? 'activated' : 'deactivated'} across all projects`,
      )
      fetchUsers()
    } catch (err) {
      toast.error(extractErrorMessage(err, 'Failed to update user status'))
    }
  }

  const totalPages = Math.ceil(total / size)

  return (
    <div className="max-w-7xl mx-auto flex flex-col gap-8 w-full">
      <div className="flex items-center gap-4 mb-2">
        <Button 
          variant="outline" 
          size="icon" 
          className="border-2 border-slate w-10 h-10 rounded-xl"
          onClick={() => router.navigate({ to: '/dashboard' })}
        >
          <ArrowLeft className="w-5 h-5 text-slate" />
        </Button>
        <div>
          <h1 className="text-3xl font-display font-black tracking-tight text-slate">
            Global Users
          </h1>
          <p className="text-slate/70 font-semibold mt-1">
            Manage users across all your projects.
          </p>
        </div>
      </div>

      <div className="flex items-center space-x-2">
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate/50" />
          <Input
            placeholder="Search by name or email..."
            className="pl-9 bg-vanilla/50"
            value={search}
            onChange={(e) => {
              setSearch(e.target.value)
              setPage(1)
            }}
          />
        </div>
      </div>

      <div className="bg-vanilla rounded-xl border-2 border-slate shadow-[4px_4px_0px_rgba(30,41,59,1)] overflow-hidden">
        <Table>
          <TableHeader className="bg-sand border-b-2 border-slate">
            <TableRow className="hover:bg-transparent">
              <TableHead className="font-black text-slate uppercase tracking-wider py-4">
                User
              </TableHead>

              <TableHead className="font-black text-slate uppercase tracking-wider py-4">
                Active
              </TableHead>
              <TableHead className="font-black text-slate uppercase tracking-wider py-4 text-right">
                Actions
              </TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {loading ? (
              <TableRow>
                <TableCell colSpan={4} className="h-32 text-center">
                  <Loader2 className="w-8 h-8 animate-spin mx-auto text-slate" />
                </TableCell>
              </TableRow>
            ) : users.length === 0 ? (
              <TableRow>
                <TableCell
                  colSpan={4}
                  className="h-32 text-center text-slate/60 font-medium"
                >
                  No users found.
                </TableCell>
              </TableRow>
            ) : (
              users.map((user) => (
                <TableRow
                  key={`${user.id}-${user.email}`}
                  className="border-b-2 border-slate/10 hover:bg-vanilla/50 transition-colors"
                >
                  <TableCell>
                    <div className="flex items-center gap-3">
                      <Avatar className="w-10 h-10 border-2 border-slate">
                        <AvatarFallback className="bg-sand font-bold text-slate">
                          {(user.name?.[0] || user.email[0]).toUpperCase()}
                        </AvatarFallback>
                      </Avatar>
                      <div>
                        <div className="font-bold text-slate">
                          {user.name || 'Unknown User'}
                        </div>
                        <div className="text-sm font-medium text-slate/60">
                          {user.email}
                        </div>
                      </div>
                    </div>
                  </TableCell>

                  <TableCell>
                    <Checkbox
                      checked={user.is_active}
                      onCheckedChange={() =>
                        handleToggleStatus(user.email, user.is_active)
                      }
                      className="border-2 border-slate data-[state=checked]:bg-slate data-[state=checked]:text-white"
                    />
                  </TableCell>
                  <TableCell className="text-right">
                    <DropdownMenu>
                      <DropdownMenuTrigger asChild>
                        <Button
                          variant="ghost"
                          className="h-8 w-8 p-0 text-slate hover:bg-slate/10 hover:text-slate"
                        >
                          <span className="sr-only">Open menu</span>
                          <MoreHorizontal className="h-4 w-4" />
                        </Button>
                      </DropdownMenuTrigger>
                        <DropdownMenuContent
                          align="end"
                          className="w-48 bg-vanilla border-2 border-slate shadow-[4px_4px_0px_rgba(30,41,59,1)] rounded-xl p-1"
                        >
                          <DropdownMenuLabel className="font-bold text-slate px-2 py-1.5">
                            Actions
                          </DropdownMenuLabel>
                          <DropdownMenuItem
                            onClick={() =>
                              handleToggleStatus(user.email, user.is_active)
                            }
                            className="font-medium cursor-pointer rounded-lg px-2 py-1.5"
                          >
                          <ShieldOff className="mr-2 h-4 w-4" />
                          {user.is_active
                            ? 'Deactivate Everywhere'
                            : 'Activate Everywhere'}
                        </DropdownMenuItem>
                    </DropdownMenuContent>
                    </DropdownMenu>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>

        {!loading && totalPages > 1 && (
          <div className="p-4 border-t-2 border-slate flex items-center justify-between bg-sand">
            <div className="text-sm font-bold text-slate">
              Showing {(page - 1) * size + 1} to {Math.min(page * size, total)}{' '}
              of {total} users
            </div>
            <div className="flex gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => setPage((p) => Math.max(1, p - 1))}
                disabled={page === 1}
                className="font-bold border-2"
              >
                Previous
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                disabled={page === totalPages}
                className="font-bold border-2"
              >
                Next
              </Button>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
