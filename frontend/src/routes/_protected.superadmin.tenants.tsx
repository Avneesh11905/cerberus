import { createFileRoute, useRouter } from '@tanstack/react-router'
import { useState } from 'react'
import {
  useQuery,
  useMutation,
  useQueryClient,
  keepPreviousData,
} from '@tanstack/react-query'
import {
  getTenants,
  updateTenantStatus,
  updateTenantRole,
} from '../api/superadmin'
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
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '../components/ui/dropdown-menu'
import {
  ContextMenu,
  ContextMenuContent,
  ContextMenuItem,
  ContextMenuTrigger,
  ContextMenuSeparator,
} from '../components/ui/context-menu'
import {
  MoreHorizontal,
  Search,
  Shield,
  ShieldOff,
  UserX,
  UserCheck,
  BarChart,
  Copy,
  RefreshCcw,
} from 'lucide-react'
import { Input } from '../components/ui/input'
import { toast } from 'sonner'
import { extractErrorMessage } from '../lib/api-client'
import { Skeleton } from '../components/ui/skeleton'

export const Route = createFileRoute('/_protected/superadmin/tenants')({
  component: SuperadminTenantsPage,
})

function SuperadminTenantsPage() {
  const [page, setPage] = useState(1)
  const [search, setSearch] = useState('')
  const [searchInput, setSearchInput] = useState('')
  const router = useRouter()

  const queryClient = useQueryClient()

  const { data, isLoading } = useQuery({
    queryKey: ['superadmin-tenants', page, search],
    queryFn: () => getTenants(page, 50, search || undefined),
    placeholderData: keepPreviousData,
  })

  const statusMutation = useMutation({
    mutationFn: ({ id, isActive }: { id: string; isActive: boolean }) =>
      updateTenantStatus(id, isActive),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['superadmin-tenants'] })
      toast.success('Tenant status updated')
    },
    onError: (err) => {
      toast.error('Failed to update status: ' + extractErrorMessage(err))
    },
  })

  const roleMutation = useMutation({
    mutationFn: ({ id, role }: { id: string; role: string }) =>
      updateTenantRole(id, role),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['superadmin-tenants'] })
      toast.success('Tenant role updated')
    },
    onError: (err) => {
      toast.error('Failed to update role: ' + extractErrorMessage(err))
    },
  })

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault()
    setPage(1)
    setSearch(searchInput)
  }

  return (
    <ContextMenu>
      <ContextMenuTrigger asChild>
        <div className="space-y-6 pt-4 w-full h-full min-h-[calc(100vh-100px)] px-4 sm:px-6 lg:px-8">
          <div className="max-w-7xl mx-auto w-full">
            <div className="flex flex-col sm:flex-row justify-between items-start sm:items-end gap-4 mb-6">
              <div>
                <h2 className="text-xl font-bold text-slate">
                  Tenant Management
                </h2>
                <p className="text-sm font-semibold text-slate/60 mt-1">
                  Manage global access and roles for all users.
                </p>
              </div>

              <form onSubmit={handleSearch} className="relative w-full sm:w-72">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-taupe" />
                <Input
                  value={searchInput}
                  onChange={(e) => setSearchInput(e.target.value)}
                  placeholder="Search email or ID..."
                  className="pl-9 bg-vanilla border-taupe/50 focus-visible:ring-ochre"
                />
              </form>
            </div>

            <div className="bg-vanilla border-2 border-taupe/30 rounded-xl overflow-hidden shadow-sm mt-6">
              <Table>
                <TableHeader className="bg-sand/30">
                  <TableRow className="border-taupe/30 hover:bg-transparent">
                    <TableHead className="font-bold text-slate w-62.5">
                      Tenant
                    </TableHead>
                    <TableHead className="font-bold text-slate">Role</TableHead>
                    <TableHead className="font-bold text-slate">
                      Status
                    </TableHead>
                    <TableHead className="font-bold text-slate hidden md:table-cell">
                      Joined
                    </TableHead>
                    <TableHead className="text-right font-bold text-slate w-25">
                      Actions
                    </TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {isLoading ? (
                    Array.from({ length: 5 }).map((_, i) => (
                      <TableRow
                        key={i}
                        className="border-taupe/20 hover:bg-transparent"
                      >
                        <TableCell>
                          <Skeleton className="h-5 w-40 bg-taupe/20" />
                        </TableCell>
                        <TableCell>
                          <Skeleton className="h-5 w-20 bg-taupe/20" />
                        </TableCell>
                        <TableCell>
                          <Skeleton className="h-5 w-16 bg-taupe/20" />
                        </TableCell>
                        <TableCell className="hidden md:table-cell">
                          <Skeleton className="h-5 w-24 bg-taupe/20" />
                        </TableCell>
                        <TableCell className="text-right">
                          <Skeleton className="h-8 w-8 ml-auto bg-taupe/20" />
                        </TableCell>
                      </TableRow>
                    ))
                  ) : !data?.items || data.items.length === 0 ? (
                    <TableRow className="hover:bg-transparent">
                      <TableCell
                        colSpan={5}
                        className="h-32 text-center text-slate/60 font-semibold"
                      >
                        No tenants found.
                      </TableCell>
                    </TableRow>
                  ) : (
                    data.items.map((tenant) => (
                      <ContextMenu key={tenant.id}>
                        <ContextMenuTrigger asChild>
                          <TableRow className="border-taupe/20 hover:bg-sand/30 transition-colors">
                            <TableCell>
                              <div className="font-semibold text-slate truncate">
                                {tenant.name || 'Unnamed User'}
                              </div>
                              {tenant.email && (
                                <div className="text-xs text-slate/70 mt-0.5 truncate font-semibold">
                                  {tenant.email}
                                </div>
                              )}
                              <div className="text-xs text-slate/50 font-mono mt-0.5">
                                {tenant.id}
                              </div>
                            </TableCell>
                            <TableCell>
                              <span
                                className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-bold uppercase ${
                                  tenant.role === 'SUPERADMIN'
                                    ? 'bg-ochre/20 text-ochre'
                                    : 'bg-taupe/20 text-slate/80'
                                }`}
                              >
                                {tenant.role}
                              </span>
                            </TableCell>
                            <TableCell>
                              <span
                                className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-bold uppercase ${
                                  tenant.is_active
                                    ? 'bg-sage/20 text-sage'
                                    : 'bg-terracotta/20 text-terracotta'
                                }`}
                              >
                                {tenant.is_active ? 'Active' : 'Disabled'}
                              </span>
                            </TableCell>
                            <TableCell className="hidden md:table-cell text-sm font-medium text-slate/70">
                              {tenant.created_at
                                ? new Date(
                                    tenant.created_at,
                                  ).toLocaleDateString()
                                : 'Unknown'}
                            </TableCell>
                            <TableCell className="text-right">
                              <DropdownMenu>
                                <DropdownMenuTrigger asChild>
                                  <Button
                                    variant="ghost"
                                    className="h-8 w-8 p-0 text-slate/70 hover:text-slate hover:bg-taupe/20"
                                  >
                                    <span className="sr-only">Open menu</span>
                                    <MoreHorizontal className="h-4 w-4" />
                                  </Button>
                                </DropdownMenuTrigger>
                                <DropdownMenuContent
                                  align="end"
                                  className="w-48"
                                >
                                  <DropdownMenuLabel>
                                    Manage Tenant
                                  </DropdownMenuLabel>
                                  <DropdownMenuSeparator />

                                  <DropdownMenuItem
                                    onClick={() =>
                                      router.navigate({
                                        to: '/superadmin/tenants/$tenantId/analytics',
                                        params: { tenantId: tenant.id },
                                      })
                                    }
                                    className="cursor-pointer"
                                  >
                                    <BarChart className="mr-2 h-4 w-4 text-slate" />{' '}
                                    View Analytics
                                  </DropdownMenuItem>

                                  <DropdownMenuItem
                                    onClick={() =>
                                      statusMutation.mutate({
                                        id: tenant.id,
                                        isActive: !tenant.is_active,
                                      })
                                    }
                                    disabled={statusMutation.isPending}
                                  >
                                    {tenant.is_active ? (
                                      <>
                                        <UserX className="mr-2 h-4 w-4 text-terracotta" />{' '}
                                        Disable Account
                                      </>
                                    ) : (
                                      <>
                                        <UserCheck className="mr-2 h-4 w-4 text-sage" />{' '}
                                        Enable Account
                                      </>
                                    )}
                                  </DropdownMenuItem>

                                  <DropdownMenuItem
                                    onClick={() =>
                                      roleMutation.mutate({
                                        id: tenant.id,
                                        role:
                                          tenant.role === 'SUPERADMIN'
                                            ? 'TENANT'
                                            : 'SUPERADMIN',
                                      })
                                    }
                                    disabled={roleMutation.isPending}
                                  >
                                    {tenant.role === 'SUPERADMIN' ? (
                                      <>
                                        <ShieldOff className="mr-2 h-4 w-4 text-slate" />{' '}
                                        Demote to Tenant
                                      </>
                                    ) : (
                                      <>
                                        <Shield className="mr-2 h-4 w-4 text-ochre" />{' '}
                                        Promote to Admin
                                      </>
                                    )}
                                  </DropdownMenuItem>
                                </DropdownMenuContent>
                              </DropdownMenu>
                            </TableCell>
                          </TableRow>
                        </ContextMenuTrigger>
                        <ContextMenuContent className="w-56 bg-vanilla border-2 border-slate rounded-xl shadow-[4px_4px_0px_rgba(96,114,116,1)] p-1 z-60">
                          <ContextMenuItem
                            className="font-bold cursor-pointer rounded-lg px-3 py-2 hover:bg-sand focus:bg-sand"
                            onClick={() => {
                              navigator.clipboard.writeText(tenant.id)
                              toast.success('Tenant ID copied to clipboard')
                            }}
                          >
                            <Copy className="w-4 h-4 mr-2" /> Copy Tenant ID
                          </ContextMenuItem>
                          <ContextMenuSeparator className="bg-slate/10 my-1" />
                          <ContextMenuItem
                            className="font-bold cursor-pointer rounded-lg px-3 py-2 hover:bg-sand focus:bg-sand"
                            onClick={() =>
                              router.navigate({
                                to: '/superadmin/tenants/$tenantId/analytics',
                                params: { tenantId: tenant.id },
                              })
                            }
                          >
                            <BarChart className="w-4 h-4 mr-2" /> View Analytics
                          </ContextMenuItem>
                          <ContextMenuItem
                            className="font-bold cursor-pointer rounded-lg px-3 py-2 hover:bg-sand focus:bg-sand"
                            onClick={() =>
                              statusMutation.mutate({
                                id: tenant.id,
                                isActive: !tenant.is_active,
                              })
                            }
                            disabled={statusMutation.isPending}
                          >
                            {tenant.is_active ? (
                              <>
                                <UserX className="w-4 h-4 mr-2 text-terracotta" />{' '}
                                <span className="text-terracotta">
                                  Disable Tenant
                                </span>
                              </>
                            ) : (
                              <>
                                <UserCheck className="w-4 h-4 mr-2 text-sage" />{' '}
                                <span className="text-sage">Enable Tenant</span>
                              </>
                            )}
                          </ContextMenuItem>
                          <ContextMenuItem
                            className="font-bold cursor-pointer rounded-lg px-3 py-2 hover:bg-sand focus:bg-sand"
                            onClick={() =>
                              roleMutation.mutate({
                                id: tenant.id,
                                role:
                                  tenant.role === 'SUPERADMIN'
                                    ? 'USER'
                                    : 'SUPERADMIN',
                              })
                            }
                            disabled={roleMutation.isPending}
                          >
                            {tenant.role === 'SUPERADMIN' ? (
                              <>
                                <ShieldOff className="w-4 h-4 mr-2 text-ochre" />{' '}
                                Revoke Superadmin
                              </>
                            ) : (
                              <>
                                <Shield className="w-4 h-4 mr-2 text-ochre" />{' '}
                                Promote to Superadmin
                              </>
                            )}
                          </ContextMenuItem>
                        </ContextMenuContent>
                      </ContextMenu>
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
                    className="border-taupe/50 bg-vanilla text-slate hover:bg-sand"
                  >
                    Previous
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setPage((p) => p + 1)}
                    disabled={page * data.size >= data.total}
                    className="border-taupe/50 bg-vanilla text-slate hover:bg-sand"
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
          onClick={() =>
            queryClient.invalidateQueries({ queryKey: ['superadmin-tenants'] })
          }
        >
          <RefreshCcw className="w-4 h-4 mr-2" /> Refresh Tenants
        </ContextMenuItem>
      </ContextMenuContent>
    </ContextMenu>
  )
}
