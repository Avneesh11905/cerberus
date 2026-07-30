import { createFileRoute, redirect } from '@tanstack/react-router'

export const Route = createFileRoute('/_protected/projects/$projectId/')({
  beforeLoad: ({ params }) => {
    throw redirect({
      to: '/projects/$projectId/analytics',
      params: { projectId: params.projectId }
    })
  },
})
