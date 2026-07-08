import { useState, useEffect } from 'react'
import { Save, Pencil } from 'lucide-react'
import { useAuth } from '#/lib/auth'
import { Button } from '#/components/ui/button'
import { Input } from '#/components/ui/input'
import { Label } from '#/components/ui/label'
import { Avatar, AvatarImage, AvatarFallback } from '#/components/ui/avatar'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '#/components/ui/dialog'

interface ProfileDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export function ProfileDialog({ open, onOpenChange }: ProfileDialogProps) {
  const { user, updateProfile } = useAuth()
  const [name, setName] = useState('')
  const [picture, setPicture] = useState('')
  const [isSaving, setIsSaving] = useState(false)
  const [isEditingPicture, setIsEditingPicture] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (user && open) {
      setName(user.name || '')
      setPicture(user.picture || '')
      setIsEditingPicture(false) // reset state on open
    }
  }, [user, open])

  const handleSaveProfile = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)

    if (picture && !picture.startsWith('http')) {
      setError('Profile picture must be a valid URL starting with http/https.')
      return
    }

    setIsSaving(true)
    try {
      await updateProfile({ name, picture })
      onOpenChange(false)
    } catch (err: any) {
      console.error("Failed to update profile", err)
      setError(err?.response?.data?.detail || 'Failed to update profile.')
    } finally {
      setIsSaving(false)
    }
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-106.25">
        <DialogHeader>
          <DialogTitle>Edit Profile</DialogTitle>
          <DialogDescription>
            Update your public profile details.
          </DialogDescription>
        </DialogHeader>
        <form onSubmit={handleSaveProfile} className="space-y-6 py-4" noValidate>
          
          <div className="flex flex-col items-center gap-4 mb-2">
            <div className="relative group">
              <Avatar className="w-24 h-24 border-2 border-border shadow-sm">
                <AvatarImage src={picture || user?.picture || ''} alt={name || user?.name || ''} />
                <AvatarFallback className="text-2xl bg-primary/10 text-primary">
                  {(name || user?.name || 'U').charAt(0).toUpperCase()}
                </AvatarFallback>
              </Avatar>
              <Button 
                size="icon"
                variant="outline"
                type="button" 
                onClick={() => setIsEditingPicture(!isEditingPicture)}
                className="absolute bottom-0 right-0 w-8 h-8 bg-black text-white dark:bg-white dark:text-black rounded-full shadow-sm hover:opacity-90 hover:bg-black dark:hover:bg-white transition-opacity cursor-pointer border-2 border-background"
                title="Edit Profile Picture"
              >
                <Pencil className="w-4 h-4" />
              </Button>
            </div>
            
            {isEditingPicture && (
              <div className="w-full space-y-2 animate-in fade-in slide-in-from-top-2 duration-200">
                <Label>Profile Picture URL</Label>
                <Input
                  type="url"
                  placeholder="https://example.com/avatar.png"
                  value={picture}
                  onChange={(e) => setPicture(e.target.value)}
                  autoFocus
                />
              </div>
            )}
          </div>

          <div className="space-y-4">
            <div className="space-y-2">
              <Label>Display Name</Label>
              <Input
                type="text"
                placeholder="e.g. John Doe"
                value={name}
                onChange={(e) => setName(e.target.value)}
              />
            </div>
            
            <div className="space-y-2">
              <Label>Email Address</Label>
              <Input type="text" disabled value={user?.email || ''} className="bg-muted text-muted-foreground" />
              <p className="text-xs text-muted-foreground">Your email cannot be changed for security reasons.</p>
            </div>
          </div>

          {error && (
            <p className="text-sm text-destructive font-medium">{error}</p>
          )}

          <div className="flex justify-end pt-2">
            <Button type="submit" disabled={isSaving}>
              <Save className="w-4 h-4 mr-2" />
              {isSaving ? 'Saving...' : 'Save Changes'}
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  )
}
