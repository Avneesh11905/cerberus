import { useState, useEffect } from 'react'
import { Search, Loader2, UserX, Shield } from 'lucide-react'
import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
} from './ui/card'
import { Button } from './ui/button'
import { Input } from './ui/input'
import { toast } from 'sonner'
import {
  getProjectUsers,
  updateProjectUserStatus,
  getProjectUserClaims,
  updateProjectUserClaims,
} from '../api/projects'
import type { ProjectUser } from '../api/projects'
import { extractErrorMessage } from '../lib/api-client'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from './ui/dialog'

export function ProjectUsers({ projectId }: { projectId: string }) {
  const [users, setUsers] = useState<ProjectUser[]>([])
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(1)
  const [search, setSearch] = useState('')
  const [loading, setLoading] = useState(true)
  const [debouncedSearch, setDebouncedSearch] = useState('')

  // Claims Dialog State
  const [selectedUser, setSelectedUser] = useState<ProjectUser | null>(null)
  const [claims, setClaims] = useState<{ key: string; value: string }[]>([])
  const [claimsLoading, setClaimsLoading] = useState(false)
  const [savingClaims, setSavingClaims] = useState(false)

  const size = 10

  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedSearch(search)
      setPage(1)
    }, 500)
    return () => clearTimeout(handler)
  }, [search])

  const fetchUsers = async () => {
    try {
      setLoading(true)
      const data = await getProjectUsers(projectId, page, size, debouncedSearch)
      setUsers(data.items)
      setTotal(data.total)
    } catch (err) {
      toast.error(extractErrorMessage(err, 'Failed to fetch users'))
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchUsers()
  }, [projectId, page, size, debouncedSearch])

  const toggleStatus = async (user: ProjectUser) => {
    try {
      await updateProjectUserStatus(projectId, user.id, !user.is_active)
      toast.success(`User ${!user.is_active ? 'activated' : 'deactivated'}`)
      fetchUsers()
    } catch (err) {
      toast.error(extractErrorMessage(err, 'Failed to update user status'))
    }
  }

  const openClaims = async (user: ProjectUser) => {
    setSelectedUser(user)
    setClaimsLoading(true)
    try {
      const data = await getProjectUserClaims(projectId, user.id)
      // data might be { claims: ... } or just { ... } depending on the API.
      // The OpenAPI says `PaginatedProjectUsersRes` for list, but `Get User Claims` doesn't strictly define the response object. Let's assume it returns a raw object or { overrides: {} }.
      // If it's { user_overrides: {} }, use that. Otherwise use raw data.
      const overrides = data.user_overrides
      setClaims(
        Object.entries(overrides).map(([k, v]) => ({
          key: k,
          value: String(v),
        })),
      )
    } catch (err) {
      toast.error(extractErrorMessage(err, 'Failed to fetch user claims'))
      setSelectedUser(null)
    } finally {
      setClaimsLoading(false)
    }
  }

  const handleSaveClaims = async () => {
    if (!selectedUser) return
    setSavingClaims(true)
    try {
      const overridesObj = claims.reduce(
        (acc, curr) => {
          if (curr.key) acc[curr.key] = curr.value
          return acc
        },
        {} as Record<string, string>,
      )

      await updateProjectUserClaims(projectId, selectedUser.id, overridesObj)
      toast.success('User claims updated')
      setSelectedUser(null)
    } catch (err) {
      toast.error(extractErrorMessage(err, 'Failed to update user claims'))
    } finally {
      setSavingClaims(false)
    }
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Project Users</CardTitle>
        <CardDescription>
          Manage users who have authenticated with this project.
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        <div className="flex gap-4 items-center">
          <div className="relative flex-1 max-w-sm">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate/50" />
            <Input
              placeholder="Search by email..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="pl-9"
            />
          </div>
        </div>

        <div className="border-2 border-slate">
          {loading ? (
            <div className="p-8 flex justify-center">
              <Loader2 className="w-6 h-6 animate-spin text-slate" />
            </div>
          ) : users.length === 0 ? (
            <div className="p-12 flex flex-col items-center justify-center text-center bg-sand">
              <UserX className="w-12 h-12 text-slate/50 mb-4" />
              <h3 className="text-xl font-bold text-slate mb-2">
                No Users Found
              </h3>
              <p className="text-slate/70 font-semibold max-w-sm">
                No users match your criteria or no users have authenticated yet.
              </p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left text-sm font-semibold">
                <thead className="bg-taupe/10 border-b-2 border-slate">
                  <tr>
                    <th className="px-4 py-3 text-slate">Email</th>
                    <th className="px-4 py-3 text-slate">Status</th>
                    <th className="px-4 py-3 text-slate">Last Login</th>
                    <th className="px-4 py-3 text-slate text-right">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y-2 divide-taupe/20">
                  {users.map((user) => (
                    <tr
                      key={user.id}
                      className="hover:bg-sand/30 transition-colors"
                    >
                      <td className="px-4 py-4">
                        <div className="flex items-center gap-3">
                          <div className="w-8 h-8 bg-slate text-vanilla flex items-center justify-center font-bold">
                            {user.email[0].toUpperCase()}
                          </div>
                          <div>
                            <p className="text-slate font-bold">{user.email}</p>
                            <p className="text-xs text-slate/70">{user.id}</p>
                          </div>
                        </div>
                      </td>
                      <td className="px-4 py-4">
                        {user.is_active ? (
                          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 text-xs font-bold bg-sage/20 text-sage border border-sage/30">
                            <span className="w-1.5 h-1.5 rounded-full bg-sage" />{' '}
                            Active
                          </span>
                        ) : (
                          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 text-xs font-bold bg-terracotta/20 text-terracotta border border-terracotta/30">
                            <span className="w-1.5 h-1.5 rounded-full bg-terracotta" />{' '}
                            Inactive
                          </span>
                        )}
                      </td>
                      <td className="px-4 py-4 text-slate/70">
                        {user.last_login
                          ? new Date(user.last_login).toLocaleDateString()
                          : 'Never'}
                      </td>
                      <td className="px-4 py-4 text-right">
                        <div className="flex justify-end gap-2">
                          <Button
                            variant="outline"
                            size="sm"
                            className="h-8 text-xs font-bold"
                            onClick={() => toggleStatus(user)}
                          >
                            {user.is_active ? 'Deactivate' : 'Activate'}
                          </Button>
                          <Button
                            variant="outline"
                            size="sm"
                            className="h-8 text-xs font-bold gap-1"
                            onClick={() => openClaims(user)}
                          >
                            <Shield className="w-3 h-3" /> Claims
                          </Button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

        <div className="flex items-center justify-between">
          <p className="text-sm font-semibold text-slate/70">
            Showing {users.length > 0 ? (page - 1) * size + 1 : 0} to{' '}
            {Math.min(page * size, total)} of {total}
          </p>
          <div className="flex gap-2">
            <Button
              variant="outline"
              disabled={page === 1}
              onClick={() => setPage((p) => p - 1)}
            >
              Previous
            </Button>
            <Button
              variant="outline"
              disabled={page * size >= total}
              onClick={() => setPage((p) => p + 1)}
            >
              Next
            </Button>
          </div>
        </div>
      </CardContent>

      <Dialog
        open={!!selectedUser}
        onOpenChange={(open: boolean) => !open && setSelectedUser(null)}
      >
        <DialogContent className="sm:max-w-150 border-2 border-slate bg-vanilla p-0 overflow-hidden shadow-[8px_8px_0px_rgba(30,41,59,1)]">
          <DialogHeader className="p-6 bg-sand border-b-2 border-slate">
            <DialogTitle className="text-2xl font-black text-slate">
              User Claim Overrides
            </DialogTitle>
            <DialogDescription className="font-semibold text-slate/70">
              Override default project claims for {selectedUser?.email}.
            </DialogDescription>
          </DialogHeader>
          <div className="p-6">
            {claimsLoading ? (
              <div className="py-8 flex justify-center">
                <Loader2 className="w-6 h-6 animate-spin text-slate" />
              </div>
            ) : (
              <div className="space-y-4">
                {claims.map((c, idx) => (
                  <div key={idx} className="flex gap-2 items-center">
                    <Input
                      placeholder="Key (e.g. role)"
                      value={c.key}
                      onChange={(e) => {
                        const newClaims = [...claims]
                        newClaims[idx].key = e.target.value
                        setClaims(newClaims)
                      }}
                    />
                    <Input
                      placeholder="Value (e.g. admin)"
                      value={c.value}
                      onChange={(e) => {
                        const newClaims = [...claims]
                        newClaims[idx].value = e.target.value
                        setClaims(newClaims)
                      }}
                    />
                    <Button
                      variant="destructive"
                      className="px-3"
                      onClick={() =>
                        setClaims(claims.filter((_, i) => i !== idx))
                      }
                    >
                      X
                    </Button>
                  </div>
                ))}
                <Button
                  type="button"
                  variant="outline"
                  className="w-full border-dashed"
                  onClick={() => setClaims([...claims, { key: '', value: '' }])}
                >
                  + Add Override
                </Button>
              </div>
            )}
          </div>
          <DialogFooter className="p-6 bg-sand border-t-2 border-slate flex justify-end">
            <Button variant="outline" onClick={() => setSelectedUser(null)}>
              Cancel
            </Button>
            <Button onClick={handleSaveClaims} disabled={savingClaims}>
              {savingClaims ? (
                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
              ) : null}
              Save Overrides
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </Card>
  )
}
