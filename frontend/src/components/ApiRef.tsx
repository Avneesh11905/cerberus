import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '#/components/ui/table'

export function ApiRef({
  name,
  desc,
  args,
  ret,
}: {
  name: string
  desc: string
  args: { name: string; type: string; desc: string; defaultValue?: string }[]
  ret: string
}) {
  return (
    <div className="my-6 not-prose border border-slate-200 dark:border-slate-800 rounded-xl p-5 bg-slate-50 dark:bg-[#1c1c1c]">
      <h4 className="font-mono text-lg font-semibold text-blue-600 dark:text-blue-400 mb-2">
        {name}
      </h4>
      <p className="text-base text-slate-600 dark:text-slate-400 mb-4">
        {desc}
      </p>
      {args.length > 0 && (
        <div className="mb-4 border border-slate-200 dark:border-slate-800 rounded-md overflow-hidden bg-white dark:bg-black/20">
          <Table>
            <TableHeader>
              <TableRow className="border-b border-slate-200 dark:border-slate-800 hover:bg-transparent">
                <TableHead className="font-semibold text-slate-900 dark:text-slate-100">
                  Argument
                </TableHead>
                <TableHead className="font-semibold text-slate-900 dark:text-slate-100">
                  Type
                </TableHead>
                <TableHead className="font-semibold text-slate-900 dark:text-slate-100">
                  Default
                </TableHead>
                <TableHead className="font-semibold text-slate-900 dark:text-slate-100">
                  Description
                </TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {args.map((a, i) => (
                <TableRow
                  key={i}
                  className="border-b border-slate-100 dark:border-slate-800/50 hover:bg-slate-50/50 dark:hover:bg-slate-800/20"
                >
                  <TableCell className="align-top">
                    <code className="text-blue-600 dark:text-blue-400 bg-blue-50 dark:bg-blue-500/10 px-1.5 py-0.5 rounded text-sm">
                      {a.name}
                    </code>
                  </TableCell>
                  <TableCell className="align-top text-slate-500 font-mono text-sm">
                    {a.type}
                  </TableCell>
                  <TableCell className="align-top text-slate-500 font-mono text-sm">
                    {a.defaultValue ? (
                      <code className="bg-slate-100 dark:bg-slate-800 px-1.5 py-0.5 rounded text-slate-700 dark:text-slate-300">
                        {a.defaultValue}
                      </code>
                    ) : (
                      '-'
                    )}
                  </TableCell>
                  <TableCell className="align-top text-slate-600 dark:text-slate-400">
                    {a.desc}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      )}
      <div className="text-base flex items-center gap-2">
        <span className="font-medium text-slate-900 dark:text-slate-100">
          Returns:
        </span>
        <code className="font-mono text-sm bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 px-1.5 py-0.5 rounded">
          {ret}
        </code>
      </div>
    </div>
  )
}
