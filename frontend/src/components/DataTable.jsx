import { ChevronLeft, ChevronRight, Search, ChevronUp, ChevronDown, ChevronsUpDown } from 'lucide-react'
import { useState, useMemo } from 'react'

export default function DataTable({ columns, data, loading, onSearch, searchPlaceholder = 'Search...' }) {
  const [page, setPage] = useState(0)
  const [sortKey, setSortKey] = useState(null)
  const [sortDir, setSortDir] = useState('asc')
  const pageSize = 10

  const sorted = useMemo(() => {
    if (!sortKey) return data
    return [...data].sort((a, b) => {
      const av = a[sortKey] ?? ''
      const bv = b[sortKey] ?? ''
      const cmp = String(av).localeCompare(String(bv), undefined, { numeric: true, sensitivity: 'base' })
      return sortDir === 'asc' ? cmp : -cmp
    })
  }, [data, sortKey, sortDir])

  const paginated = sorted.slice(page * pageSize, (page + 1) * pageSize)
  const totalPages = Math.ceil(sorted.length / pageSize)

  const handleSort = (col) => {
    if (col.key === 'actions' || !col.label) return
    if (sortKey === col.key) {
      setSortDir(d => d === 'asc' ? 'desc' : 'asc')
    } else {
      setSortKey(col.key)
      setSortDir('asc')
    }
    setPage(0)
  }

  return (
    <div className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
      {onSearch && (
        <div className="px-4 py-3 border-b border-slate-200">
          <div className="relative max-w-xs">
            <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
            <input
              type="text"
              placeholder={searchPlaceholder}
              onChange={(e) => { onSearch(e.target.value); setPage(0) }}
              className="pl-9 pr-3 py-2 text-sm border border-slate-200 rounded-lg w-full focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
        </div>
      )}
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="bg-slate-50 border-b border-slate-200">
              {columns.map((col) => {
                const sortable = col.key !== 'actions' && col.label
                const active = sortKey === col.key
                return (
                  <th
                    key={col.key}
                    onClick={() => sortable && handleSort(col)}
                    className={`px-4 py-3 text-left text-xs font-semibold text-slate-500 uppercase tracking-wide select-none ${sortable ? 'cursor-pointer hover:text-slate-700' : ''}`}
                  >
                    <span className="inline-flex items-center gap-1">
                      {col.label}
                      {sortable && (
                        active
                          ? sortDir === 'asc' ? <ChevronUp size={13} className="text-blue-500" /> : <ChevronDown size={13} className="text-blue-500" />
                          : <ChevronsUpDown size={13} className="text-slate-300" />
                      )}
                    </span>
                  </th>
                )
              })}
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {loading ? (
              <tr><td colSpan={columns.length} className="px-4 py-8 text-center text-slate-400">Loading...</td></tr>
            ) : paginated.length === 0 ? (
              <tr><td colSpan={columns.length} className="px-4 py-8 text-center text-slate-400">No records found</td></tr>
            ) : (
              paginated.map((row, i) => (
                <tr key={row.id || i} className="hover:bg-slate-50 transition-colors">
                  {columns.map((col) => (
                    <td key={col.key} className="px-4 py-3 text-slate-700">
                      {col.render ? col.render(row[col.key], row) : row[col.key]}
                    </td>
                  ))}
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
      {totalPages > 1 && (
        <div className="px-4 py-3 border-t border-slate-200 flex items-center justify-between">
          <span className="text-xs text-slate-500">
            Showing {page * pageSize + 1}–{Math.min((page + 1) * pageSize, data.length)} of {data.length}
          </span>
          <div className="flex gap-1">
            <button
              disabled={page === 0}
              onClick={() => setPage(p => p - 1)}
              className="p-1.5 rounded hover:bg-slate-100 disabled:opacity-40"
            >
              <ChevronLeft size={16} />
            </button>
            <button
              disabled={page >= totalPages - 1}
              onClick={() => setPage(p => p + 1)}
              className="p-1.5 rounded hover:bg-slate-100 disabled:opacity-40"
            >
              <ChevronRight size={16} />
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
