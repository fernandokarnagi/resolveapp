import { useQuery } from '@tanstack/react-query'
import api from '../../api/axios'
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
  PieChart, Pie, Cell
} from 'recharts'
import LoadingSpinner from '../../components/LoadingSpinner'

const PIE_COLORS = ['#3b82f6', '#f59e0b', '#10b981', '#6b7280', '#ef4444', '#8b5cf6']

export default function Analytics() {
  const { data: stats, isLoading: statsLoading } = useQuery({
    queryKey: ['dashboard'],
    queryFn: () => api.get('/api/analytics/dashboard').then(r => r.data),
  })
  const { data: casesByStatus = [] } = useQuery({
    queryKey: ['cases-by-status'],
    queryFn: () => api.get('/api/analytics/cases-by-status').then(r => r.data),
  })
  const { data: costsByMonth = [] } = useQuery({
    queryKey: ['costs-by-month'],
    queryFn: () => api.get('/api/analytics/costs-by-month').then(r => r.data),
  })
  const { data: maintenanceStats } = useQuery({
    queryKey: ['maintenance-stats'],
    queryFn: () => api.get('/api/analytics/maintenance-stats').then(r => r.data),
  })
  const { data: attendanceSummary = [] } = useQuery({
    queryKey: ['attendance-summary'],
    queryFn: () => api.get('/api/analytics/attendance-summary').then(r => r.data),
  })

  if (statsLoading) return <LoadingSpinner />

  const cleanerAttendance = attendanceSummary.filter(a => a.type === 'cleaner')
  const securityAttendance = attendanceSummary.filter(a => a.type === 'security')

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-800">Analytics</h1>
        <p className="text-slate-500 text-sm">System-wide performance metrics</p>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {[
          { label: 'Occupancy Rate', value: `${stats?.occupancy_rate ?? 0}%`, color: 'bg-green-500' },
          { label: 'Open Cases', value: stats?.open_cases, color: 'bg-orange-500' },
          { label: 'Open Corrective Maintenance', value: stats?.open_corrective_maintenance, color: 'bg-red-500' },
          { label: 'Monthly Cost', value: `SGD ${(stats?.monthly_cost || 0).toLocaleString()}`, color: 'bg-purple-500' },
        ].map(kpi => (
          <div key={kpi.label} className="bg-white rounded-xl p-4 shadow-sm border border-slate-200">
            <p className="text-sm text-slate-500">{kpi.label}</p>
            <p className={`text-2xl font-bold mt-1 ${kpi.color.replace('bg-', 'text-')}`}>{kpi.value ?? '—'}</p>
          </div>
        ))}
      </div>

      {/* Charts row 1 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Monthly Costs */}
        <div className="bg-white rounded-xl p-5 shadow-sm border border-slate-200">
          <h2 className="font-semibold text-slate-800 mb-4">Monthly Costs by Category</h2>
          <ResponsiveContainer width="100%" height={260}>
            <BarChart data={costsByMonth}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
              <XAxis dataKey="month" tick={{ fontSize: 12 }} />
              <YAxis tick={{ fontSize: 12 }} />
              <Tooltip />
              <Legend />
              {['maintenance', 'cleaning', 'utilities', 'security', 'others'].map((cat, i) => (
                <Bar key={cat} dataKey={cat} stackId="a" fill={PIE_COLORS[i]} />
              ))}
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Cases by Status */}
        <div className="bg-white rounded-xl p-5 shadow-sm border border-slate-200">
          <h2 className="font-semibold text-slate-800 mb-4">Cases by Status</h2>
          {casesByStatus.length > 0 ? (
            <ResponsiveContainer width="100%" height={260}>
              <PieChart>
                <Pie data={casesByStatus} dataKey="count" nameKey="status" cx="50%" cy="50%" outerRadius={90} label={({ status, count }) => `${status}: ${count}`}>
                  {casesByStatus.map((_, i) => <Cell key={i} fill={PIE_COLORS[i % PIE_COLORS.length]} />)}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          ) : (
            <div className="h-64 flex items-center justify-center text-slate-400">No case data</div>
          )}
        </div>
      </div>

      {/* Charts row 2 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Maintenance Stats */}
        <div className="bg-white rounded-xl p-5 shadow-sm border border-slate-200">
          <h2 className="font-semibold text-slate-800 mb-4">Maintenance Overview</h2>
          <div className="space-y-4">
            <div>
              <p className="text-sm font-medium text-slate-600 mb-2">Preventive Maintenance</p>
              <div className="flex flex-wrap gap-2">
                {(maintenanceStats?.preventive || []).map(item => (
                  <div key={item.status} className="bg-slate-50 rounded-lg px-3 py-2 text-center">
                    <p className="text-lg font-bold text-slate-800">{item.count}</p>
                    <p className="text-xs text-slate-500 capitalize">{item.status?.replace('_', ' ')}</p>
                  </div>
                ))}
              </div>
            </div>
            <div>
              <p className="text-sm font-medium text-slate-600 mb-2">Corrective Maintenance</p>
              <div className="flex flex-wrap gap-2">
                {(maintenanceStats?.corrective || []).map(item => (
                  <div key={item.status} className="bg-slate-50 rounded-lg px-3 py-2 text-center">
                    <p className="text-lg font-bold text-slate-800">{item.count}</p>
                    <p className="text-xs text-slate-500 capitalize">{item.status?.replace('_', ' ')}</p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* Attendance Summary */}
        <div className="bg-white rounded-xl p-5 shadow-sm border border-slate-200">
          <h2 className="font-semibold text-slate-800 mb-4">Attendance Summary (This Month)</h2>
          <div className="space-y-4">
            {[
              { label: 'Cleaners', items: cleanerAttendance },
              { label: 'Security Officers', items: securityAttendance },
            ].map(({ label, items }) => (
              <div key={label}>
                <p className="text-sm font-medium text-slate-600 mb-2">{label}</p>
                <div className="flex flex-wrap gap-2">
                  {items.length > 0 ? items.map(item => (
                    <div key={item.status} className="bg-slate-50 rounded-lg px-3 py-2 text-center">
                      <p className="text-lg font-bold text-slate-800">{item.count}</p>
                      <p className="text-xs text-slate-500 capitalize">{item.status}</p>
                    </div>
                  )) : (
                    <p className="text-sm text-slate-400">No data</p>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
