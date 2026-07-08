import { createFileRoute, redirect, Navigate } from '@tanstack/react-router'
import { useState } from 'react'
import { useAdmin } from '#/hooks/useAdmin'
import { DataTable } from '#/components/DataTable'
import { queryClient } from './__root'
import type { User } from '#/lib/auth'
import { useAuth } from '#/lib/auth'
import { Search } from 'lucide-react'
import type { ColumnDef } from '@tanstack/react-table'
import { Button } from '#/components/ui/button'
import { Input } from '#/components/ui/input'
import { Card, CardContent, CardHeader, CardTitle } from '#/components/ui/card'

export const Route = createFileRoute('/_protected/admin/tenants')({
  beforeLoad: () => {
    const user = queryClient.getQueryData<User>(['me'])
    //  Same cold-cache fix as admin.logs — redirect when user is undefined too.
    if (!user || user.role !== 'admin') {
      throw redirect({ to: '/dashboard' })
    }
  },
  component: AdminTenants,
})

function AdminTenants() {
  const { user } = useAuth()
  const [searchTerm, setSearchTerm] = useState('')
  const { tenants, isLoadingTenants, updateTenantStatus } = useAdmin()

  if (user && user.role !== 'admin') {
    return <Navigate to="/dashboard" />
  }

  const handleToggleStatus = async (tenantId: string, currentStatus: boolean) => {
    await updateTenantStatus.mutateAsync({ tenantId, is_active: !currentStatus })
  }

  const filteredTenants = tenants.filter(t => 
    t.name?.toLowerCase().includes(searchTerm.toLowerCase()) || 
    t.email.toLowerCase().includes(searchTerm.toLowerCase())
  )

  const tenantColumns: ColumnDef<any>[] = [
    {
      header: 'Tenant',
      cell: ({ row }) => {
        const tenant = row.original
        return (
          <div className="flex items-center gap-3">
            <div className="flex flex-col">
              <span className="font-medium leading-none">{tenant.name}</span>
            </div>
          </div>
        )
      }
    },
    { header: 'Email', accessorKey: 'email' },
    { 
      header: 'Status', 
      accessorKey: 'is_active',
      cell: ({ row }) => {
        const isActive = row.original.is_active !== false
        return (
          <span className={`px-2 py-1 rounded text-xs font-medium ${isActive ? 'bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/20' : 'bg-destructive/10 text-destructive border border-destructive/20'}`}>
            {isActive ? 'Active' : 'Disabled'}
          </span>
        )
      }
    },
    {
      header: 'Actions',
      id: 'actions',
      cell: ({ row }) => {
        const tenant = row.original
        const isActive = tenant.is_active !== false
        return (
          <Button
            variant={isActive ? 'destructive' : 'outline'}
            size="sm"
            onClick={() => handleToggleStatus(tenant.id, isActive)}
            className="w-24"
          >
            {isActive ? 'Disable' : 'Enable'}
          </Button>
        )
      }
    }
  ]

  return (
    <div className="w-full h-full overflow-y-auto custom-scrollbar p-4 md:p-6 lg:p-8 max-w-7xl mx-auto space-y-6">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold tracking-tight">Tenants</h2>
          <p className="text-muted-foreground">Manage all organizations registered on Cerberus.</p>
        </div>
      </div>

      <Card className="w-full">
        <CardHeader className="pb-3 border-b">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <CardTitle>Tenant Directory</CardTitle>
            <div className="relative w-full sm:w-96">
              <div className="absolute inset-y-0 left-0 flex items-center pl-3 pointer-events-none">
                <Search className="w-4 h-4 text-muted-foreground" />
              </div>
              <Input
                type="text"
                placeholder="Search by name or email..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-9 w-full"
              />
            </div>
          </div>
        </CardHeader>
        <CardContent className="p-0">
          <div className="w-full overflow-x-auto border-t">
            <DataTable
              data={filteredTenants}
              columns={tenantColumns}
              isLoading={isLoadingTenants}
              emptyMessage="No tenants found matching your search."
            />
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
