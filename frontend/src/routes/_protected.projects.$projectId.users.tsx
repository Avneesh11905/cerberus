import { createFileRoute } from '@tanstack/react-router'
import { ProjectUsers } from '../components/ProjectUsers'

export const Route = createFileRoute(
  '/_protected/projects/$projectId/users',
)({
  component: UsersTab,
})

function UsersTab() {
  const { projectId } = Route.useParams()

  return (
    <div className="animate-in fade-in slide-in-from-bottom-2 duration-300 w-full">
      <ProjectUsers projectId={projectId} />
    </div>
  )
}
